"""
RPC Client for ZMK Studio protocol.

Abstracts the low-level protocol communication into a simple API.
"""

import logging
from typing import Optional, Dict, Any, List
from zmk_studio.protocol import SerialClient, framing, protobuf

# Protocol constants
# Request fields
REQ_REQUEST_ID = 1
REQ_CORE = 3
REQ_BEHAVIORS = 4
REQ_KEYMAP = 5

# Core request fields
CORE_GET_LOCK_STATE = 2
CORE_LOCK = 3

# Keymap request fields
KEYMAP_GET_KEYMAP = 1
KEYMAP_GET_PHYSICAL_LAYOUTS = 6

# Behaviors request fields
BEHAVIORS_LIST_ALL = 1
BEHAVIORS_GET_DETAILS = 2

# Response fields
RESP_REQUEST_RESPONSE = 1
RESP_NOTIFICATION = 2

# RequestResponse fields
RR_REQUEST_ID = 1
RR_META = 2
RR_CORE = 3
RR_BEHAVIORS = 4
RR_KEYMAP = 5

# Meta response fields
META_NO_RESPONSE = 1
META_SIMPLE_ERROR = 2

# Core response fields
CORE_GET_LOCK_STATE_RESP = 2

# Keymap response fields
KEYMAP_GET_KEYMAP_RESP = 1
KEYMAP_GET_PHYSICAL_LAYOUTS_RESP = 6

# Behaviors response fields
BEHAVIORS_LIST_ALL_RESP = 1
BEHAVIORS_GET_DETAILS_RESP = 2

# Meta error codes
META_ERROR_GENERIC = 0
META_ERROR_UNLOCK_REQUIRED = 1
META_ERROR_RPC_NOT_FOUND = 2
META_ERROR_MSG_DECODE_FAILED = 3
META_ERROR_MSG_ENCODE_FAILED = 4

META_ERRORS = {
    0: "GENERIC",
    1: "UNLOCK_REQUIRED",
    2: "RPC_NOT_FOUND",
    3: "MSG_DECODE_FAILED",
    4: "MSG_ENCODE_FAILED",
}

# Lock states
LOCK_STATE_LOCKED = 0
LOCK_STATE_UNLOCKED = 1

logger = logging.getLogger(__name__)


class RPCError(Exception):
    """Exception raised for RPC errors."""

    def __init__(self, error_code: int, error_name: str):
        self.error_code = error_code
        self.error_name = error_name
        super().__init__(f"RPC Error: {error_name} ({error_code})")


class RPCClient:
    """
    High-level RPC client for ZMK Studio protocol.

    Provides simple methods for common operations:
    - get_lock_state()
    - unlock()
    - get_keymap()
    - get_behaviors()
    - get_behavior_details()
    - get_physical_layouts()
    """

    def __init__(
        self, port: Optional[str] = None, baudrate: int = 12500, debug: bool = False
    ):
        """
        Initialize RPC client.

        Args:
            port: Serial port path (e.g., "COM8" or "/dev/ttyACM0")
            baudrate: Baud rate (default: 12500 for ZMK Studio)
            debug: Enable debug logging
        """
        self.serial = SerialClient(port=port, baudrate=baudrate)
        self.request_id = 0
        self.debug = debug

        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

    def connect(self) -> bool:
        """
        Connect to the keyboard via serial.

        Returns:
            True if connected successfully, False otherwise
        """
        logger.info(f"Connecting to {self.serial.port or 'auto-detect port'}...")
        if self.serial.connect():
            logger.info("Connected!")
            return True
        logger.error("Failed to connect")
        return False

    def disconnect(self) -> None:
        """Disconnect from the keyboard."""
        self.serial.disconnect()
        logger.info("Disconnected")

    def get_lock_state(self) -> Optional[int]:
        """
        Get the current lock state of the keyboard.

        Returns:
            LOCK_STATE_LOCKED (0) or LOCK_STATE_UNLOCKED (1), or None on error
        """
        logger.info("Getting lock state...")

        # Core.Request: field 2 (bool) = getLockState = true
        core_inner = protobuf.encode_bool(CORE_GET_LOCK_STATE, True)
        subsystem = protobuf.encode_ld(REQ_CORE, core_inner)

        rr = self._call_rpc(subsystem)
        if rr is None:
            return None

        # core.Response: field 2 (int32) = getLockState
        if RR_CORE in rr:
            for _, core_data in rr[RR_CORE]:
                core_resp = protobuf.decode_message(core_data)
                if CORE_GET_LOCK_STATE_RESP in core_resp:
                    lock_state = core_resp[CORE_GET_LOCK_STATE_RESP][0][1]
                    state_name = (
                        "UNLOCKED" if lock_state == LOCK_STATE_UNLOCKED else "LOCKED"
                    )
                    logger.info(f"Lock state: {state_name} ({lock_state})")
                    return lock_state

        return None

    def unlock(self) -> bool:
        """
        Unlock the keyboard for keymap access.

        Returns:
            True if unlocked successfully, False otherwise
        """
        logger.info("Unlocking keyboard...")

        # Core.Request: field 3 (bool) = lock = true (toggles lock state)
        core_inner = protobuf.encode_bool(CORE_LOCK, True)
        subsystem = protobuf.encode_ld(REQ_CORE, core_inner)

        rr = self._call_rpc(subsystem)
        if rr is None:
            return False

        # Check if we got a core response
        if RR_CORE in rr:
            for _, core_data in rr[RR_CORE]:
                core_resp = protobuf.decode_message(core_data)
                if CORE_GET_LOCK_STATE_RESP in core_resp:
                    new_state = core_resp[CORE_GET_LOCK_STATE_RESP][0][1]
                    state_name = (
                        "UNLOCKED" if new_state == LOCK_STATE_UNLOCKED else "LOCKED"
                    )
                    logger.info(f"New lock state: {state_name} ({new_state})")
                    return new_state == LOCK_STATE_UNLOCKED

        return False

    def get_keymap(self) -> Optional[Dict[str, Any]]:
        """
        Get the complete keymap from the keyboard.

        Returns:
            Keymap dictionary with layers, or None on error
        """
        logger.info("Getting keymap...")

        # Keymap.Request: field 1 (bool) = getKeymap = true
        keymap_inner = protobuf.encode_bool(KEYMAP_GET_KEYMAP, True)
        subsystem = protobuf.encode_ld(REQ_KEYMAP, keymap_inner)

        rr = self._call_rpc(subsystem)
        if rr is None:
            return None

        if isinstance(rr, dict) and "error" in rr:
            logger.error(f"Cannot get keymap: {rr['error']}")
            return None

        # keymap.Response: field 1 (LD) = getKeymap -> Keymap
        if RR_KEYMAP not in rr:
            logger.error("No keymap data in response")
            return None

        _, km_data = rr[RR_KEYMAP][0]

        # keymap.Response has this structure:
        #   field 1 (LD) = getKeymap -> Keymap message
        km_resp = protobuf.decode_message(km_data)

        # Get Keymap from field 1 (getKeymap)
        if KEYMAP_GET_KEYMAP_RESP not in km_resp:
            logger.error("No getKeymap field in keymap response")
            return None

        keymap_wire, keymap_bytes = km_resp[KEYMAP_GET_KEYMAP_RESP][0]
        if not isinstance(keymap_bytes, bytes):
            logger.error(f"getKeymap data is not bytes: {type(keymap_bytes)}")
            return None

        logger.info(f"Received keymap data: {len(keymap_bytes)} bytes")

        return self._decode_keymap(keymap_bytes)

    def get_behaviors(self) -> Optional[List[int]]:
        """
        List all available behavior IDs.

        Returns:
            List of behavior IDs, or None on error
        """
        logger.info("Getting behaviors list...")

        # Behaviors.Request: field 1 (bool) = listAllBehaviors = true
        behaviors_inner = protobuf.encode_bool(BEHAVIORS_LIST_ALL, True)
        subsystem = protobuf.encode_ld(REQ_BEHAVIORS, behaviors_inner)

        rr = self._call_rpc(subsystem)
        if rr is None:
            return None

        # behaviors.Response: field 1 (LD) = listAllBehaviors -> ListAllBehaviorsResponse
        if RR_BEHAVIORS not in rr:
            logger.error("No behaviors data in response")
            return None

        _, beh_data = rr[RR_BEHAVIORS][0]
        behavior_ids = self._decode_behaviors_list(beh_data)
        return behavior_ids

    def get_behavior_details(self, behavior_id: int) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific behavior.

        Args:
            behavior_id: The behavior ID to query

        Returns:
            Behavior details dictionary, or None on error
        """
        logger.info(f"Getting details for behavior {behavior_id}...")

        # Behaviors.Request: field 2 (LD) = getBehaviorDetails
        # GetBehaviorDetailsRequest: field 1 (uint32) = behaviorId
        detail_req = protobuf.encode_uint32(1, behavior_id)
        behaviors_inner = protobuf.encode_ld(BEHAVIORS_GET_DETAILS, detail_req)
        subsystem = protobuf.encode_ld(REQ_BEHAVIORS, behaviors_inner)

        rr = self._call_rpc(subsystem)
        if rr is None:
            return None

        if RR_BEHAVIORS not in rr:
            return None

        _, beh_data = rr[RR_BEHAVIORS][0]
        return self._decode_behavior_details(beh_data)

    def get_physical_layouts(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get physical layout information.

        Returns:
            List of physical layout dictionaries, or None on error
        """
        logger.info("Getting physical layouts...")

        # Keymap.Request: field 6 (bool) = getPhysicalLayouts = true
        keymap_inner = protobuf.encode_bool(KEYMAP_GET_PHYSICAL_LAYOUTS, True)
        subsystem = protobuf.encode_ld(REQ_KEYMAP, keymap_inner)

        rr = self._call_rpc(subsystem)
        if rr is None:
            return None

        if RR_KEYMAP not in rr:
            logger.error("No physical layouts in response")
            return None

        km_wire, km_data = rr[RR_KEYMAP][0]
        km_resp = protobuf.decode_message(km_data)

        # keymap.Response: field 6 (LD) = getPhysicalLayouts -> PhysicalLayouts
        if KEYMAP_GET_PHYSICAL_LAYOUTS_RESP not in km_resp:
            logger.error("No physical layouts field in keymap response")
            return None

        pl_wire, pl_data = km_resp[KEYMAP_GET_PHYSICAL_LAYOUTS_RESP][0]
        return self._decode_physical_layouts(pl_data)

    def _call_rpc(self, subsystem_data: bytes) -> Optional[Dict[str, Any]]:
        """
        Build and send an RPC request.

        Args:
            subsystem_data: Encoded inner message for one subsystem

        Returns:
            Decoded response dict, or None on error
        """
        self.request_id += 1
        req_id = self.request_id

        # Build top-level Request:
        # field 1 (varint): requestId
        # field 3 (LD): core.Request
        # field 4 (LD): behaviors.Request
        # field 5 (LD): keymap.Request
        request = protobuf.encode_uint32(REQ_REQUEST_ID, req_id) + subsystem_data

        if self.debug:
            logger.debug(f"Sending request ID {req_id}")

        # Send framed request
        if not self.serial.send_framed(request):
            logger.error("Failed to send request")
            return None

        # Receive response
        messages = self.serial.receive_framed(timeout=8.0)
        if not messages:
            logger.error("No response received")
            return None

        # Process first response message
        # It should be a Response containing requestResponse
        response_data = messages[0]

        if self.debug:
            logger.debug(f"Response [{len(response_data)}]: {response_data.hex()}")

        # Decode top-level Response
        top = protobuf.decode_message(response_data)

        # field 1 = requestResponse (LD)
        if RESP_REQUEST_RESPONSE not in top:
            # field 2 = notification
            if RESP_NOTIFICATION in top:
                logger.debug("Got notification instead of response")
                # Try next message if available
                if len(messages) > 1:
                    response_data = messages[1]
                    top = protobuf.decode_message(response_data)
                    if RESP_REQUEST_RESPONSE not in top:
                        logger.error("No requestResponse in second message either")
                        return None
                else:
                    return None
            else:
                logger.error("Unknown response format")
                return None

        # Decode RequestResponse
        rr_wire, rr_data = top[RESP_REQUEST_RESPONSE][0]
        rr = protobuf.decode_message(rr_data)

        # Check requestId matches
        if RR_REQUEST_ID in rr:
            resp_req_id = rr[RR_REQUEST_ID][0][1]
            if resp_req_id != req_id:
                logger.warning(f"requestId mismatch: sent {req_id}, got {resp_req_id}")

        # Check for meta errors
        if RR_META in rr:
            meta_wire, meta_data = rr[RR_META][0]
            meta = protobuf.decode_message(meta_data)
            if META_SIMPLE_ERROR in meta:
                error_code = meta[META_SIMPLE_ERROR][0][1]
                error_name = META_ERRORS.get(error_code, f"UNKNOWN({error_code})")
                logger.error(f"RPC Error: {error_name}")
                return {"error": error_name, "error_code": error_code}
            if META_NO_RESPONSE in meta:
                if meta[META_NO_RESPONSE][0][1]:
                    logger.debug("No response expected for this RPC")
                    return {"noResponse": True}

        return rr

    def _decode_keymap(self, data: bytes) -> Dict[str, Any]:
        """
        Decode a Keymap protobuf message.

        Args:
            data: Encoded Keymap message bytes

        Returns:
            Keymap dictionary
        """
        km = protobuf.decode_message(data)
        result = {"layers": [], "availableLayers": 0, "maxLayerNameLength": 0}

        # Decode availableLayers and maxLayerNameLength fields
        if 2 in km:
            result["availableLayers"] = km[2][0][1]
        if 3 in km:
            result["maxLayerNameLength"] = km[3][0][1]

        # Decode repeated Layer field (field 1)
        if 1 in km:
            for _, layer_data in km[1]:
                layer = self._decode_layer(layer_data)
                result["layers"].append(layer)

        return result

    def _decode_layer(self, data: bytes) -> Dict[str, Any]:
        """
        Decode a Layer protobuf message.

        Args:
            data: Encoded Layer message bytes

        Returns:
            Layer dictionary
        """
        layer_msg = protobuf.decode_message(data)
        layer = {"id": 0, "name": "", "bindings": []}

        if 1 in layer_msg:
            layer["id"] = layer_msg[1][0][1]
        if 2 in layer_msg:
            name_data = layer_msg[2][0][1]
            if isinstance(name_data, bytes):
                layer["name"] = name_data.decode("utf-8", errors="replace")

        # Decode repeated BehaviorBinding field (field 3)
        if 3 in layer_msg:
            for _, binding_data in layer_msg[3]:
                binding = self._decode_behavior_binding(binding_data)
                layer["bindings"].append(binding)

        return layer

    def _decode_behavior_binding(self, data: bytes) -> Dict[str, Any]:
        """
        Decode a BehaviorBinding protobuf message.

        Args:
            data: Encoded BehaviorBinding message bytes

        Returns:
            Binding dictionary
        """
        binding_msg = protobuf.decode_message(data)
        binding = {"behavior_id": 0, "param1": 0, "param2": 0}

        # Field 1 (sint32): behaviorId (ZigZAG encoded)
        if 1 in binding_msg:
            zigzag_value = binding_msg[1][0][1]
            binding["behavior_id"] = protobuf.decode_zigzag(zigzag_value)

        # Field 2 (varint): param1
        if 2 in binding_msg:
            binding["param1"] = binding_msg[2][0][1]

        # Field 3 (varint): param2
        if 3 in binding_msg:
            binding["param2"] = binding_msg[3][0][1]

        return binding

    def _decode_behaviors_list(self, data: bytes) -> List[int]:
        """
        Decode a ListAllBehaviorsResponse protobuf message.

        Args:
            data: Encoded ListAllBehaviorsResponse bytes

        Returns:
            List of behavior IDs
        """
        msg = protobuf.decode_message(data)
        behaviors = []

        # Field 1 (repeated varint): behaviorIds
        if 1 in msg:
            for _, value in msg[1]:
                behaviors.append(value)

        return behaviors

    def _decode_behavior_details(self, data: bytes) -> Optional[Dict[str, Any]]:
        """
        Decode a BehaviorDetailsResponse protobuf message.

        Args:
            data: Encoded BehaviorDetailsResponse bytes

        Returns:
            Behavior details dictionary
        """
        msg = protobuf.decode_message(data)
        details = {"id": 0, "name": "", "description": ""}

        # Field 1 (uint32): id
        if 1 in msg:
            details["id"] = msg[1][0][1]

        # Field 2 (string): name
        if 2 in msg:
            name_data = msg[2][0][1]
            if isinstance(name_data, bytes):
                details["name"] = name_data.decode("utf-8", errors="replace")

        # Field 3 (string): description
        if 3 in msg:
            desc_data = msg[3][0][1]
            if isinstance(desc_data, bytes):
                details["description"] = desc_data.decode("utf-8", errors="replace")

        return details

    def _decode_physical_layouts(self, data: bytes) -> List[Dict[str, Any]]:
        """
        Decode PhysicalLayouts protobuf message.

        Args:
            data: Encoded PhysicalLayouts bytes

        Returns:
            List of physical layout dictionaries
        """
        msg = protobuf.decode_message(data)
        layouts = []

        # Field 1 (repeated LD): layouts
        if 1 in msg:
            for _, layout_data in msg[1]:
                layout = self._decode_physical_layout(layout_data)
                layouts.append(layout)

        return layouts

    def _decode_physical_layout(self, data: bytes) -> Dict[str, Any]:
        """
        Decode a PhysicalLayout protobuf message.

        Args:
            data: Encoded PhysicalLayout bytes

        Returns:
            Physical layout dictionary
        """
        msg = protobuf.decode_message(data)
        layout = {"id": 0, "name": "", "keys": []}

        # Field 1 (uint32): id
        if 1 in msg:
            layout["id"] = msg[1][0][1]

        # Field 2 (string): name
        if 2 in msg:
            name_data = msg[2][0][1]
            if isinstance(name_data, bytes):
                layout["name"] = name_data.decode("utf-8", errors="replace")

        # Field 3 (repeated LD): keys
        if 3 in msg:
            for _, key_data in msg[3]:
                key = self._decode_physical_key(key_data)
                layout["keys"].append(key)

        return layout

    def _decode_physical_key(self, data: bytes) -> Dict[str, Any]:
        """
        Decode a PhysicalKey protobuf message.

        Args:
            data: Encoded PhysicalKey bytes

        Returns:
            Physical key dictionary
        """
        msg = protobuf.decode_message(data)
        key = {"id": 0, "x": 0, "y": 0, "width": 1, "height": 1}

        # Field 1 (uint32): id
        if 1 in msg:
            key["id"] = msg[1][0][1]

        # Field 2 (float): x
        if 2 in msg:
            # Float is encoded as 4-byte little-endian
            x_bytes = msg[2][0][1]
            if isinstance(x_bytes, bytes) and len(x_bytes) >= 4:
                import struct

                key["x"] = struct.unpack("<f", x_bytes[:4])[0]

        # Field 3 (float): y
        if 3 in msg:
            y_bytes = msg[3][0][1]
            if isinstance(y_bytes, bytes) and len(y_bytes) >= 4:
                import struct

                key["y"] = struct.unpack("<f", y_bytes[:4])[0]

        return key

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


__all__ = [
    "RPCClient",
    "RPCError",
    "LOCK_STATE_LOCKED",
    "LOCK_STATE_UNLOCKED",
]
