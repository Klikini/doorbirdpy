"""Main DoorBirdPy module."""
import httplib2
import json
import sys
from urllib.parse import urlencode


class DoorBird(object):
    """Represent a doorbell unit."""

    """
    Initializes the options for subsequent connections to the unit.
    
    :param ip: The IP address of the unit
    :param username: The username (with sufficient privileges) of the unit
    :param password: The password for the provided username
    """
    def __init__(self, ip, username, password):
        self._ip = ip
        self._credentials = username, password

        self._http = httplib2.Http()
        self._http.add_credentials(username, password)

    """
    Test the connection to the device.
    
    :returns: A tuple containing the ready status (True/False) and the HTTP 
    status code returned by the device or 0 for no status
    """
    def ready(self):
        url = self.__url("info.cgi", auth=False)
        response, content = self._http.request(url)
        try:
            body_text = content.decode(encoding='utf-8')
            body_json = json.loads(body_text)
            code = body_json["BHA"]["RETURNCODE"]
            return int(code) == 1, int(response["status"])
        except ValueError:
            return False, int(response["status"])

    """
    A multipart JPEG live video stream with the default resolution and
    compression as defined in the system configuration.
    
    :returns: The URL of the stream
    """
    @property
    def live_video_url(self):
        return self.__url("video.cgi")

    """
    A JPEG file with the default resolution and compression as 
    defined in the system configuration.
    
    :returns: The URL of the image
    """
    @property
    def live_image_url(self):
        return self.__url("image.cgi")

    """
    Energize the door opener/alarm output relay of the device.
    
    :returns: True if OK, False if not
    """
    def open_door(self, relay=1):
        url = self.__url("open-door.cgi", {
            "r": relay
        }, auth=False)
        response, content = self._http.request(url)
        return int(json.loads(content.decode('utf-8'))["BHA"]["RETURNCODE"]) == 1

    """
    Energize the light relay of the device.
    
    :returns: JSON
    """
    def turn_light_on(self):
        url = self.__url("light-on.cgi", auth=False)
        response, content = self._http.request(url)
        code = json.loads(content.decode('utf-8'))["BHA"]["RETURNCODE"]
        return int(code) == 1

    """
    A past image stored in the cloud.

    :param index: Index of the history images, where 1 is the latest 
    history image
    :returns: The URL of the image.
    """
    def history_image_url(self, index, event):
        return self.__url("history.cgi", {
            "index": index,
            "event": event
        })

    """
    Get notification settings.
    
    :returns: A list of dictionaries
    """
    def notifications(self):
        url = self.__url("notification.cgi", auth=False)
        response, content = self._http.request(url)
        return json.loads(content.decode('utf-8'))["BHA"]["NOTIFICATIONS"]

    """
    Reset notification settings.
    """
    def reset_notifications(self):
        url = self.__url("notification.cgi", {
            "reset": 1
        }, auth=False)
        response, content = self._http.request(url)
        return int(response["status"]) == 200

    """
    Subscribe an event notification.
    
    :param event: Event type (doorbell, motionsensor, dooropen)
    :param url: HTTP or HTTPS URL to call with GET command if the event occurs
    :param user: Basic or Digest authentication user for the HTTP URL
    :param password: Basic or Digest authentication password or the HTTP URL
    :param relaxation: Relaxation time in seconds, for concurrent events.
    :returns: True if OK, False if not
    """
    def subscribe_notification(self, event, url, user=None, password=None,
                               relaxation=None):
        params = {
            "url": url,
            "event": event,
            "subscribe": 1
        }

        if user:
            params["user"] = user

        if password:
            params["password"] = password

        if relaxation:
            params["relaxation"] = relaxation

        url = self.__url("notification.cgi", params, auth=False)
        response, content = self._http.request(url)
        return int(response["status"]) == 200

    """
    Disable an existing notification.
    
    :param event: Event type (doorbell, motionsensor, dooropen)
    :returns: True if OK, False if not
    """
    def disable_notification(self, event):
        url = self.__url("notification.cgi", {
            "event": event,
            "subscribe": 0
        }, auth=False)
        response, content = self._http.request(url)
        return int(response["status"]) == 200

    """
    The current state of the doorbell.
    
    :returns: True for pressed, False for idle
    """
    def doorbell_state(self):
        url = self.__url("monitor.cgi", {
            "check": "doorbell"
        }, auth=False)
        response, content = self._http.request(url)

        try:
            content = content.decode(sys.stdin.encoding)
            return int(content.split("=")[1]) == 1
        except IndexError:
            return False

    """
    The current state of the motion sensor.
    
    :returns: True for motion, False for idle
    """
    def motion_sensor_state(self):
        url = self.__url("monitor.cgi", {
            "check": "motionsensor"
        }, auth=False)
        response, content = self._http.request(url)

        try:
            content = content.decode(sys.stdin.encoding)
            return int(content.split("=")[1]) == 1
        except IndexError:
            return False

    """
    Some version information about the device.
    
    :returns: A dictionary of the device information:
    - FIRMWARE
    - BUILD_NUMBER
    - WIFI_MAC_ADDR (if the device is connected via WiFi)
    """
    def info(self):
        url = self.__url("info.cgi", auth=False)
        response, content = self._http.request(url)
        return json.loads(content.decode('utf-8'))["BHA"]["VERSION"][0]

    """
    Live video request over RTSP.
    
    :param http: Set to True to use RTSP over HTTP
    :returns: The URL for the MPEG H.264 live video stream
    """
    @property
    def rtsp_live_video_url(self, http=False):
        return self.__url("mpeg/media.amp", port=(8557 if http else 554))

    """
    The HTML5 viewer for interaction from other platforms.
    
    :returns: The URL of the viewer
    """
    @property
    def html5_viewer_url(self):
        return self.__url("view.html")

    """
    Create a URL for accessing the device.

    :param path: The endpoint to call
    :param args: A dictionary of query parameters
    :param port: The port to use (defaults to 80)
    :param auth: Set to False to remove the URL authentication
    :returns: The full URL
    """
    def __url(self, path, args=None, port=80, auth=True):
        query = urlencode(args) if args else ""

        if auth:
            template = "http://{}@{}:{}/bha-api/{}?{}"
            user = ":".join(self._credentials)
            return template.format(user, self._ip, port, path, query)
        else:
            template = "http://{}:{}/bha-api/{}?{}"
            return template.format(self._ip, port, path, query)
