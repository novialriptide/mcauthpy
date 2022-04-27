import socket
import struct
import io

from mcauthpy.exceptions import TooBigToUnpack

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

    def unpack_varint(self, provide_bytes: bool = False) -> int:
        """Unpacks a VarInt.

        Parameters:
            provide_bytes (int): Provide the length of the VarInt.

        Returns:
            int: The unpacked VarInt as a Python integer.

        """
        value = 0
        position = 0
        read_bytes = b""

        while True:
            current_byte = self.read(1)
            read_bytes += current_byte

            value |= (ord(current_byte) & SEGMENT_BITS) << position

            if ord(current_byte) & CONTINUE_BIT == 0:
                break

            position += 7

            if position >= 32:
                raise TooBigToUnpack("VarInt is too big")

        if value & (1 << 31):
            value -= 1 << 32

        if provide_bytes:
            return value, read_bytes
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
                raise TooBigToUnpack("VarLong is too big")

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
        return self.read(16 + 1)

    def unpack_short(self) -> int:
        return struct.unpack("h", self.read(2))[0]

    def unpack_double(self) -> int:
        return struct.unpack("d", self.read(8))[0]
