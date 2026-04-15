"""
ZMK Studio RPC Protocol

Implements the RPC request/response encoding for ZMK Studio protocol.
Handles request building, response parsing, and meta error handling.

Request structure:
  field 1 (varint):  requestId
  field 3 (LD):     core.Request
  field 4 (LD):     behaviors.Request
  field 5 (LD):     keymap.Request

Response structure:
  field 1 (LD):     requestResponse
    field 1 (varint): requestId
    field 2 (LD):     meta.Response
    field 3 (LD):     core.Response
    field 4 (LD):     behaviors.Response
    field 5 (LD):     keymap.Response
  field 2 (LD):     notification

Meta error codes:
  0: GENERIC
  1: UNLOCK_REQUIRED
  2: RPC_NOT_FOUND
  3: MSG_DECODE_FAILED
  4: MSG_ENCODE_FAILED
"""

from typing import Optional, Dict, Any, List
from .protobuf import Protobuf
from .framing import Framing

# Meta error conditions
META_GENERIC = 0
META_UNLOCK_REQUIRED = 1
META_RPC_NOT_FOUND = 2
META_MSG_DECODE_FAILED = 3
META_MSG_ENCODE_FAILED = 4

META_ERRORS = {
    0: "GENERIC",
    1: "UNLOCK_REQUIRED",
    2: "RPC_NOT_FOUND",
    3: "MSG_DECODE_FAILED",
    4: "MSG_ENCODE_FAILED",
}

# Core lock states
LOCK_STATE_LOCKED = 0
LOCK_STATE_UNLOCKED = 1


class RPCClient:
    """ZMK Studio RPC client for request/response handling."""

    def __init__(self):
        self.pb = Protobuf()
        self.request_id = 0
        self.debug = False

    def build_request(self, subsystem_data: bytes) -> tuple[int, bytes]:
        """
        Build a complete RPC request with request ID and subsystem data.

        Args:
            subsystem_data: Encoded inner message for one subsystem (core, behaviors, or keymap)

        Returns:
            Tuple of (request_id, encoded_request_bytes)
        """
        self.request_id += 1
        req_id = self.request_id

        # Build the top-level Request:
        # field 1 (varint): requestId
        # field 3 (LD): core.Request
        # field 4 (LD): behaviors.Request
        # field 5 (LD): keymap.Request
        request = Protobuf.encode_uint32(1, req_id) + subsystem_data

        return req_id, request

    def call_rpc(
        self, subsystem_data: bytes, send_func: callable, receive_func: callable
    ) -> Optional[Dict[int, List[tuple[int, Any]]]]:
        """
        Execute an RPC call: build request, send, receive response, decode.

        Args:
            subsystem_data: Encoded inner message for one subsystem
            send_func: Function to send bytes (e.g., serial.send_framed)
            receive_func: Function to receive bytes (e.g., serial.receive_framed)

        Returns:
            Parsed response dict, or None if error/no response
        """
        req_id, request = self.build_request(subsystem_data)

        # Send framed request
        framed_request = Framing.frame(request)
        send_func(framed_request)

        # Receive framed response
        messages = receive_func()
        if not messages:
            if self.debug:
                print("  No response received")
            return None

        # Decode first response message
        response_data = messages[0]
        if self.debug:
            print(f"  Response [{len(response_data)}]: {response_data.hex()}")

        # Parse response
        return self.parse_response(response_data, req_id)

    def parse_response(
        self, response_data: bytes, expected_request_id: int
    ) -> Optional[Dict[int, List[tuple[int, Any]]]]:
        """
        Parse an RPC response and extract the relevant subsystem data.

        Args:
            response_data: Framed protobuf response bytes
            expected_request_id: Expected request ID for matching

        Returns:
            Parsed response dict with int field numbers as keys, or error dict if meta error occurred
        """
        # Decode top-level Response
        top = Protobuf.decode_message(response_data)

        # field 1 = requestResponse (LD)
        if 1 not in top:
            # field 2 = notification
            if 2 in top:
                if self.debug:
                    print("  Got notification instead of response")
                return None
            else:
                if self.debug:
                    print("  Unknown response format")
                return None

        # Decode RequestResponse
        rr_wire, rr_data = top[1][0]
        rr = Protobuf.decode_message(rr_data)

        # Check requestId matches
        if 1 in rr:
            resp_req_id = rr[1][0][1]  # (wire_type=0, value)
            if resp_req_id != expected_request_id:
                if self.debug:
                    print(
                        f"  WARNING: requestId mismatch: sent {expected_request_id}, got {resp_req_id}"
                    )

        # Check for meta errors
        if 2 in rr:
            meta_wire, meta_data = rr[2][0]
            meta = Protobuf.decode_message(meta_data)
            if 2 in meta:  # simpleError
                error_code = meta[2][0][1]
                error_name = META_ERRORS.get(error_code, f"UNKNOWN({error_code})")
                if self.debug:
                    print(f"  ERROR: {error_name}")
                # Return error dict with string keys for compatibility
                return {"error": error_name, "error_code": error_code}  # type: ignore
            if 1 in meta:  # noResponse
                if meta[1][0][1]:
                    if self.debug:
                        print("  No response expected for this RPC")
                    return {"noResponse": True}  # type: ignore

        return rr

    def encode_core_request(
        self, get_lock_state: bool = False, lock: bool = False
    ) -> bytes:
        """
        Encode a core.Request message.

        Args:
            get_lock_state: Request lock state
            lock: Toggle lock state (True to lock, False for other operations)

        Returns:
            Encoded core.Request as length-delimited field
        """
        core_inner = b""
        if get_lock_state:
            core_inner += Protobuf.encode_bool(2, True)
        if lock:
            core_inner += Protobuf.encode_bool(3, True)

        return Protobuf.encode_ld(3, core_inner)  # field 3 = core

    def encode_behaviors_request(
        self, list_all: bool = False, behavior_id: Optional[int] = None
    ) -> bytes:
        """
        Encode a behaviors.Request message.

        Args:
            list_all: Request list of all behaviors
            behavior_id: Request details for specific behavior ID

        Returns:
            Encoded behaviors.Request as length-delimited field
        """
        behaviors_inner = b""
        if list_all:
            behaviors_inner += Protobuf.encode_bool(1, True)
        if behavior_id is not None:
            # GetBehaviorDetailsRequest: field 1 (uint32) = behaviorId
            detail_req = Protobuf.encode_uint32(1, behavior_id)
            behaviors_inner += Protobuf.encode_ld(2, detail_req)  # getBehaviorDetails

        return Protobuf.encode_ld(4, behaviors_inner)  # field 4 = behaviors

    def encode_keymap_request(
        self,
        get_keymap: bool = False,
        check_unsaved: bool = False,
        save_changes: bool = False,
        discard_changes: bool = False,
        get_physical_layouts: bool = False,
    ) -> bytes:
        """
        Encode a keymap.Request message.

        Args:
            get_keymap: Request keymap data
            check_unsaved: Check for unsaved changes
            save_changes: Save changes
            discard_changes: Discard unsaved changes
            get_physical_layouts: Request physical layout information

        Returns:
            Encoded keymap.Request as length-delimited field
        """
        keymap_inner = b""
        if get_keymap:
            keymap_inner += Protobuf.encode_bool(1, True)
        if check_unsaved:
            keymap_inner += Protobuf.encode_bool(3, True)
        if save_changes:
            keymap_inner += Protobuf.encode_bool(4, True)
        if discard_changes:
            keymap_inner += Protobuf.encode_bool(5, True)
        if get_physical_layouts:
            keymap_inner += Protobuf.encode_bool(6, True)

        return Protobuf.encode_ld(5, keymap_inner)  # field 5 = keymap

    def parse_core_response(
        self, rr: Dict[int, List[tuple[int, Any]]]
    ) -> Optional[Dict[str, Any]]:
        """
        Parse core.Response from RequestResponse.

        Args:
            rr: RequestResponse dict from parse_response

        Returns:
            Dict with lock_state if present, or None
        """
        if 3 not in rr:
            return None

        core_wire, core_data = rr[3][0]
        core_resp = Protobuf.decode_message(core_data)
        result = {}

        if 2 in core_resp:
            result["lock_state"] = core_resp[2][0][1]

        return result if result else None

    def parse_behaviors_response(
        self, rr: Dict[int, List[tuple[int, Any]]]
    ) -> Optional[bytes]:
        """
        Parse behaviors.Response from RequestResponse.

        Args:
            rr: RequestResponse dict from parse_response

        Returns:
            Raw behaviors response bytes, or None
        """
        if 4 not in rr:
            return None

        _, beh_data = rr[4][0]
        return beh_data

    def parse_keymap_response(
        self, rr: Dict[int, List[tuple[int, Any]]]
    ) -> Optional[bytes]:
        """
        Parse keymap.Response from RequestResponse.

        Args:
            rr: RequestResponse dict from parse_response

        Returns:
            Raw keymap response bytes, or None
        """
        if 5 not in rr:
            return None

        _, km_data = rr[5][0]
        return km_data
