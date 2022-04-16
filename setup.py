from setuptools import setup

setup(
    name="mcauthpy",
    author="Andrew Hong",
    author_email="novialriptide@gmail.com",
    url="https://github.com/novialriptide/mcauthpy",
    version="1.0.1",
    install_requires=[
        "pycryptodome>=3.14.1",
        "cryptography>=36.0.2",
    ],
    packages=["mcauthpy"],
)
