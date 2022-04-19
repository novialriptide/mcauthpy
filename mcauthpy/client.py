from typing import Tuple

import socket
import os
import hashlib
import requests
import copy
import zlib

from mcauthpy.exceptions import TooBigToUnpack

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
        self.compression_threshold = None

        self.email = email
        self.password = password
        self._mctoken = get_mc_access_token(self.email, self.password)
        self._mcprofile = authenticate(self._mctoken)
        self.username = self._mcprofile["name"]

        self.buffer = PacketBuffer(b"")
        self.cipher = None

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
            encrypted_data = self.connection.recv(1024)
            data = self.cipher.decrypt(encrypted_data)
            self.buffer.add(data)
            self.saved_buffer = copy.copy(self.buffer.data)

            try:
                packet_length = self.buffer.unpack_varint()
                packet = PacketBuffer(self.buffer.read(packet_length))

                if packet_length > len(self.buffer.data):
                    self.buffer.data = self.saved_buffer
                    continue

                elif packet_length >= self.compression_threshold:
                    data_length, data_length_bytes = packet.unpack_varint(
                        provide_bytes=True
                    )

                    compressed_length = packet_length - len(data_length_bytes)
                    compressed_data = packet.unpack_byte_array(compressed_length)
                    uncompressed_data = PacketBuffer(zlib.decompress(compressed_data))

                    print(uncompressed_data.data[:25])
                    packet_id, packet_id_bytes = uncompressed_data.unpack_varint(provide_bytes=True)
                    print(packet_id_bytes)
                    uncompressed_data = uncompressed_data.data

                elif packet_length < self.compression_threshold:
                    packet_id = packet.unpack_varint()
                    uncompressed_data = packet.unpack_byte_array(packet_length)

                return packet_id, PacketBuffer(uncompressed_data)

            except (TooBigToUnpack):
                self.buffer.data = self.saved_buffer
                continue

    def _get_compression_threshold(self) -> None:
        encrypted_data = self.connection.recv(1024)
        data = self.cipher.decrypt(encrypted_data)
        self.buffer.add(data)
        packet_length = self.buffer.unpack_varint()
        packet = PacketBuffer(self.buffer.read(packet_length))

        packet_id = packet.unpack_varint()
        if packet_id == 3:
            self.compression_threshold = packet.unpack_varint()

    def login_with_encryption(self) -> None:
        self.send_packet(
            0x00,
            pack_varint(self.protocol_version),
            pack_string(self.server_ip),
            pack_unsigned_short(self.server_port),
            pack_varint(2),
            encrypted=False
        )

        self.send_packet(0x00, pack_string(self.username), encrypted=False)

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
            encrypted=False
        )

        self.cipher = AES.new(
            shared_secret, AES.MODE_CFB, segment_size=8, iv=shared_secret
        )
        self.en_cipher = AES.new(
            shared_secret, AES.MODE_CFB, segment_size=8, iv=shared_secret
        )

        self._get_compression_threshold()

    def send_packet(self, packet_id: int, *fields: Tuple[bytes], encrypted: bool = True) -> bytes:
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
