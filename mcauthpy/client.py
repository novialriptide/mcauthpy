from typing import Tuple

import socket
import struct

SEGMENT_BITS = 0x7F
CONTINUE_BIT = 0x80


class Client:
    def __init__(self) -> None:
        """Initializes the client."""
        self._timeout = 5
        self.connection = None
        self.server_ip = None
        self.server_port = None
        self.protocol_version = None

    def connect(
        self, server_ip: str, server_port: int = 25565, protocol_version: int = 758
    ) -> None:
        """Connects to a server with specified server ip, server port, and protocol version.

        Parameters:
            server_ip (str): The server's ip address.
            server_port (int): The server's port; 25565 is the default for most servers.
            protocol_version (int): The Minecraft: Java Edition protocol version. (ex: 758 = 1.18.2)

        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.protocol_version = protocol_version
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.settimeout(self._timeout)
        self.connection.connect((self.server_ip, self.server_port))

    def minecraft_sha1_hash(self, sha1_hash):
        return format(
            int.from_bytes(sha1_hash.digest(), byteorder="big", signed=True), "x"
        )

    def pack_boolean(self, value: bool) -> bytes:
        """Converts a boolean to a boolean in bytes format.

        Parameters:
            value (bool): Data to convert.

        Returns:
            bytes: Data in bytes format.

        """
        if value:
            return b"\x01"
        else:
            return b"\x00"

    def pack_varint(self, value: int) -> bytes:
        """Converts a Python int to a Minecraft: Java Edition VarInt. Does not
        support negatives.

        Parameters:
            value (int): Data to convert.

        Returns:
            bytes: Data in Minecraft: Java Edition VarInt format.

        """
        data = b""

        while True:
            if (value & ~SEGMENT_BITS) == 0:
                data += struct.pack("B", value)
                return data

            data += struct.pack("B", (value & SEGMENT_BITS) | CONTINUE_BIT)

            value >>= 7

    def pack_varlong(self, value: int) -> bytes:
        """Converts a Python int to a Minecraft: Java Edition VarLong. This
        function directly calls `pack_varint()`. Does not support negatives.

        Parameters:
            value (int): Data to convert.

        Returns:
            bytes: Data in Minecraft: Java Edition VarLong format.

        """
        return self.pack_varint(value)

    def pack_unsigned_short(self, value: int) -> bytes:
        """Converts a Python int to an Unsigned Short.
        Directly calls struct.pack("H", value).

        Returns:
            bytes: Data in Unsigned Short format.

        """
        return struct.pack("H", value)

    def pack_string(self, value: str) -> bytes:
        """Converts a Python string to a Minecraft: Java Edition String.

        Returns:
            bytes: Data in Minecraft: Java Edition String format.

        """
        value = value.encode("utf-8")
        return self.pack_varint(len(value)) + value

    def send_packet(self, packet_id: int, *fields: Tuple[bytes]) -> bytes:
        """Sends a packet to the connected server.

        Parameters:
            packet_id (int): The packet's id in hexadecimal format.
            *fields (Tuple[bytes]): The packed data to send to the server.

        Returns:
            bytes: The packet that is sent to the server.

        """
        data = b""

        data += self.pack_varint(packet_id)

        for field in fields:
            data += field

        out = self.pack_varint(len(data)) + data
        self.connection.send(out)
        return out

    def read(self) -> bytes:
        """Reads and unpacks the packet sent from the server.

        Returns:
            bytes: The unpacked data.

        """
        packet_length = self.unpack_varint()
        packet_id = self.unpack_varint()
        data_length = self.unpack_varint()

        return self.connection.recv(data_length)

    def raw_read(self, bytes_size: int = 1024) -> bytes:
        """Reads data sent from the server.

        Returns:
            bytes: The raw data.

        """
        return self.connection.recv(bytes_size)
