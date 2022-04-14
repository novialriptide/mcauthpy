<div align="center">
    <h1>mcauthpy</h1>
    <p>Envoyer Minecraft paquets à le Minecraft ou Mojang serveurs en Python</p>
    <img src="https://img.shields.io/github/license/novialriptide/mcauthpy" alt="License">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">
    <img src="https://img.shields.io/github/issues/novialriptide/mcauthpy" alt="Issues">
    <img src="https://img.shields.io/github/issues-pr/novialriptide/mcauthpy" alt="Pull Requests">
    <img src="https://img.shields.io/github/stars/novialriptide/mcauthpy" alt="Stars">
    <img src="https://img.shields.io/tokei/lines/github/novialriptide/mcauthpy" alt="Lines">
</div>

## Construire De Source
1. Cloner référentiel.
2. Exécuter `pip install .`

## Norme Usage (Dernier Mettre à Jour: 12/4/2022)
Voila un exemple d'envoyer une [Poignée De Main](https://wiki.vg/Protocol#Handshake) paquet.
```python
import mcauthpy

client = mcauthpy.Client()
client.connect("localhost")
client.send_packet( # Envoyer Poignée De Main Paquet
    0x00, # ID De Paquet
    mcauthpy.pack_varint(758), # Version Du Protocol
    mcauthpy.pack_string("localhost"), # Adresse Du Serveur
    mcauthpy.pack_unsigned_short(25565), # Port Du Serveur
    mcauthpy.pack_varint(1) # État d'Après (1 pour état)
)
```

<div align="center">
    <p>
        <a href="https://github.com/novialriptide/mcauthpy#readme">English</a>,
        <a href="https://github.com/novialriptide/mcauthpy/blob/main/.github/README.ko.md">한국말</a>,
        <a href="https://github.com/novialriptide/mcauthpy/blob/main/.github/README.fr.md">Français</a>
    </p>
    <p>Dernier Mettre à Jour: 4/12/2022, traduit par Novial</p>
</div>