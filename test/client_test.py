import struct
import unittest
import mcauthpy

class DataTypesTest(unittest.TestCase):
    def test_pack_varint(self):
        c = mcauthpy.Client(None, None, None)
        
        self.assertEqual(c.pack_varint(0), b"\x00")
        self.assertEqual(c.pack_varint(1), b"\x01")
        self.assertEqual(c.pack_varint(2), b"\x02")
        self.assertEqual(c.pack_varint(127), b"\x7f")
        self.assertEqual(c.pack_varint(128), b"\x80\x01")
        self.assertEqual(c.pack_varint(255), b"\xff\x01")
        self.assertEqual(c.pack_varint(25565), b"\xdd\xc7\x01")
        self.assertEqual(c.pack_varint(2097151), b"\xff\xff\x7f")
        self.assertEqual(c.pack_varint(2147483647), b"\xff\xff\xff\xff\x07")
        # self.assertEqual(c.pack_varint(-1), b"\xff\xff\xff\xff\x0f")
        # self.assertEqual(c.pack_varint(-2147483648), b"\x80\x80\x80\x80\x08")

    def test_pack_varlong(self):
        c = mcauthpy.Client(None, None, None)
        
        self.assertEqual(c.pack_varlong(0), b"\x00")
        self.assertEqual(c.pack_varlong(1), b"\x01")
        self.assertEqual(c.pack_varlong(2), b"\x02")
        self.assertEqual(c.pack_varlong(127), b"\x7f")
        self.assertEqual(c.pack_varlong(128), b"\x80\x01")
        self.assertEqual(c.pack_varlong(255), b"\xff\x01")
        self.assertEqual(c.pack_varlong(2147483647), b"\xff\xff\xff\xff\x07")
        self.assertEqual(c.pack_varlong(9223372036854775807), b"\xff\xff\xff\xff\xff\xff\xff\xff\x7f")
        # self.assertEqual(c.pack_varlong(-1), b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01")
        # self.assertEqual(c.pack_varlong(-2147483648), b"\x80\x80\x80\x80\xf8\xff\xff\xff\x01")
        # self.assertEqual(c.pack_varlong(-9223372036854775808), b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01")

if __name__ == "__main__":
    unittest.main()