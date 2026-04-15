"""
Framing module for ZMK Studio protocol.

Implements SOF/ESC/EOF framing for serial communication.
"""

# Framing bytes
SOF = 0xAB  # Start of Frame
ESC = 0xAC  # Escape byte
EOF = 0xAD  # End of Frame
EOF_BYTE = EOF  # Alias for backward compatibility


class Framing:
    """
    Framing encoder/decoder for ZMK Studio protocol.

    Provides SOF/ESC/EOF framing for serial communication.
    """

    @staticmethod
    def encode(data: bytes) -> bytes:
        """
        Encode data with SOF/ESC/EOF framing.

        Args:
            data: Raw data bytes to frame

        Returns:
            Framed data bytes
        """
        return encode(data)

    @staticmethod
    def decode(data: bytes) -> list[bytes]:
        """
        Decode framed data, returns list of complete messages.

        Args:
            data: Raw data bytes from serial port

        Returns:
            List of decoded message payloads (without framing bytes)
        """
        return decode(data)

    # Aliases for compatibility
    frame = encode  # Alias: frame() -> encode()
    unframe = decode  # Alias: unframe() -> decode()


def encode(data: bytes) -> bytes:
    """
    Encode data with SOF/ESC/EOF framing.

    Args:
        data: Raw data bytes to frame

    Returns:
        Framed data bytes

    Example:
        >>> encode(b"hello")
        b'\\xabhello\\xad'
    """
    result = bytearray([SOF])
    for byte in data:
        if byte in (SOF, ESC, EOF):
            result.append(ESC)
        result.append(byte)
    result.append(EOF)
    return bytes(result)


def decode(data: bytes) -> list[bytes]:
    """
    Decode framed data, returns list of complete messages.

    Args:
        data: Raw data bytes from serial port

    Returns:
        List of decoded message payloads (without framing bytes)

    Example:
        >>> decode(b'\\xabhello\\xad\\xabworld\\xad')
        [b'hello', b'world']
    """
    IDLE, AWAITING_DATA, ESCAPED = 0, 1, 2
    state = IDLE
    current = bytearray()
    messages = []

    for byte in data:
        if state == IDLE:
            if byte == SOF:
                state = AWAITING_DATA
            # else: ignore garbage between messages
        elif state == AWAITING_DATA:
            if byte == SOF:
                # Unexpected SOF mid-frame, reset
                current = bytearray()
            elif byte == ESC:
                state = ESCAPED
            elif byte == EOF:
                messages.append(bytes(current))
                current = bytearray()
                state = IDLE
            else:
                current.append(byte)
        elif state == ESCAPED:
            current.append(byte)
            state = AWAITING_DATA

    return messages


__all__ = ["SOF", "ESC", "EOF", "encode", "decode"]
