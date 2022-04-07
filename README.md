<div align="center">
    <h1>mcauthpy</h1>
    <p>Minecraft: Java Edition Protocol API that allows you to send packets to Mojang servers in Python.</p>
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">
    <img src="https://img.shields.io/badge/python-3-blue.svg?v=1" alt="Language">
    <img src="https://img.shields.io/github/issues/novialriptide/mcauthpy" alt="Issues">
    <img src="https://img.shields.io/github/stars/novialriptide/mcauthpy" alt="Stars">
    <img src="https://img.shields.io/github/license/novialriptide/mcauthpy" alt="License">
</div>

## Build From Source
1. Clone repo
2. Run `pip install .`

## Standard Usage (Last Updated: 4/7/2022)
Here's an example of sending a [Handshake](https://wiki.vg/Protocol#Handshake) packet
```python
import mcauthpy

client = mcauthpy.Client()
client.connect("localhost")
client.send_packet( # Send Handshake Packet
    0x00, # Packet ID
    c.pack_varint(758), # Protocol Version
    c.pack_string("localhost"), # Server Address
    c.pack_unsigned_short(25565), # Server Port
    c.pack_varint(1) # Next State (1 for Status)
)
```
