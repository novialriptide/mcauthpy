import socket
import struct
import io

SEGMENT_BITS = 0x7F
CONTINUE_BIT = 0x80


class PacketBuffer:
    def __init__(self, data: bytes, compressed: bool = False) -> None:
        self.data = data
        self.compressed = compressed

    def read(self, length: int) -> bytes:
        out = self.data[:length]
        self.data = self.data[length:]

        return out

    def add(self, data: bytes) -> None:
        self.data += data

    def unpack_varint(self, _connection: socket.socket = None) -> int:
        """Unpacks a VarInt.

        Parameters:
            _connection (socket.socket): If you want to unpack from a socket connection.

        Returns:
            int: The unpacked VarInt as a Python integer.

        """
        value = 0
        position = 0

        while True:
            if _connection is not None:
                current_byte = _connection.recv(1)
            if _connection is None:
                current_byte = self.read(1)

            value |= (ord(current_byte) & SEGMENT_BITS) << position

            if ord(current_byte) & CONTINUE_BIT == 0:
                break

            position += 7

            if position >= 32:
                raise RuntimeError("VarInt is too big")

        if value & (1 << 31):
            value -= 1 << 32

        return value

    def unpack_varlong(self) -> int:
        """Unpacks a VarLong.

        Returns:
            int: The unpacked VarLong as a Python integer.

        """
        value = 0
        position = 0

        while True:
            current_byte = self.read(1)
            value |= (ord(current_byte) & SEGMENT_BITS) << position

            if (ord(current_byte) & CONTINUE_BIT) == 0:
                break

            position += 7

            if position >= 64:
                raise RuntimeError("VarLong is too big")

        return value

    def unpack_string(self) -> bytes:
        """Unpacks a string.

        Returns:
            str: The unpacked string.

        """
        str_length = self.unpack_varint()
        return self.read(str_length)
        # return self.read(1 + (str_length * 4) + 3)

    def unpack_byte_array(self, length) -> bytes:
        """Unpacks a string.

        Returns:
            str: The unpacked string.

        """
        return self.read(length)

    def unpack_boolean(self) -> bool:
        """Unpacks a boolean.

        Returns:
            bool: The unpacked boolean.

        """
        return struct.unpack("?", self.read(1))[0]

    def unpack_uuid(self) -> bool:
        """Unpacks an UUID.

        Returns:
            bool: The unpacked UUID.

        """
        return self.unpack_string(16)
