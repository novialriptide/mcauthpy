import socket
import struct
import io

SEGMENT_BITS = 0x7F
CONTINUE_BIT = 0x80

def unpack_packet(connection) -> "PacketBuffer":
    buffer = PacketBuffer(b"")
    length = buffer.unpack_varint(_connection=connection)
    buffer.data = connection.recv(length)
    return buffer

class PacketBuffer:
    def __init__(self, connection: socket.socket, compressed: bool = False) -> None:
        self.packet_length = self.unpack_varint(_connection = connection)
        self.data = io.BytesIO(connection.recv(self.packet_length))
        self.compressed = compressed

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
                current_byte = self.data.read(1)

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
            current_byte = self.data.read(1)
            value |= (ord(current_byte) & SEGMENT_BITS) << position

            if (ord(current_byte) & CONTINUE_BIT) == 0:
                break

            position += 7

            if position >= 64:
                raise RuntimeError("VarLong is too big")

        return value

    def unpack_string(self, str_length) -> bytes:
        """Unpacks a string.

        Returns:
            str: The unpacked string.

        """
        return self.data.read(1 + (str_length * 4) + 3)

    def unpack_byte_array(self, length) -> bytes:
        """Unpacks a string.

        Returns:
            str: The unpacked string.

        """
        return self.data.read(length)

    def unpack_boolean(self) -> bool:
        """Unpacks a boolean.

        Returns:
            bool: The unpacked boolean.

        """
        return struct.unpack("?", self.data.read(1))[0]

    def unpack_uuid(self) -> bool:
        """Unpacks an UUID.

        Returns:
            bool: The unpacked UUID.

        """
        return self.unpack_string(16)
