from typing import Tuple

import socket
import os
import hashlib
import requests
import copy
import zlib

from ._auth import authenticate, get_mc_access_token
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
    def __init__(self) -> None:
        """Do not use mcauthpy.Client() directly. Use either
        >>> mcauthpy.Client.login_from_microsoft()
        >>> mcauthpy.Client.login_from_username()
        """
        self.buffer = PacketBuffer(b"")
        self.cipher = None

        self._timeout = 5
        self.connection = None
        self.server_ip = None
        self.server_port = None
        self.protocol_version = None
        self.compression_threshold = -1
    
    @classmethod
    def login_from_microsoft(cls, email: str, password: str) -> "Client":
        """Initializes the client. The account must be
        migrated from Mojang! All packets are encrypted.

        Parameters:
            email (str): The Microsoft account's email address.
            password (str): The Microsoft account's password.

        """
        instance = cls()
        
        instance.email = email
        instance.password = password
        mctoken = get_mc_access_token(instance.email, instance.password)
        mcprofile = authenticate(mctoken)

        instance.username = mcprofile["name"]
        instance.server_online_mode = True

    @classmethod
    def login_from_username(cls, username: str) -> "Client":
        """Initializes the client. All packets are NOT encrypted.

        Servers must have this configuration
        so you can use this constructor.
        ```
        online-mode=false
        ```

        Parameters:
            username (str): The Minecraft client's username.

        """
        instance = cls()
        instance.username = username
        instance.server_online_mode = False

        return instance

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

    def get_received_buffer(self) -> Tuple[int, PacketBuffer]:
        while True:
            received_data = self.connection.recv(1024)
            if self.cipher is not None:
                received_data = self.cipher.decrypt(received_data)

            self.buffer.add(received_data)
            self.saved_buffer = copy.copy(self.buffer.data)

            try:
                packet_length = self.buffer.unpack_varint()
            except TypeError:
                return None, None

            if packet_length > len(self.buffer.data):
                self.buffer.data = self.saved_buffer
                continue

            packet = PacketBuffer(self.buffer.read(packet_length))

            if self.compression_threshold != -1:
                data_length = packet.unpack_varint()

                if data_length > 0:
                    uncompressed_data = PacketBuffer(zlib.decompress(packet.data))
                else:
                    uncompressed_data = PacketBuffer(packet.data)

                packet_id = uncompressed_data.unpack_varint()
                uncompressed_data = uncompressed_data.data

            else:
                packet_id = packet.unpack_varint()
                uncompressed_data = packet.unpack_byte_array(packet_length)

            return packet_id, PacketBuffer(uncompressed_data)

    def _get_compression_threshold(self, received_data) -> None:
        received_data = self.connection.recv(1024)
        if self.cipher is not None:
            received_data = self.cipher.decrypt(received_data)

        self.buffer.add(received_data)
        packet_length = self.buffer.unpack_varint()
        packet = PacketBuffer(self.buffer.read(packet_length))

        packet_id = packet.unpack_varint()
        if packet_id == 3:
            self.compression_threshold = packet.unpack_varint()

    def _login(self) -> None:
        self.send_packet(
            0x00,
            pack_varint(self.protocol_version),
            pack_string(self.server_ip),
            pack_unsigned_short(self.server_port),
            pack_varint(2),
            encrypted=False,
        )

        self.send_packet(0x00, pack_string(self.username), encrypted=False)

    def client_auth(self, received_data) -> None:
        # Client Authentication
        p = PacketBuffer(received_data)
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
            encrypted=False,
        )

        self.cipher = AES.new(
            shared_secret, AES.MODE_CFB, segment_size=8, iv=shared_secret
        )
        self.en_cipher = AES.new(
            shared_secret, AES.MODE_CFB, segment_size=8, iv=shared_secret
        )

    def login(self) -> None:
        self._login()
        received_data = self.connection.recv(1024)

        try:
            self.client_auth(received_data)
        except TypeError:
            self.buffer.add(received_data)

        self._get_compression_threshold(received_data)

    def send_packet(
        self, packet_id: int, *fields: Tuple[bytes], encrypted: bool = True
    ) -> bytes:
        """Sends a packet to the connected server.

        Parameters:
            packet_id (int): The packet's id in hexadecimal format.
            *fields (Tuple[bytes]): The packed data to send to the server.
            encrypted (bool): If the packet should be sent encrypted or not.

        Returns:
            bytes: The packet that is sent to the server.

        """
        packet_id = pack_varint(packet_id)

        data = b""
        for field in fields:
            data += field

        if encrypted:
            data = packet_id + data
            out = pack_varint(len(data)) + data
            self.connection.send(out)
            return self.en_cipher.encrypt(out)

        elif not encrypted:
            data = packet_id + data
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
