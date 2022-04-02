import socket
import json
import time
import struct

class Client:
    def __init__(self, server_ip: str, server_port: int = 25565):
        self.server_ip = server_ip
        self.server_port = server_port
        self._timeout = 5
    
    def _unpack_varint(self, connection):
        data = 0
        for x in range(5):
            ordinal = connection.recv(1)
            print(ordinal)
            
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
    
    def _send_data(self, connection, *args):
        data = b""
        
        for arg in args:
            data += self._pack_data(arg)
        
        connection.send(self._pack_varint(len(data)) + data)
    
    def _read_fully(self, connection, extra_varint: bool = False):
        packet_length = self._unpack_varint(connection)
        packet_id = self._unpack_varint(connection)
        byte = b''

        if extra_varint:
            # Packet contained netty header offset for this
            if packet_id > packet_length:
                self._unpack_varint(connection)

            extra_length = self._unpack_varint(connection)

            while len(byte) < extra_length:
                byte += connection.recv(extra_length)

        else:
            byte = connection.recv(packet_length)

        return byte

    
    def get_status(self):
        """ Get the status response """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.settimeout(self._timeout)
            connection.connect((self.server_ip, self.server_port))

            # Send handshake + status request
            self._send_data(connection, b'\x00\x00', self.server_ip, self.server_port, b'\x01')
            self._send_data(connection, b'\x00')

            # Read response, offset for string length
            data = self._read_fully(connection, extra_varint=True)

            # Send and read unix time
            self._send_data(connection, b'\x01', time.time() * 1000)
            unix = self._read_fully(connection)

        # Load json and return
        response = json.loads(data.decode('utf8'))
        response['ping'] = int(time.time() * 1000) - struct.unpack('Q', unix)[0]

        return response