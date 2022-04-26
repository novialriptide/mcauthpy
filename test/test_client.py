import unittest
import mcauthpy
import hashlib


class DataTypesTest(unittest.TestCase):
    def test_pack_varint(self):
        self.assertEqual(mcauthpy.pack_varint(0), b"\x00")
        self.assertEqual(mcauthpy.pack_varint(1), b"\x01")
        self.assertEqual(mcauthpy.pack_varint(2), b"\x02")
        self.assertEqual(mcauthpy.pack_varint(127), b"\x7f")
        self.assertEqual(mcauthpy.pack_varint(128), b"\x80\x01")
        self.assertEqual(mcauthpy.pack_varint(255), b"\xff\x01")
        self.assertEqual(mcauthpy.pack_varint(25565), b"\xdd\xc7\x01")
        self.assertEqual(mcauthpy.pack_varint(2097151), b"\xff\xff\x7f")
        self.assertEqual(mcauthpy.pack_varint(2147483647), b"\xff\xff\xff\xff\x07")
        self.assertEqual(mcauthpy.pack_varint(-1), b"\xff\xff\xff\xff\x0f")
        self.assertEqual(mcauthpy.pack_varint(-2147483648), b"\x80\x80\x80\x80\x08")

    def test_pack_varlong(self):
        self.assertEqual(mcauthpy.pack_varlong(0), b"\x00")
        self.assertEqual(mcauthpy.pack_varlong(1), b"\x01")
        self.assertEqual(mcauthpy.pack_varlong(2), b"\x02")
        self.assertEqual(mcauthpy.pack_varlong(127), b"\x7f")
        self.assertEqual(mcauthpy.pack_varlong(128), b"\x80\x01")
        self.assertEqual(mcauthpy.pack_varlong(255), b"\xff\x01")
        self.assertEqual(mcauthpy.pack_varlong(2147483647), b"\xff\xff\xff\xff\x07")
        self.assertEqual(
            mcauthpy.pack_varlong(9223372036854775807),
            b"\xff\xff\xff\xff\xff\xff\xff\xff\x7f",
        )
        # self.assertEqual(mcauthpy.pack_varlong(-1), b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01")
        # self.assertEqual(mcauthpy.pack_varlong(-2147483648), b"\x80\x80\x80\x80\xf8\xff\xff\xff\x01")
        # self.assertEqual(mcauthpy.pack_varlong(-9223372036854775808), b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01")

    def test_sha1(self):
        self.assertEqual(
            mcauthpy.minecraft_sha1_hash(hashlib.sha1(b"Notch")),
            "4ed1f46bbe04bc756bcb17c0c7ce3e4632f06a48",
        )
        self.assertEqual(
            mcauthpy.minecraft_sha1_hash(hashlib.sha1(b"jeb_")),
            "-7c9d5b0044c130109a5d7b5fb5c317c02b4e28c1",
        )
        self.assertEqual(
            mcauthpy.minecraft_sha1_hash(hashlib.sha1(b"simon")),
            "88e16a1019277b15d58faf0541e11910eb756f6",
        )


if __name__ == "__main__":
    unittest.main()
