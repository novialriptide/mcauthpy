LOGIN_MODE = 0
PLAY_MODE = 1


def better_hex(number: int):
    return f"0x{str(hex(number)[2:].zfill(2)).upper()}"
