"""
Unit tests for ZMK Studio protocol module.

Tests the complete protocol stack:
- Serial client (mocked)
- Framing/unframing
- Protobuf encoding/decoding
- RPC request/response handling
"""

import pytest
import serial
from unittest.mock import Mock, MagicMock, patch
from zmk_studio.protocol.serial import SerialClient
from zmk_studio.protocol.framing import Framing, SOF, ESC, EOF_BYTE
from zmk_studio.protocol.protobuf import Protobuf
from zmk_studio.protocol.rpc import (
    RPCClient,
    META_ERRORS,
    LOCK_STATE_LOCKED,
    LOCK_STATE_UNLOCKED,
)


class TestSerialClient:
    """Test cases for SerialClient."""

    @patch("zmk_studio.protocol.serial.serial")
    @patch("zmk_studio.protocol.serial.serial.tools.list_ports.comports")
    def test_init_default_params(self, mock_list_ports, mock_serial):
        """Test initialization with default parameters."""
        client = SerialClient()

        assert client.port is None
        assert client.baudrate == 12500
        assert client.default_timeout == 1.0
        assert client.debug is False
        assert client._request_id == 0

    def test_init_with_params(self):
        """Test initialization with custom parameters."""
        client = SerialClient(port="COM8", baudrate=9600, timeout=2.0, debug=True)

        assert client.port == "COM8"
        assert client.baudrate == 9600
        assert client.default_timeout == 2.0
        assert client.debug is True

    @patch("zmk_studio.protocol.serial.serial.tools.list_ports.comports")
    def test_find_port_usb_device(self, mock_list_ports):
        """Test auto-detection of USB serial port."""
        # Mock a USB serial port
        mock_port = Mock()
        mock_port.device = "COM8"
        mock_port.description = "USB Serial Device"
        mock_list_ports.return_value = [mock_port]

        client = SerialClient()
        found_port = client.find_port()

        assert found_port == "COM8"

    @patch("zmk_studio.protocol.serial.serial.tools.list_ports.comports")
    def test_find_port_acm_device(self, mock_list_ports):
        """Test auto-detection of ACM serial port."""
        # Mock an ACM serial port (common for ZMK keyboards)
        mock_port = Mock()
        mock_port.device = "/dev/ttyACM0"
        mock_port.description = "ZMK Keyboard"
        mock_list_ports.return_value = [mock_port]

        client = SerialClient()
        found_port = client.find_port()

        assert found_port == "/dev/ttyACM0"

    @patch("zmk_studio.protocol.serial.serial.tools.list_ports.comports")
    def test_find_port_fallback(self, mock_list_ports):
        """Test fallback to first port if no USB device found."""
        # Mock a generic serial port
        mock_port = Mock()
        mock_port.device = "COM1"
        mock_port.description = "Generic Serial"
        mock_list_ports.return_value = [mock_port]

        client = SerialClient()
        found_port = client.find_port()

        assert found_port == "COM1"

    @patch("zmk_studio.protocol.serial.serial.tools.list_ports.comports")
    def test_find_port_none_available(self, mock_list_ports):
        """Test find_port when no ports available."""
        mock_list_ports.return_value = []

        client = SerialClient()
        found_port = client.find_port()

        assert found_port is None

    @patch("zmk_studio.protocol.serial.serial.Serial")
    @patch("zmk_studio.protocol.serial.serial.tools.list_ports.comports")
    def test_connect_success(self, mock_list_ports, mock_serial_class):
        """Test successful connection."""
        # Mock serial port
        mock_port = Mock()
        mock_port.device = "COM8"
        mock_port.description = "USB Serial"
        mock_list_ports.return_value = [mock_port]

        # Mock serial instance
        mock_ser = Mock()
        mock_ser.is_open = True
        mock_ser.in_waiting = 0
        mock_serial_class.return_value = mock_ser

        client = SerialClient()
        result = client.connect()

        assert result is True
        assert client.ser == mock_ser
        assert client.port == "COM8"
        mock_ser.read.assert_not_called()  # No data to flush

    @patch("zmk_studio.protocol.serial.serial.Serial")
    @patch("zmk_studio.protocol.serial.serial.tools.list_ports.comports")
    def test_connect_with_stale_data(self, mock_list_ports, mock_serial_class):
        """Test connection with stale data to flush."""
        # Mock serial port
        mock_port = Mock()
        mock_port.device = "COM8"
        mock_port.description = "USB Serial"
        mock_list_ports.return_value = [mock_port]

        # Mock serial instance with stale data
        mock_ser = Mock()
        mock_ser.is_open = True
        mock_ser.in_waiting = 10
        mock_ser.read.return_value = b"stale_data"
        mock_serial_class.return_value = mock_ser

        client = SerialClient(debug=True)
        result = client.connect()

        assert result is True
        mock_ser.read.assert_called_once_with(10)

    @patch("zmk_studio.protocol.serial.serial.tools.list_ports.comports")
    def test_connect_no_port(self, mock_list_ports):
        """Test connection when no port found."""
        mock_list_ports.return_value = []

        client = SerialClient()
        result = client.connect()

        assert result is False

    @patch("zmk_studio.protocol.serial.serial.Serial")
    @patch("zmk_studio.protocol.serial.serial.tools.list_ports.comports")
    def test_connect_exception(self, mock_list_ports, mock_serial_class):
        """Test connection with exception."""
        # Mock list_ports to return a valid port
        mock_port = Mock()
        mock_port.device = "COM8"
        mock_port.description = "USB Serial"
        mock_list_ports.return_value = [mock_port]

        # Mock Serial to raise exception on __init__
        mock_serial_class.side_effect = serial.SerialException("Port not found")

        client = SerialClient()
        result = client.connect()

        assert result is False

    @patch("zmk_studio.protocol.serial.serial.Serial")
    def test_send(self, mock_serial_class):
        """Test sending raw bytes."""
        mock_ser = Mock()
        mock_ser.is_open = True
        mock_serial_class.return_value = mock_ser

        client = SerialClient(port="COM8")
        client.ser = mock_ser
        data = b"test_data"

        client.send(data)

        mock_ser.write.assert_called_once_with(data)
        mock_ser.flush.assert_called_once()

    @patch("zmk_studio.protocol.serial.serial.Serial")
    def test_send_not_connected(self, mock_serial_class):
        """Test send when not connected raises error."""
        client = SerialClient(port="COM8")

        with pytest.raises(RuntimeError, match="Not connected"):
            client.send(b"test")

    @patch("zmk_studio.protocol.serial.serial.Serial")
    def test_send_framed(self, mock_serial_class):
        """Test sending framed data."""
        mock_ser = Mock()
        mock_ser.is_open = True
        mock_serial_class.return_value = mock_ser

        client = SerialClient(port="COM8")
        client.ser = mock_ser
        data = b"test_data"

        client.send_framed(data)

        # Should send framed data (SOF + data + EOF)
        mock_ser.write.assert_called_once()
        written_data = mock_ser.write.call_args[0][0]
        assert written_data[0] == SOF
        assert written_data[-1] == EOF_BYTE

    @patch("zmk_studio.protocol.serial.serial.Serial")
    def test_receive(self, mock_serial_class):
        """Test receiving raw bytes."""
        mock_ser = Mock()
        mock_ser.is_open = True
        mock_ser.in_waiting = 5
        mock_ser.read.return_value = b"hello"
        mock_serial_class.return_value = mock_ser

        client = SerialClient(port="COM8")
        client.ser = mock_ser

        data = client.receive()

        assert data == b"hello"

    @patch("zmk_studio.protocol.serial.serial.Serial")
    def test_receive_timeout(self, mock_serial_class):
        """Test receive timeout returns None."""
        mock_ser = Mock()
        mock_ser.is_open = True
        mock_ser.in_waiting = 0
        mock_ser.read.return_value = b""
        mock_serial_class.return_value = mock_ser

        client = SerialClient(port="COM8")
        client.ser = mock_ser

        data = client.receive()

        assert data is None

    @patch("zmk_studio.protocol.serial.serial.Serial")
    def test_receive_framed(self, mock_serial_class):
        """Test receiving framed data."""
        mock_ser = Mock()
        mock_ser.is_open = True
        # Simulate data arriving
        framed_data = Framing.frame(b"test")
        mock_ser.read.return_value = framed_data
        # First check has data
        call_count = [0]

        def in_waiting_side_effect():
            call_count[0] += 1
            return len(framed_data) if call_count[0] == 1 else 0

        type(mock_ser).in_waiting = property(lambda self: in_waiting_side_effect())
        mock_serial_class.return_value = mock_ser

        client = SerialClient(port="COM8")
        client.ser = mock_ser

        messages = client.receive_framed(timeout=0.5, chunk_timeout=0.1)

        assert messages is not None
        assert len(messages) == 1
        assert messages[0] == b"test"

    @patch("zmk_studio.protocol.serial.serial.Serial")
    def test_receive_framed_no_data(self, mock_serial_class):
        """Test receive_framed with no data."""
        mock_ser = Mock()
        mock_ser.is_open = True
        mock_ser.in_waiting = 0
        mock_serial_class.return_value = mock_ser

        client = SerialClient(port="COM8")
        client.ser = mock_ser

        messages = client.receive_framed(timeout=0.5, silence_timeout=0.1)

        assert messages is None

    @patch("zmk_studio.protocol.serial.serial.Serial")
    def test_flush(self, mock_serial_class):
        """Test flushing buffers."""
        mock_ser = Mock()
        mock_ser.is_open = True
        mock_ser.in_waiting = 10
        mock_ser.read.return_value = b"stale"
        mock_serial_class.return_value = mock_ser

        client = SerialClient(port="COM8")
        client.ser = mock_ser

        client.flush()

        mock_ser.read.assert_called_once_with(10)
        mock_ser.flush.assert_called_once()

    @patch("zmk_studio.protocol.serial.serial.Serial")
    def test_disconnect(self, mock_serial_class):
        """Test disconnecting."""
        mock_ser = Mock()
        mock_ser.is_open = True
        mock_serial_class.return_value = mock_ser

        client = SerialClient(port="COM8")
        client.ser = mock_ser

        client.disconnect()

        mock_ser.close.assert_called_once()
        assert client.ser is None

    @patch("zmk_studio.protocol.serial.serial.Serial")
    @patch("zmk_studio.protocol.serial.serial.tools.list_ports.comports")
    def test_context_manager(self, mock_list_ports, mock_serial_class):
        """Test using SerialClient as context manager."""
        # Mock serial port
        mock_port = Mock()
        mock_port.device = "COM8"
        mock_port.description = "USB Serial"
        mock_list_ports.return_value = [mock_port]

        # Mock serial instance
        mock_ser = Mock()
        mock_ser.is_open = True
        mock_ser.in_waiting = 0
        mock_serial_class.return_value = mock_ser

        with SerialClient() as client:
            assert client.ser == mock_ser

        mock_ser.close.assert_called_once()

    def test_request_id(self):
        """Test request ID incrementing."""
        client = SerialClient(port="COM8")

        assert client.request_id == 0
        assert client.next_request_id() == 1
        assert client.next_request_id() == 2
        assert client.request_id == 2


class TestRPCClient:
    """Test cases for RPCClient."""

    def test_init(self):
        """Test RPCClient initialization."""
        client = RPCClient()

        assert client.request_id == 0
        assert client.debug is False

    def test_build_request(self):
        """Test building RPC request."""
        client = RPCClient()
        subsystem_data = b"subsystem"

        req_id, request = client.build_request(subsystem_data)

        assert req_id == 1
        assert client.request_id == 1

    def test_build_request_increments_id(self):
        """Test that build_request increments request ID."""
        client = RPCClient()

        _, _ = client.build_request(b"req1")
        assert client.request_id == 1

        _, _ = client.build_request(b"req2")
        assert client.request_id == 2

    def test_encode_core_request_lock_state(self):
        """Test encoding core request for lock state."""
        client = RPCClient()
        data = client.encode_core_request(get_lock_state=True)

        assert len(data) > 0
        # Should be a length-delimited field (field 3)
        assert data[0] & 0x07 == 2  # wire type 2 = length-delimited

    def test_encode_core_request_lock(self):
        """Test encoding core request for lock."""
        client = RPCClient()
        data = client.encode_core_request(lock=True)

        assert len(data) > 0

    def test_encode_behaviors_request_list_all(self):
        """Test encoding behaviors request for list all."""
        client = RPCClient()
        data = client.encode_behaviors_request(list_all=True)

        assert len(data) > 0

    def test_encode_behaviors_request_details(self):
        """Test encoding behaviors request for details."""
        client = RPCClient()
        data = client.encode_behaviors_request(behavior_id=42)

        assert len(data) > 0

    def test_encode_keymap_request_get(self):
        """Test encoding keymap request for get."""
        client = RPCClient()
        data = client.encode_keymap_request(get_keymap=True)

        assert len(data) > 0

    def test_parse_response_no_response_field(self):
        """Test parsing response with no response field."""
        client = RPCClient()
        # Create invalid response (no field 1 or 2)
        response_data = Protobuf.encode_uint32(3, 1)

        result = client.parse_response(response_data, 1)

        assert result is None

    def test_parse_response_notification(self):
        """Test parsing response that's a notification."""
        client = RPCClient()
        # Create notification response (field 2 instead of 1)
        notification_data = Protobuf.encode_string(1, "test")
        response_data = Protobuf.encode_ld(2, notification_data)

        result = client.parse_response(response_data, 1)

        assert result is None

    def test_parse_response_meta_error(self):
        """Test parsing response with meta error."""
        client = RPCClient()
        # Create response with meta error
        # field 1: requestResponse
        #   field 2: meta.Response
        #     field 2: simpleError with error code 1 (UNLOCK_REQUIRED)
        error_inner = Protobuf.encode_uint32(2, 1)  # Error code 1 = UNLOCK_REQUIRED
        meta_resp = Protobuf.encode_ld(2, error_inner)
        rr_resp = Protobuf.encode_ld(2, meta_resp)
        response_data = Protobuf.encode_ld(1, rr_resp)

        result = client.parse_response(response_data, 1)

        assert result is not None
        assert "error" in result

    def test_parse_core_response(self):
        """Test parsing core response."""
        client = RPCClient()
        # Create core response with lock state
        # field 3: core.Response
        #   field 2: lock_state
        core_inner = Protobuf.encode_uint32(2, LOCK_STATE_UNLOCKED)
        rr_resp = Protobuf.encode_ld(3, core_inner)
        response = Protobuf.decode_message(rr_resp)

        result = client.parse_core_response(response)

        assert result is not None
        assert "lock_state" in result
        assert result["lock_state"] == LOCK_STATE_UNLOCKED

    def test_parse_core_response_no_field(self):
        """Test parsing core response when field not present."""
        client = RPCClient()
        response = {}

        result = client.parse_core_response(response)

        assert result is None

    def test_parse_behaviors_response(self):
        """Test parsing behaviors response."""
        client = RPCClient()
        # Create behaviors response
        # field 4: behaviors.Response
        beh_data = b"behaviors_data"
        rr_resp = Protobuf.encode_ld(4, beh_data)
        response = Protobuf.decode_message(rr_resp)

        result = client.parse_behaviors_response(response)

        assert result == beh_data

    def test_parse_behaviors_response_no_field(self):
        """Test parsing behaviors response when field not present."""
        client = RPCClient()
        response = {}

        result = client.parse_behaviors_response(response)

        assert result is None

    def test_parse_keymap_response(self):
        """Test parsing keymap response."""
        client = RPCClient()
        # Create keymap response
        # field 5: keymap.Response
        km_data = b"keymap_data"
        rr_resp = Protobuf.encode_ld(5, km_data)
        response = Protobuf.decode_message(rr_resp)

        result = client.parse_keymap_response(response)

        assert result == km_data

    def test_parse_keymap_response_no_field(self):
        """Test parsing keymap response when field not present."""
        client = RPCClient()
        response = {}

        result = client.parse_keymap_response(response)

        assert result is None

    def test_call_rpc_success(self):
        """Test call_rpc with successful response."""
        client = RPCClient()
        client.debug = True  # Enable debug for this test
        subsystem_data = b"subsystem"

        # Mock send and receive functions
        send_func = Mock()
        receive_func = Mock()

        # Create valid response (RequestResponse with requestId)
        # field 1: requestResponse (LD)
        #   field 1: requestId (varint) = 1
        rr_inner = Protobuf.encode_uint32(1, 1)
        response_data = Protobuf.encode_ld(1, rr_inner)
        # receive_func should return UNFRAMED messages (list of bytes)
        receive_func.return_value = [response_data]

        result = client.call_rpc(subsystem_data, send_func, receive_func)

        # Result should be the parsed RequestResponse dict
        assert result is not None
        assert 1 in result  # requestId field should be present
        send_func.assert_called_once()
        receive_func.assert_called_once()

    def test_call_rpc_no_response(self):
        """Test call_rpc when no response received."""
        client = RPCClient()
        subsystem_data = b"subsystem"

        send_func = Mock()
        receive_func = Mock(return_value=None)

        result = client.call_rpc(subsystem_data, send_func, receive_func)

        assert result is None


class TestFramingAliases:
    """Test that frame/unframe are aliases for encode/decode."""

    def test_frame_is_encode(self):
        """Test that frame is an alias for encode."""
        data = b"test_data"

        result_frame = Framing.frame(data)
        result_encode = Framing.encode(data)

        assert result_frame == result_encode

    def test_unframe_is_decode(self):
        """Test that unframe is an alias for decode."""
        data = b"test_data"
        framed = Framing.encode(data)

        result_unframe = Framing.unframe(framed)
        result_decode = Framing.decode(framed)

        assert result_unframe == result_decode


class TestProtocolIntegration:
    """Integration tests for protocol components."""

    def test_full_rpc_flow(self):
        """Test complete RPC flow: build, frame, send, receive, unframe, parse."""
        # Setup
        client = RPCClient()
        subsystem_data = client.encode_core_request(get_lock_state=True)

        # Build request
        req_id, request = client.build_request(subsystem_data)

        # Frame request
        framed_request = Framing.frame(request)

        # Create mock response (lock_state = unlocked)
        core_inner = Protobuf.encode_uint32(2, LOCK_STATE_UNLOCKED)
        rr_resp = Protobuf.encode_ld(3, core_inner)
        response_data = Protobuf.encode_ld(1, rr_resp)
        framed_response = Framing.frame(response_data)

        # Unframe and parse
        messages = Framing.unframe(framed_response)
        assert len(messages) == 1

        parsed = client.parse_response(messages[0], req_id)
        assert parsed is not None

        result = client.parse_core_response(parsed)
        assert result is not None
        assert result["lock_state"] == LOCK_STATE_UNLOCKED

    def test_zigzag_encoding_roundtrip(self):
        """Test ZigZag encoding roundtrip for signed integers."""
        test_values = [0, 1, -1, 2, -2, 100, -100, 127, -128, 32767, -32768]

        for value in test_values:
            encoded = Protobuf.encode_zigzag(value)
            # Decode varint first, then decode zigzag
            decoded_varint, _ = Protobuf.decode_varint(encoded)
            decoded = Protobuf.decode_zigzag(decoded_varint)

            assert decoded == value, f"Failed for value {value}: got {decoded}"
