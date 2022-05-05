<div align="center">
    <h1>mcauthpy</h1>
    <p>Minecraft: Java Edition Protocol API that allows you to send packets to Mojang & Minecraft servers in Python.</p>
    <img src="https://img.shields.io/github/license/novialriptide/mcauthpy" alt="License">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">
    <img src="https://img.shields.io/pypi/v/mcauthpy" alt="PyPi Version">
    <img src="https://img.shields.io/pypi/dm/mcauthpy" alt="PyPi Downloads">
    <img src="https://img.shields.io/tokei/lines/github/novialriptide/mcauthpy" alt="Lines">
</div>

## Installation
```
pip install mcauthpy
```

## Build From Source
1. Clone repo
2. Run `pip install .`

## Standard Usage (Last Updated: 5/3/2022)
Here's an example of sending a [Handshake](https://wiki.vg/Protocol#Handshake) packet.
```python
import mcauthpy

client = mcauthpy.Client("email", "password")
client.connect("localhost")
client.send_packet( # Send Handshake Packet
    0x00, # Packet ID
    mcauthpy.pack_varint(758), # Protocol Version
    mcauthpy.pack_string("localhost"), # Server Address
    mcauthpy.pack_unsigned_short(25565), # Server Port
    mcauthpy.pack_varint(1) # Next State (1 for status)
)
```
Here's an example of receiving data from a connected server.
```python
import mcauthpy

client = mcauthpy.Client("email", "password")
client.connect("localhost")
client.login()

while True:
    packet_id, buffer = client.get_received_buffer()
    print(packet_id, buffer.data)
```

## Special Thanks
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
