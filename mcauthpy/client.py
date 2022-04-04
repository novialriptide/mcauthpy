import socket
import json
import time
import struct
import hashlib
import os
import requests
import uuid
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.serialization import load_der_public_key

class Client:
    def __init__(self, server_ip: str, server_port: int = 25565, protocol_version: int = 758):
        self.server_ip = server_ip
        self.server_port = server_port
        self.protocol_version = protocol_version
        self._timeout = 5
        self.connection = None
    
    def _connect(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.settimeout(self._timeout)
        self.connection.connect((self.server_ip, self.server_port))
    
    def _unpack_varint(self):
        data = 0
        for x in range(5):
            ordinal = self.connection.recv(1)
            
            if len(ordinal) == 0:
                break
            
            byte = ord(ordinal)
            data = data | (byte & 0x7F) << 7*x
            
            if not byte & 0x80:
                break
        
        return data

    def _pack_varint(self, data):
        ordinal = b""
        
        while True:
            byte = data & 0x7F
            data >>= 7
            ordinal += struct.pack("B", byte | (0x80 if data > 0 else 0))
            
            if data == 0:
                break
        
        return ordinal
    
    def _pack_data(self, data):
        if type(data) == str:
            data = data.encode("utf8")
            return self._pack_varint(len(data)) + data
        
        elif type(data) == int:
            return struct.pack("H", data)
        
        elif type(data) == float:
            return struct.pack("Q", int(data))
        
        else:
            return data
    
    def _send_packet(self, *args):
        data = b""
        
        for arg in args:
            data += self._pack_data(arg)

        self.connection.send(self._pack_varint(len(data)) + data) # send noncompressed data
    
    def _read(self, extra_varint: bool = False):
        packet_length = self._unpack_varint()
        packet_id = self._unpack_varint()

        data = bytes(bytearray(self.connection.recv(packet_length))[2:packet_length+2])

        return data
    
    def get_status(self):
        """Gets server status
        """
        self._connect()
        self._send_packet(b"\x00", b"\x00", self.server_ip, self.server_port, b"\x01")
        self._send_packet(b"\x00") # request packet

        data = self._read()
        response = json.loads(data.decode("utf8"))

        return response
    
    def login(self, username, access_token, player_uuid):
        """Initiate login with server.
        """
        self._connect()
        
        # Handshake packet
        self._send_packet(b"\x00", self._pack_varint(self.protocol_version), self.server_ip, self.server_port, b"\x02")
        
        # Login packet
        self._send_packet(b"\x00", username)
        public_key = self._read()
        print(public_key)
        public_key = RSA.generate(1024).publickey().export_key("DER")
        print(public_key)

        shared_secret = os.urandom(16)
        

        cipher = load_der_public_key(public_key, default_backend())
        encrypted_secret = cipher.encrypt(shared_secret, PKCS1v15())
        encryted_token = cipher.encrypt(shared_secret, PKCS1v15())

        generated_hash = hashlib.sha1()
        generated_hash.update(b"")
        generated_hash.update(shared_secret)
        generated_hash.update(public_key)
        generated_hash = generated_hash.hexdigest()
        
        response_post = requests.post(
            "https://sessionserver.mojang.com/session/minecraft/join",
            headers = {"Content-Type": "application/json"},
            json={
                "accessToken": access_token,
                "selectedProfile": player_uuid,
                "serverId": generated_hash
            }
        )
        
        if response_post.status_code != 204:
            raise Exception(f"Status code is not 204: ({response_post.status_code})")

        response_get = requests.get(f"https://sessionserver.mojang.com/session/minecraft/hasJoined?username={username}&serverId={generated_hash}&ip={socket.gethostbyname(socket.gethostname())}")
        data = response_get.json()
        
        
        # Encryption Request Packet
        #self._send_packet(b"\x01", generated_hash, len(public_key), public_key, len(shared_secret), shared_secret)
        
        # Encryption Response Packet
        self._send_packet(b"\x01", len(encrypted_secret), encrypted_secret, len(encryted_token), encryted_token)
        
        # Login Success Packet
        #clean_id = uuid.UUID(hex=data["id"])
        #self._send_packet(b"\x02", str(clean_id), data["name"])
        
        return data

    def get_ping(self):
        """Get server ping.
        
        Warning: Can only be used right after get_status()
        
        """
        self._send_packet(b"\x01", time.time() * 1000)
        unix = self._read()
        
        return int(time.time() * 1000) - struct.unpack("Q", unix)[0]