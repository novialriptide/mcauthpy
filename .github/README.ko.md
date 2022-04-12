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

## 소스에서 빌드
1. 저장소 복제하다
2. `pip install .` 수행

## 사용하는 방법 (마지막 업데이트: 2022년 4월 12일)
[핸드셰이크](https://wiki.vg/Protocol#Handshake) 패킷 전송의 예
```python
import mcauthpy

client = mcauthpy.Client()
client.connect("localhost")
client.send_packet( # 핸드셰이크 패킷 보내다
    0x00, # 패킷 신분증
    mcauthpy.pack_varint(758), # 프로토콜 버전
    mcauthpy.pack_string("localhost"), # 서버 주소
    mcauthpy.pack_unsigned_short(25565), # 서버 포트
    mcauthpy.pack_varint(1) # 상태 (1 = 상태)
)
```

<div align="center">
    <p>
        <a href="https://github.com/novialriptide/mcauthpy#readme">English</a>,
        <a href="https://github.com/novialriptide/mcauthpy/blob/main/.github/README.fr.MD">한국말</a>,
        <a href="https://github.com/novialriptide/mcauthpy/blob/main/.github/README.ko.md">Français</a>
    </p>
    <p>마지막 업데이트: 2022년 4월 12일</p>
</div>