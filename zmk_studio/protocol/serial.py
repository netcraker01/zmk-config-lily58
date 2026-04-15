"""
ZMK Studio Serial Client

Implements CDC-ACM serial client for ZMK Studio RPC protocol.
Uses pyserial.Serial for communication at 12500 baud (ZMK Studio standard).

Key features:
- Auto-detection of ZMK keyboard serial port
- Timeout management for slow 12500 baud communication
- Frame-based receive for handling large responses
- Flush stale data on connect
"""

import time
import logging
from typing import Optional, List, Callable

import serial
import serial.tools.list_ports

from . import framing

logger = logging.getLogger(__name__)


class SerialClient:
    """
    CDC-ACM serial client for ZMK Studio RPC protocol.

    Handles serial communication at 12500 baud with proper timeout
    management for slow data rates. Supports frame-based receive
    for handling large responses (e.g., keymap data).
    """

    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: int = 12500,
        timeout: float = 1.0,
        debug: bool = False,
    ):
        """
        Initialize serial client.

        Args:
            port: Serial port name (e.g., "COM8" or "/dev/ttyACM0")
            baudrate: Baud rate (default: 12500 for ZMK Studio)
            timeout: Default read timeout in seconds
            debug: Enable debug logging
        """
        self.port = port
        self.baudrate = baudrate
        self.default_timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.debug = debug
        self._request_id = 0

    def find_port(self) -> Optional[str]:
        """
        Auto-detect ZMK keyboard serial port.

        Returns:
            Port name if found, None otherwise

        Scans available serial ports and returns the first one that
        appears to be a USB serial device (common for ZMK keyboards).
        """
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            desc = p.description.lower()
            # Look for USB serial devices
            if (
                "usb" in desc
                or "serial" in desc
                or "dispositivo" in desc
                or "acm" in desc
            ):
                logger.debug(f"Found potential ZMK port: {p.device} - {p.description}")
                return p.device

        # Fallback: return first available port
        if ports:
            logger.debug(f"Fallback to first port: {ports[0].device}")
            return ports[0].device

        return None

    def connect(self) -> bool:
        """
        Open serial connection.

        Returns:
            True if connection successful, False otherwise

        Auto-detects port if not specified, flushes any stale data,
        and waits for connection to stabilize.
        """
        if not self.port:
            self.port = self.find_port()

        if not self.port:
            logger.error("No serial port found")
            return False

        try:
            logger.info(f"Connecting to {self.port} at {self.baudrate} baud")
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.default_timeout,
                write_timeout=self.default_timeout,
            )
            time.sleep(0.5)  # Let connection stabilize

            # Flush any stale data
            if self.ser.in_waiting:
                stale_data = self.ser.read(self.ser.in_waiting)
                if self.debug:
                    logger.debug(f"Flushed {len(stale_data)} bytes of stale data")

            logger.info("Connected to serial port")
            return True

        except (serial.SerialException, OSError) as e:
            logger.error(f"Failed to connect to {self.port}: {e}")
            return False

    def disconnect(self) -> None:
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            logger.debug("Closing serial connection")
            self.ser.close()
            self.ser = None

    def send(self, data: bytes) -> None:
        """
        Send raw bytes over serial connection.

        Args:
            data: Bytes to send

        Raises:
            RuntimeError: If not connected
        """
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Not connected to serial port")

        if self.debug:
            logger.debug(f"TX [{len(data)}]: {data.hex()}")

        self.ser.write(data)
        self.ser.flush()

    def send_framed(self, data: bytes) -> bool:
        """
        Send framed data (adds SOF/ESC/EOF framing).

        Args:
            data: Raw bytes to frame and send

        Returns:
            True if sent successfully, False on error

        Uses Framing.encode to add SOF prefix, escape special bytes,
        and add EOF suffix before transmission.
        """
        try:
            framed = framing.encode(data)
            self.send(framed)
            return True
        except Exception as e:
            logger.error(f"Failed to send framed data: {e}")
            return False

    def receive(
        self, timeout: Optional[float] = None, size: Optional[int] = None
    ) -> Optional[bytes]:
        """
        Receive raw bytes from serial connection.

        Args:
            timeout: Read timeout in seconds (uses default if None)
            size: Number of bytes to read (reads all available if None)

        Returns:
            Received bytes, or None if timeout or error
        """
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Not connected to serial port")

        old_timeout = self.ser.timeout
        if timeout is not None:
            self.ser.timeout = timeout

        try:
            if size is not None:
                data = self.ser.read(size)
            else:
                # Read all available data
                data = self.ser.read(self.ser.in_waiting or 1)

            if self.debug and data:
                logger.debug(f"RX [{len(data)}]: {data.hex()}")

            return data if data else None

        finally:
            self.ser.timeout = old_timeout

    def receive_framed(
        self,
        timeout: float = 8.0,
        chunk_timeout: float = 1.5,
        silence_timeout: float = 3.0,
    ) -> Optional[List[bytes]]:
        """
        Receive framed data, collecting multiple chunks until transmission complete.

        For large responses (keymap), data may come in multiple chunks over
        slow 12500 baud. This method reads patiently until silence is detected.

        Args:
            timeout: Maximum total time to wait for data
            chunk_timeout: Silence duration (seconds) that indicates end of transmission
            silence_timeout: Time to wait before giving up if no data received

        Returns:
            List of decoded framed messages, or None if timeout or error

        Strategy:
        1. Use short timeout (0.1s) to poll for data
        2. Read all available bytes in chunks
        3. Track last data receipt time
        4. When no data for chunk_timeout seconds, consider transmission complete
        5. If no data at all after silence_timeout seconds, give up
        """
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Not connected to serial port")

        self.ser.timeout = 0.1
        raw = bytearray()
        start = time.time()
        last_data = start

        while time.time() - start < timeout:
            available = self.ser.in_waiting
            if available > 0:
                chunk = self.ser.read(available)
                raw.extend(chunk)
                last_data = time.time()
            elif len(raw) > 0 and time.time() - last_data > chunk_timeout:
                # Got data, then silence = end of transmission
                # At 12500 baud, 1.5s = ~1875 bytes of silence = definitely done
                if self.debug:
                    logger.debug(f"Transmission complete: {len(raw)} bytes received")
                break
            elif len(raw) == 0 and time.time() - start > silence_timeout:
                # No data at all after silence_timeout seconds
                if self.debug:
                    logger.debug(
                        f"No data received after {silence_timeout}s, giving up"
                    )
                break

            time.sleep(0.01)

        if not raw:
            logger.debug("No data received")
            return None

        if self.debug:
            logger.debug(f"RX raw [{len(raw)}]: {raw.hex()}")

        # Decode framed messages
        messages = framing.decode(bytes(raw))
        if not messages:
            logger.debug("No complete framed messages found")
            if self.debug:
                logger.debug(f"RX first 50 bytes: {raw[:50].hex()}")
            return None

        if self.debug:
            logger.debug(
                f"Decoded {len(messages)} framed message(s): sizes={[len(m) for m in messages]}"
            )

        return messages

    def receive_until(
        self, condition: Callable[[List[bytes]], bool], timeout: float = 8.0
    ) -> Optional[List[bytes]]:
        """
        Receive framed data until a condition is met.

        Args:
            condition: Callable that takes list of messages and returns True when done
            timeout: Maximum time to wait

        Returns:
            List of decoded framed messages when condition is met, None if timeout
        """
        self.ser.timeout = 0.1
        raw = bytearray()
        start = time.time()
        last_data = start

        while time.time() - start < timeout:
            available = self.ser.in_waiting
            if available > 0:
                chunk = self.ser.read(available)
                raw.extend(chunk)
                last_data = time.time()

                # Try decoding and check condition
                messages = framing.decode(bytes(raw))
                if messages and condition(messages):
                    return messages

            elif len(raw) > 0 and time.time() - last_data > 1.5:
                # Silence, check condition one last time
                messages = framing.decode(bytes(raw))
                if messages:
                    if condition(messages):
                        return messages
                break

            time.sleep(0.01)

        return None

    def flush(self) -> None:
        """Flush input and output buffers."""
        if self.ser and self.ser.is_open:
            if self.ser.in_waiting:
                self.ser.read(self.ser.in_waiting)
            self.ser.flush()

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False

    @property
    def request_id(self) -> int:
        """Get current request ID."""
        return self._request_id

    def next_request_id(self) -> int:
        """
        Increment and return next request ID.

        Returns:
            New request ID
        """
        self._request_id += 1
        return self._request_id
