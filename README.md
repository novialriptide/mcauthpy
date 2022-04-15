<div align="center">
    <h1>mcauthpy</h1>
    <p>Minecraft: Java Edition Protocol API that allows you to send packets to Mojang & Minecraft servers in Python.</p>
    <img src="https://img.shields.io/github/license/novialriptide/mcauthpy" alt="License">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">
    <img src="https://img.shields.io/github/issues/novialriptide/mcauthpy" alt="Issues">
    <img src="https://img.shields.io/github/issues-pr/novialriptide/mcauthpy" alt="Pull Requests">
    <img src="https://img.shields.io/github/stars/novialriptide/mcauthpy" alt="Stars">
    <img src="https://img.shields.io/tokei/lines/github/novialriptide/mcauthpy" alt="Lines">
</div>

## Build From Source
1. Clone repo
2. Run `pip install .`

## Standard Usage (Last Updated: 4/12/2022)
Here's an example of sending a [Handshake](https://wiki.vg/Protocol#Handshake) packet.
```python
import mcauthpy

client = mcauthpy.Client()
client.connect("localhost")
client.send_packet( # Send Handshake Packet
    0x00, # Packet ID
    mcauthpy.pack_varint(758), # Protocol Version
    mcauthpy.pack_string("localhost"), # Server Address
    mcauthpy.pack_unsigned_short(25565), # Server Port
    mcauthpy.pack_varint(1) # Next State (1 for status)
)
```

## Special Thanks
 - [Bixilon](https://gitlab.bixilon.de/bixilon) and team for the [protocol data](https://gitlab.bixilon.de/bixilon/minosoft/-/raw/master/src/main/resources/assets/minosoft/mapping/versions.json)
 - [wiki.vg](https://wiki.vg/) team for the documentation on the Minecraft Protocol
 - Ellen for help on the Korean translations

<div align="center">
    <p>
        <a href="https://github.com/novialriptide/mcauthpy#readme">English</a>,
        <a href="https://github.com/novialriptide/mcauthpy/blob/main/.github/README.ko.md">한국말</a>,
        <a href="https://github.com/novialriptide/mcauthpy/blob/main/.github/README.fr.md">Français</a>
    </p>
    <p>Last Updated: 4/15/2022</p>
</div>
