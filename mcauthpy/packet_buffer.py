import struct
import io

SEGMENT_BITS = 0x7F
CONTINUE_BIT = 0x80

class PacketBuffer:
    def __init__(self, data: bytes) -> None:
        self.data = io.BytesIO(data)

    def unpack_varint(self) -> int:
        """Unpacks a VarInt from socket connection.

        Returns:
            int: The unpacked VarInt as a Python integer.

        """
        value = 0
        position = 0

        while True:
            current_byte = self.data.read(1)
            value |= (ord(current_byte) & SEGMENT_BITS) << position

            if ord(current_byte) & CONTINUE_BIT == 0:
                break

            position += 7

            if position >= 32:
                raise RuntimeError("VarInt is too big")

        return value

    def unpack_varlong(self) -> int:
        """Unpacks a VarLong from socket connection.

        Returns:
            int: The unpacked VarLong as a Python integer.

        """
        value = 0
        position = 0

        while True:
            current_byte = self.data.read(1)
            value |= (ord(current_byte) & SEGMENT_BITS) << position

            if (ord(current_byte) & CONTINUE_BIT) == 0:
                break

            position += 7

            if position >= 64:
                raise RuntimeError("VarLong is too big")
        
        return value

    def unpack_string(self, str_length) -> bytes:
        """Unpacks a string from socket connection.
        
        Returns:
            str: The unpacked string.

        """
        return self.data.read(1 + (str_length * 4) + 3)

    def unpack_byte_array(self, length) -> bytes:
        """Unpacks a string from socket connection.
        
        Returns:
            str: The unpacked string.

        """
        return self.data.read(length)

    def unpack_boolean(self) -> bool:
        """Unpacks a boolean from socket connection.
        
        Returns:
            bool: The unpacked boolean.

        """
        return struct.unpack("?", self.data.read(1))[0]

    def unpack_uuid(self) -> bool:
        """Unpacks an UUID from socket connection.
        
        Returns:
            bool: The unpacked UUID.

        """
        return self.unpack_string(16)