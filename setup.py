"""DoorBirdPy setup script."""
from setuptools import setup

setup(
    name="DoorBirdPy",
    version="2.0.0",
    author="Andy Castille",
    author_email="andy@robiotic.net",
    packages=["doorbirdpy"],
    install_requires="httplib2",
    url="https://github.com/Klikini/doorbirdpy",
    download_url="https://github.com/Klikini/doorbirdpy/archive/master.zip",
    license="MIT",
    description="Python wrapper for the DoorBird LAN API v0.20",
    platforms="Cross Platform"
)
