import struct

SEGMENT_BITS = 0x7F
CONTINUE_BIT = 0x80

def pack_boolean(value: bool) -> bytes:
    """Converts a boolean to a boolean in bytes format.

    Parameters:
        value (bool): Data to convert.

    Returns:
        bytes: Data in bytes format.

    """
    if value:
        return b"\x01"
    else:
        return b"\x00"

def pack_varint(value: int) -> bytes:
    """Converts a Python int to a Minecraft: Java Edition VarInt. Does not
    support negatives.

    Parameters:
        value (int): Data to convert.

    Returns:
        bytes: Data in Minecraft: Java Edition VarInt format.

    """
    data = b""

    if value < 0:
        value += 1 << 32

    while True:
        if (value & ~SEGMENT_BITS) == 0:
            data += struct.pack("B", value)
            return data

        data += struct.pack("B", (value & SEGMENT_BITS) | CONTINUE_BIT)

        value >>= 7

def pack_varlong(value: int) -> bytes:
    """Converts a Python int to a Minecraft: Java Edition VarLong. This
    function directly calls `pack_varint()`. Does not support negatives.

    Parameters:
        value (int): Data to convert.

    Returns:
        bytes: Data in Minecraft: Java Edition VarLong format.

    """
    if value < 0:
        raise Exception("pack_varlong() does not support negatives yet.")
    
    return pack_varint(value)

def pack_unsigned_short(value: int) -> bytes:
    """Converts a Python int to an Unsigned Short.
    Directly calls struct.pack("H", value).

    Returns:
        bytes: Data in Unsigned Short format.

    """
    return struct.pack("H", value)

def pack_string(value: str) -> bytes:
    """Converts a Python string to a Minecraft: Java Edition String.

    Returns:
        bytes: Data in Minecraft: Java Edition String format.

    """
    value = value.encode("utf-8")
    return pack_varint(len(value)) + value

def minecraft_sha1_hash(sha1_hash):
    return format(
        int.from_bytes(sha1_hash.digest(), byteorder="big", signed=True), "x"
    )