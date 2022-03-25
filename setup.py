from distutils.core import setup

from mcauthpy.__version__ import VERSION

setup(
    name="mcauthpy",
    author="Andrew Hong",
    author_email="novialriptide@gmail.com",
    url="https://github.com/novialriptide/mcauthpy",
    packages=["mcauthpy"],
    version=str(VERSION),
)
