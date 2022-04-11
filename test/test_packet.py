import mcauthpy
import unittest


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

        # pb = mcauthpy.PacketBuffer(b"\xff\xff\xff\xff\x0f")
        # self.assertEqual(-1, pb.unpack_varint())

        # pb = mcauthpy.PacketBuffer(b"\x80\x80\x80\x80\x08")
        # self.assertEqual(-2147483648, pb.unpack_varint())

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


if __name__ == "__main__":
    unittest.main()
