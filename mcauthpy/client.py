import socket
import struct

SEGMENT_BITS = 0x7F
CONTINUE_BIT = 0x80

class Client:
    def __init__(self, server_ip: str, server_port: int = 25565, protocol_version: int = 758):
        self.server_ip = server_ip
        self.server_port = server_port
        self.protocol_version = protocol_version
        self._timeout = 5
        self.connection = None

    def connect(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.settimeout(self._timeout)
        self.connection.connect((self.server_ip, self.server_port))

    def unpack_varint(self):
        value = 0
        position = 0
        
        while True:
            current_byte = self.connection.recv(1)
            value |= (ord(current_byte) & SEGMENT_BITS) << position
            
            if ord(current_byte) & CONTINUE_BIT == 0:
                break
            
            position += 7
            
            if position >= 32:
                raise RuntimeError("VarInt is too big")
        
        return value
    
    def unpack_varlong(self):
        value = 0
        position = 0
        
        while True:
            current_byte = self.connection.recv(1)
            value |= (ord(current_byte) & CONTINUE_BIT) << position
            
            if (ord(current_byte) & CONTINUE_BIT) == 0:
                break
            
            position += 7
            
            if position >= 64:
                raise RuntimeError("VarLong is too big")

    def pack_varint(self, value: int) -> bytes:
        data = b""
        
        while True:
            if (value & ~SEGMENT_BITS) == 0:
                data += struct.pack("B", value)
                return data

            data += struct.pack("B", (value & SEGMENT_BITS) | CONTINUE_BIT)
            
            value >>= 7
    
    def pack_unsigned_short(self, value) -> bytes:
        return struct.pack("H", value)
    
    def pack_string(self, value: str) -> bytes:
        value = value.encode("utf-8")
        return self.pack_varint(len(value)) + value

    def send_packet(self, packet_id, *fields) -> None:
        data = b""

        data += self.pack_varint(packet_id)
        
        for field in fields:
            data += field
            
        self.connection.send(self.pack_varint(len(data)) + data)
    
    def read(self) -> bytes:
        packet_length = self.unpack_varint()
        packet_id = self.unpack_varint()
        print(packet_length, packet_id)
        
        return self.connection.recv(packet_length)
