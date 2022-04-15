import mcauthpy
import unittest
import zlib

class PacketBufferTest(unittest.TestCase):
    def test_unpack_varint(self):
        pb = mcauthpy.PacketBuffer(b"\x00")
        self.assertEqual(0, pb.unpack_varint())

        pb = mcauthpy.PacketBuffer(b"\x01")
        self.assertEqual(1, pb.unpack_varint())

        pb = mcauthpy.PacketBuffer(b"\x02")
        self.assertEqual(2, pb.unpack_varint())

        pb = mcauthpy.PacketBuffer(b"\x7f")
        self.assertEqual(127, pb.unpack_varint())

        pb = mcauthpy.PacketBuffer(b"\x80\x01")
        self.assertEqual(128, pb.unpack_varint())

        pb = mcauthpy.PacketBuffer(b"\xff\x01")
        self.assertEqual(255, pb.unpack_varint())

        pb = mcauthpy.PacketBuffer(b"\xdd\xc7\x01")
        self.assertEqual(25565, pb.unpack_varint())

        pb = mcauthpy.PacketBuffer(b"\xff\xff\x7f")
        self.assertEqual(2097151, pb.unpack_varint())

        pb = mcauthpy.PacketBuffer(b"\xff\xff\xff\xff\x07")
        self.assertEqual(2147483647, pb.unpack_varint())

        pb = mcauthpy.PacketBuffer(b"\xff\xff\xff\xff\x0f")
        self.assertEqual(-1, pb.unpack_varint())

        pb = mcauthpy.PacketBuffer(b"\x80\x80\x80\x80\x08")
        self.assertEqual(-2147483648, pb.unpack_varint())

    def test_unpack_varlong(self):
        pb = mcauthpy.PacketBuffer(b"\x00")
        self.assertEqual(0, pb.unpack_varlong())

        pb = mcauthpy.PacketBuffer(b"\x01")
        self.assertEqual(1, pb.unpack_varlong())

        pb = mcauthpy.PacketBuffer(b"\x02")
        self.assertEqual(2, pb.unpack_varlong())

        pb = mcauthpy.PacketBuffer(b"\x7f")
        self.assertEqual(127, pb.unpack_varlong())

        pb = mcauthpy.PacketBuffer(b"\x80\x01")
        self.assertEqual(128, pb.unpack_varlong())

        pb = mcauthpy.PacketBuffer(b"\xff\x01")
        self.assertEqual(255, pb.unpack_varlong())

        pb = mcauthpy.PacketBuffer(b"\xdd\xc7\x01")
        self.assertEqual(25565, pb.unpack_varlong())

        pb = mcauthpy.PacketBuffer(b"\xff\xff\x7f")
        self.assertEqual(2097151, pb.unpack_varlong())

        pb = mcauthpy.PacketBuffer(b"\xff\xff\xff\xff\x07")
        self.assertEqual(2147483647, pb.unpack_varlong())

        pb = mcauthpy.PacketBuffer(b"\xff\xff\xff\xff\xff\xff\xff\xff\x7f")
        self.assertEqual(9223372036854775807, pb.unpack_varlong())

        # pb = mcauthpy.PacketBuffer(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01")
        # self.assertEqual(-1, pb.unpack_varlong())

        # pb = mcauthpy.PacketBuffer(b"\x80\x80\x80\x80\xf8\xff\xff\xff\x01")
        # self.assertEqual(-2147483648, pb.unpack_varlong())

        # pb = mcauthpy.PacketBuffer(b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01")
        # self.assertEqual(-9223372036854775808, pb.unpack_varlong())

    def test_read_packet1(self):
        pb = mcauthpy.PacketBuffer(b"\xff\xff\x7f")
        pb.add(b"\x7f")
        
        unpacked_varint = pb.unpack_varint()
        self.assertEqual(unpacked_varint, 2097151)
        self.assertEqual(pb.data, b"\x7f")

    def test_read_packet2(self):
        pb = mcauthpy.PacketBuffer(b"")
        pb.add(mcauthpy.pack_string("Novial"))
        pb.add(mcauthpy.pack_varint(4))
        pb.add(b"\x43\x23\x12")
        pb.add(mcauthpy.pack_string("Novial"))
        
        unpacked_string = pb.unpack_string().decode("utf-8")
        self.assertEqual(unpacked_string, "Novial")
        
        unpacked_string = pb.unpack_varint()
        self.assertEqual(unpacked_string, 4)
        
        unpacked_array = pb.unpack_byte_array(3)
        self.assertEqual(unpacked_array, b"\x43\x23\x12")
        
        unpacked_string = pb.unpack_string().decode("utf-8")
        self.assertEqual(unpacked_string, "Novial")

    def test_read_packet3(self):
        pb = mcauthpy.PacketBuffer(b"")
        pb.add(mcauthpy.pack_string("novialIsSuperCool"))

        self.assertEqual(pb.data, b"\x11novialIsSuperCool")

    def test_read_packet4(self):
        pb = mcauthpy.PacketBuffer(b"")
        pb.add(b"\xb6\x12")

        self.assertEqual(pb.unpack_varint(), b"\x11novialIsSuperCool")

    def test_read_entity_position_packet(self):
        pb = mcauthpy.PacketBuffer(b"\x00)\xdd\xa9\x0c\x00\x00\x01\xe6\x03\xde\x00")
        packet_length = len(pb.data)
        data_length = pb.unpack_varint()
        packet_id = pb.unpack_varint()
        entity_id = pb.unpack_varint()
        delta_x = pb.unpack_short()
        delta_y = pb.unpack_short()
        delta_z = pb.unpack_short()
        on_ground = pb.unpack_boolean()
    
    def test_read_chat_packet(self):
        pb = mcauthpy.PacketBuffer(b'\x81\x84\x82\xd2\x01\x00\x0f\xbd\x01{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"blue","text":"New version of Parties found: 3.2.4 (Current: 3.1.12)"}],"text":""}\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        packet_length = pb.unpack_varint()
        data_length = pb.unpack_varint()
        packet_id = pb.unpack_varint()
        json_data = pb.unpack_string()
        chat_pos = pb.unpack_varint()
        uuid = pb.unpack_uuid()

if __name__ == "__main__":
    unittest.main()
