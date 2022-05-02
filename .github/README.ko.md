<div align="center">
    <h1>mcauthpy</h1>
    <p>이 파일은 모장, 마인크래프트 서버로 패킷을 보낼수있는 기능을 갖추는 마인크래프트 자바 에디션 프로토콜 API 입니다.</p>
    <img src="https://img.shields.io/github/license/novialriptide/mcauthpy" alt="License">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">
    <img src="https://img.shields.io/github/issues/novialriptide/mcauthpy" alt="Issues">
    <img src="https://img.shields.io/github/issues-pr/novialriptide/mcauthpy" alt="Pull Requests">
    <img src="https://img.shields.io/github/stars/novialriptide/mcauthpy" alt="Stars">
    <img src="https://img.shields.io/tokei/lines/github/novialriptide/mcauthpy" alt="Lines">
</div>

## 설치
```
pip install mcauthpy
```

## 소스에서 빌드
1. 저장소 복제하다
2. `pip install .` 수행

## 사용하는 방법 (마지막 업데이트: 2022년 4월 16일)
[핸드셰이크](https://wiki.vg/Protocol#Handshake) 패킷 전송의 한 종류
```python
import mcauthpy

client = mcauthpy.Client("이름", "암호")
client.connect("localhost")
client.send_packet( # 핸드셰이크 패킷 보내다
    0x00, # 패킷 신분증
    mcauthpy.pack_varint(758), # 프로토콜 버전
    mcauthpy.pack_string("localhost"), # 서버 주소
    mcauthpy.pack_unsigned_short(25565), # 서버 포트
    mcauthpy.pack_varint(1) # 상태 (1 = 상태)
)
```
다음은 서버에서 데이터를 수신하는 예입니다.
```python
import mcauthpy

client = mcauthpy.Client("email", "password")
client.connect("localhost")
client.login_with_encryption()

while True:
    packet_id, buffer = client.get_received_buffer()
    print(packet_id, buffer.data)
```

## 덕분에
 - 문서에 대한 [wiki.vg](https://wiki.vg/)에 감사드립니다.
 - 번역을 위해 Ellen에게 감사합니다.

<div align="center">
    <p>
        <a href="https://github.com/novialriptide/mcauthpy#readme">English</a>,
        <a href="https://github.com/novialriptide/mcauthpy/blob/main/.github/README.ko.md">한국말</a>,
        <a href="https://github.com/novialriptide/mcauthpy/blob/main/.github/README.fr.md">Français</a>
    </p>
    <p>마지막 업데이트: 2022년 5월 2일, 노비알하고 Ellen 번역</p>
</div>