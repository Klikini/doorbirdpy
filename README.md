# doorbirdpy
Python wrapper for the DoorBird LAN API v0.17

# Features

[DoorBird API Documentation](https://www.doorbird.com/downloads/api_lan.pdf?rev=0.17)

Note that no image data is handled by this wrapper; it only returns the URLs to access images and streams. It was designed this way so that the fetching of images could be handled by the client application and so that this library would not have so many dependencies.

## Supported

- Live video request
- Live image request
- Open door
- Light on
- History image request
- Notification request
- Check request
- Info request
- RTSP

## Not yet supported

- Monitor request
- Live audio transmit
- Live audio receive
- SIP
