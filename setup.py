"""DoorBirdPy setup script."""
from setuptools import setup

setup(
    name="DoorBirdPy",
    version="0.1.2",
    author="Andy Castille",
    author_email="andy@robiotic.net",
    packages=["doorbirdpy"],
    install_requires="httplib2",
    url="https://github.com/Klikini/doorbirdpy",
    download_url="https://github.com/Klikini/doorbirdpy/archive/master.zip",
    license="MIT",
    description="Python wrapper for the DoorBird LAN API v0.17",
    platforms="Cross Platform"
)
