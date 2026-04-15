"""
Protobuf encoder/decoder for ZMK Studio protocol.

Minimal protobuf implementation to avoid external dependencies.
"""

from typing import Any


class Protobuf:
    """
    Protobuf encoder/decoder for ZMK Studio protocol.

    Provides static methods for encoding and decoding protobuf messages.
    """

    @staticmethod
    def encode_varint(value: int) -> bytes:
        """Encode unsigned varint.

        Args:
            value: Non-negative integer to encode

        Returns:
            Varint-encoded bytes

        Raises:
            ValueError: If value is negative

        Example:
            >>> encode_varint(300)
            b'\\xac\\x02'
        """
        if value < 0:
            raise ValueError("Use encode_zigzag for signed ints")
        result = bytearray()
        while value > 0x7F:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)

    @staticmethod
    def decode_varint(data: bytes, offset: int = 0) -> tuple[int, int]:
        """Decode unsigned varint.

        Args:
            data: Bytes containing varint
            offset: Starting position in data

        Returns:
            Tuple of (value, bytes_consumed)

        Example:
            >>> decode_varint(b'\\xac\\x02')
            (300, 2)
        """
        result = 0
        shift = 0
        pos = offset
        while pos < len(data):
            byte = data[pos]
            result |= (byte & 0x7F) << shift
            pos += 1
            if not (byte & 0x80):
                break
            shift += 7
        return result, pos - offset

    @staticmethod
    def encode_zigzag(value: int) -> bytes:
        """Encode signed integer using ZigZag encoding.

        ZigZag encoding maps signed integers to unsigned:
        - 0 -> 0, -1 -> 1, 1 -> 2, -2 -> 3, 2 -> 4, ...

        Args:
            value: Signed integer to encode

        Returns:
            ZigZag-encoded varint bytes

        Example:
            >>> encode_zigzag(-1)
            b'\\x01'
        """
        zigzag = (value << 1) ^ (value >> 31)
        return encode_varint(zigzag)

    @staticmethod
    def decode_zigzag(varint_value: int) -> int:
        """Decode sint32 from ZigZag-encoded varint value.

        Args:
            varint_value: Unsigned varint value

        Returns:
            Signed integer

        Example:
            >>> decode_zigzag(1)
            -1
        """
        return (varint_value >> 1) ^ -(varint_value & 1)

    @staticmethod
    def encode_tag(field_number: int, wire_type: int) -> bytes:
        """Encode a protobuf tag (field_number << 3 | wire_type).

        Args:
            field_number: Field number
            wire_type: Wire type (0=varint, 1=64-bit, 2=LD, 5=32-bit)

        Returns:
            Tag bytes

        Example:
            >>> encode_tag(1, 2)
            b'\\x0a'
        """
        return encode_varint((field_number << 3) | wire_type)

    @staticmethod
    def encode_bool(field_number: int, value: bool) -> bytes:
        """Encode a bool field.

        Args:
            field_number: Field number
            value: Boolean value

        Returns:
            Encoded field (empty if False in proto3)

        Example:
            >>> encode_bool(1, True)
            b'\\x08\\x01'
        """
        if value:
            return encode_tag(field_number, 0) + b"\\x01"
        return b""  # Proto3: default values are not encoded

    @staticmethod
    def encode_uint32(field_number: int, value: int) -> bytes:
        """Encode a uint32 field.

        Args:
            field_number: Field number
            value: Unsigned 32-bit integer

        Returns:
            Encoded field (empty if 0)

        Example:
            >>> encode_uint32(1, 300)
            b'\\x08\\xac\\x02'
        """
        if value == 0:
            return b""
        return encode_tag(field_number, 0) + encode_varint(value)

    @staticmethod
    def encode_int32(field_number: int, value: int) -> bytes:
        """Encode an int32 field.

        Args:
            field_number: Field number
            value: Signed 32-bit integer

        Returns:
            Encoded field (empty if 0)

        Example:
            >>> encode_int32(1, -1)
            b'\\x08\\x01'
        """
        if value == 0:
            return b""
        tag = encode_tag(field_number, 0)
        if value >= 0:
            return tag + encode_varint(value)
        else:
            # Negative int32: encode as 10-byte varint (two's complement)
            return (
                tag + encode_varint(value & 0xFFFFFFFF) + b"\\x00\\x00\\x00\\x00\\x00"
            )

    @staticmethod
    def encode_sint32(field_number: int, value: int) -> bytes:
        """Encode a sint32 field (ZigZag + varint).

        Args:
            field_number: Field number
            value: Signed 32-bit integer

        Returns:
            Encoded field (empty if 0)

        Example:
            >>> encode_sint32(1, -1)
            b'\\x08\\x01'
        """
        if value == 0:
            return b""
        return encode_tag(field_number, 0) + encode_zigzag(value)

    @staticmethod
    def encode_string(field_number: int, value: str) -> bytes:
        """Encode a string field.

        Args:
            field_number: Field number
            value: String value

        Returns:
            Encoded field (empty if empty string)

        Example:
            >>> encode_string(1, "test")
            b'\\x0a\\x04test'
        """
        if not value:
            return b""
        encoded = value.encode("utf-8")
        return encode_tag(field_number, 2) + encode_varint(len(encoded)) + encoded

    @staticmethod
    def encode_ld(field_number: int, data: bytes) -> bytes:
        """Encode a length-delimited field (submessage or bytes).

        Args:
            field_number: Field number
            data: Bytes to encode

        Returns:
            Encoded field (empty if empty)

        Example:
            >>> encode_ld(1, b"hello")
            b'\\x0a\\x05hello'
        """
        if not data:
            return b""
        return encode_tag(field_number, 2) + encode_varint(len(data)) + data

    @staticmethod
    def encode_bytes(field_number: int, data: bytes) -> bytes:
        """Encode a bytes field (for raw keymap data).

        Args:
            field_number: Field number
            data: Raw bytes to encode

        Returns:
            Tag + length + data bytes

        Example:
            >>> encode_bytes(1, b"\\x01\\x02\\x03")
            b'\\x0a\\x02\\x03\\x01\\x02\\x03'
        """
        return encode_tag(field_number, 2) + encode_varint(len(data)) + data

    @staticmethod
    def encode_repeated_ld(field_number: int, items: list[bytes]) -> bytes:
        """Encode repeated length-delimited fields."""
        result = bytearray()
        for item in items:
            result.extend(encode_ld(field_number, item))
        return bytes(result)

    @staticmethod
    def decode_message(data: bytes) -> dict[int, list[tuple[int, Any]]]:
        """Decode a protobuf message into a dict.

        Returns:
            Dict mapping field numbers to list of (wire_type, value) tuples

        Example:
            >>> decode_message(b'\\x08\\x01\\x10\\x02')
            {1: [(0, 1)], 2: [(0, 2)]}
        """
        result = {}
        offset = 0
        while offset < len(data):
            try:
                tag, tlen = decode_varint(data, offset)
                offset += tlen
                field_number = tag >> 3
                wire_type = tag & 7

                if field_number == 0:
                    break

                if wire_type == 0:  # Varint
                    value, vlen = decode_varint(data, offset)
                    offset += vlen
                elif wire_type == 1:  # 64-bit
                    value = data[offset : offset + 8]
                    offset += 8
                elif wire_type == 2:  # Length-delimited
                    length, llen = decode_varint(data, offset)
                    offset += llen
                    value = data[offset : offset + length]
                    offset += length
                elif wire_type == 5:  # 32-bit
                    value = data[offset : offset + 4]
                    offset += 4
                else:
                    # Skip unknown wire type
                    break

                if field_number not in result:
                    result[field_number] = []
                result[field_number].append((wire_type, value))
            except (IndexError, ValueError):
                break
        return result

    __all__ = [
        "encode_varint",
        "decode_varint",
        "encode_zigzag",
        "decode_zigzag",
        "encode_tag",
        "encode_bool",
        "encode_uint32",
        "encode_int32",
        "encode_sint32",
        "encode_string",
        "encode_ld",
        "encode_bytes",
        "decode_message",
    ]
