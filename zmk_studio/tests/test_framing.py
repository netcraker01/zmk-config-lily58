"""
Unit tests for ZMK Studio framing protocol.

Tests SOF/ESC/EOF framing and unframing logic.
"""

import pytest
from zmk_studio.protocol.framing import Framing, SOF, ESC, EOF_BYTE


class TestFraming:
    """Test cases for Framing.encode and Framing.decode."""

    def test_encode_simple_message(self):
        """Test encoding a simple message without special bytes."""
        data = b"\x01\x02\x03\x04\x05"
        encoded = Framing.encode(data)

        # Should start with SOF and end with EOF
        assert encoded[0] == SOF
        assert encoded[-1] == EOF_BYTE
        # Middle should be the data
        assert encoded[1:-1] == data

    def test_encode_with_sof_byte(self):
        """Test encoding a message containing SOF byte."""
        data = b"\x01\xab\x03"  # Contains SOF (0xAB)
        encoded = Framing.encode(data)

        # SOF should be escaped
        assert encoded[0] == SOF
        assert encoded[-1] == EOF_BYTE
        # Data should have ESC before SOF
        # Original: 0x01 0xAB 0x03
        # Encoded:   SOF 0x01 ESC 0xAB 0x03 EOF
        assert encoded[1] == 0x01
        assert encoded[2] == ESC
        assert encoded[3] == SOF
        assert encoded[4] == 0x03

    def test_encode_with_esc_byte(self):
        """Test encoding a message containing ESC byte."""
        data = b"\x01\xac\x03"  # Contains ESC (0xAC)
        encoded = Framing.encode(data)

        # ESC should be escaped
        assert encoded[0] == SOF
        assert encoded[-1] == EOF_BYTE
        # Data should have ESC before ESC
        # Original: 0x01 0xAC 0x03
        # Encoded:   SOF 0x01 ESC 0xAC 0x03 EOF
        assert encoded[1] == 0x01
        assert encoded[2] == ESC
        assert encoded[3] == ESC
        assert encoded[4] == 0x03

    def test_encode_with_eof_byte(self):
        """Test encoding a message containing EOF byte."""
        data = b"\x01\xad\x03"  # Contains EOF (0xAD)
        encoded = Framing.encode(data)

        # EOF should be escaped
        assert encoded[0] == SOF
        assert encoded[-1] == EOF_BYTE
        # Data should have ESC before EOF
        # Original: 0x01 0xAD 0x03
        # Encoded:   SOF 0x01 ESC 0xAD 0x03 EOF
        assert encoded[1] == 0x01
        assert encoded[2] == ESC
        assert encoded[3] == EOF_BYTE
        assert encoded[4] == 0x03

    def test_encode_empty_message(self):
        """Test encoding an empty message."""
        data = b""
        encoded = Framing.encode(data)

        # Should have SOF + EOF only
        assert len(encoded) == 2
        assert encoded[0] == SOF
        assert encoded[1] == EOF_BYTE

    def test_decode_single_message(self):
        """Test decoding a single framed message."""
        data = b"\x01\x02\x03\x04\x05"
        encoded = Framing.encode(data)
        decoded = Framing.decode(encoded)

        assert len(decoded) == 1
        assert decoded[0] == data

    def test_decode_escaped_message(self):
        """Test decoding a message with escaped bytes."""
        data = b"\x01\xab\xac\xad\x05"
        encoded = Framing.encode(data)
        decoded = Framing.decode(encoded)

        assert len(decoded) == 1
        assert decoded[0] == data

    def test_decode_multiple_messages(self):
        """Test decoding multiple framed messages."""
        msg1 = b"\x01\x02\x03"
        msg2 = b"\x04\x05\x06"
        encoded1 = Framing.encode(msg1)
        encoded2 = Framing.encode(msg2)
        combined = encoded1 + encoded2

        decoded = Framing.decode(combined)

        assert len(decoded) == 2
        assert decoded[0] == msg1
        assert decoded[1] == msg2

    def test_decode_with_garbage_before(self):
        """Test decoding with garbage bytes before the frame."""
        garbage = b"garbage\xff\xfe"
        data = b"\x01\x02\x03"
        encoded = Framing.encode(data)
        combined = garbage + encoded

        decoded = Framing.decode(combined)

        assert len(decoded) == 1
        assert decoded[0] == data

    def test_decode_empty_input(self):
        """Test decoding empty input."""
        decoded = Framing.decode(b"")
        assert decoded == []

    def test_decode_incomplete_frame(self):
        """Test decoding incomplete frame (no EOF)."""
        incomplete = bytes([SOF, 0x01, 0x02, 0x03])
        decoded = Framing.decode(incomplete)
        assert decoded == []

    def test_roundtrip_complex_data(self):
        """Test encode/decode roundtrip with complex data."""
        # Data with all special bytes
        data = bytes([0x00, 0xAB, 0xAC, 0xAD, 0xFF, 0x01, 0x02])
        encoded = Framing.encode(data)
        decoded = Framing.decode(encoded)

        assert len(decoded) == 1
        assert decoded[0] == data

    def test_decode_state_machine_reset(self):
        """Test that decoder state resets on unexpected SOF."""
        # SOF, data, SOF (unexpected), data, EOF
        invalid_frame = bytes([SOF, 0x01, 0x02, SOF, 0x03, 0x04, EOF_BYTE])
        decoded = Framing.decode(invalid_frame)
        # Should return empty or incomplete message
        # The second SOF should reset the decoder
        assert len(decoded) <= 1
