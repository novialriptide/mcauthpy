from typing import Tuple

import socket
import os
import hashlib
import requests

from .auth import authenticate, get_mc_access_token
from .packet_buffer import PacketBuffer
from .packet_pack import (
    minecraft_sha1_hash,
    pack_string,
    pack_unsigned_short,
    pack_varint,
)

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.serialization import load_der_public_key
from Crypto.Cipher import AES

SEGMENT_BITS = 0x7F
CONTINUE_BIT = 0x80


class Client:
    def __init__(self, email: str, password: str) -> None:
        """Initializes the client."""
        self._timeout = 5
        self.connection = None
        self.server_ip = None
        self.server_port = None
        self.protocol_version = None

        self.email = email
        self.password = password
        self._mctoken = get_mc_access_token(self.email, self.password)
        self._mcprofile = authenticate(self._mctoken)
        self.username = self._mcprofile["name"]

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

    def login_with_encryption(self) -> None:
        self.send_packet(
            0x00,
            pack_varint(self.protocol_version),
            pack_string(self.server_ip),
            pack_unsigned_short(self.server_port),
            pack_varint(2),
        )

        self.send_packet(0x00, pack_string(self.username))

        # Client Authentication
        p = PacketBuffer(self.connection.recv(1024))
        server_id = p.read(4)
        public_key_length = p.unpack_varint()
        public_key = p.unpack_byte_array(public_key_length)
        verify_token_length = p.unpack_varint()
        verify_token = p.unpack_byte_array(verify_token_length)

        shared_secret = os.urandom(16)
        cipher = load_der_public_key(public_key, default_backend())
        encrypted_secret = cipher.encrypt(shared_secret, PKCS1v15())
        encrypted_token = cipher.encrypt(verify_token, PKCS1v15())

        generated_hash = hashlib.sha1()
        # generated_hash.update(server_id) # if 1.7.x > ??
        generated_hash.update(b"")
        generated_hash.update(shared_secret)
        generated_hash.update(public_key)
        generated_hash = minecraft_sha1_hash(generated_hash)

        response_post = requests.post(
            "https://sessionserver.mojang.com/session/minecraft/join",
            headers={"Content-Type": "application/json"},
            json={
                "accessToken": self._mctoken,
                "selectedProfile": self._mcprofile["id"],
                "serverId": generated_hash,
            },
        )

        if response_post.status_code != 204:
            raise Exception(f"Status code is not 204: ({response_post.status_code})")

        # Encryption Response Packet
        erp = self.send_packet(
            0x01,
            pack_varint(len(encrypted_secret)),
            encrypted_secret,
            pack_varint(len(encrypted_token)),
            encrypted_token,
        )

        self.cipher = AES.new(
            shared_secret, AES.MODE_CFB, segment_size=8, iv=shared_secret
        )
        self.buffer = PacketBuffer(b"")

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

    def unpack_packet(
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
