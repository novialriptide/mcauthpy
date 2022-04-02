import socket
import json
import time
import struct

class Client:
    def __init__(self, server_ip: str, server_port: int = 25565):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.server_port = server_port
    
    def _unpack_varint(self):
        data = 0
        for x in range(5):
            ordinal = self.socket.recv(1)
            
            if len(ordinal) == 0:
                break
            
            byte = ord(ordinal)
            data = data | (byte & 0x7F) << 7*x
            
            if not byte & 0x80:
                break
        
        return data
    