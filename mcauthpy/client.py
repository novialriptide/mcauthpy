from typing import Tuple

import socket
import struct
import zlib

from .packet_buffer import PacketBuffer
from .packet_pack import pack_varint

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

        self.recieved_data = b""

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

    def receive_data(self, data: bytes) -> None:
        self.received_data += data

    def send_packet(self, packet_id: int, *fields: Tuple[bytes]) -> bytes:
        """Sends a packet to the connected server.

        Parameters:
            packet_id (int): The packet's id in hexadecimal format.
            *fields (Tuple[bytes]): The packed data to send to the server.

        Returns:
            bytes: The packet that is sent to the server.

        """
        data = b""

        data += pack_varint(packet_id)

        for field in fields:
            data += field

        out = pack_varint(len(data)) + data
        self.connection.send(out)
        return out

    def get_packet(
        self, force_size: int or None = None, compressed: bool = False
    ) -> PacketBuffer:
        """Returns a PacketBuffer that was sent from the server.

        Returns:
            PacketBuffer: The packed data.

        """
        if force_size is None:
            packet_length = self._unpack_varint()
        if force_size is not None:
            packet_length = force_size

        return PacketBuffer(self.connection.recv(packet_length), compressed=compressed)

    def raw_read(self, bytes_size: int = 1024) -> bytes:
        """Reads data sent from the server.

        Returns:
            bytes: The raw data.

        """
        return self.connection.recv(bytes_size)
