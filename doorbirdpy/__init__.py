"""Main DoorBirdPy module."""
import httplib2
import json
import sys
from urllib.parse import urlencode
from doorbirdpy.schedule_entry import DoorBirdScheduleEntry, DoorBirdScheduleEntryOutput, DoorBirdScheduleEntrySchedule


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
    
    :return: A tuple containing the ready status (True/False) and the HTTP 
    status code returned by the device or 0 for no status
    """
    def ready(self):
        url = self.__url("info.cgi", auth=False)
        response, content = self._http.request(url)
        try:
            data = self.__request(url)
            code = data["BHA"]["RETURNCODE"]
            return int(code) == 1, int(response["status"])
        except ValueError:
            return False, int(response["status"])

    """
    A multipart JPEG live video stream with the default resolution and
    compression as defined in the system configuration.
    
    :return: The URL of the stream
    """
    @property
    def live_video_url(self):
        return self.__url("video.cgi")

    """
    A JPEG file with the default resolution and compression as 
    defined in the system configuration.
    
    :return: The URL of the image
    """
    @property
    def live_image_url(self):
        return self.__url("image.cgi")

    """
    Energize a door opener/alarm output/etc relay of the device.
    
    :return: True if OK, False if not
    """
    def energize_relay(self, relay=1):
        data = self.__request(self.__url("open-door.cgi", {
            "r": relay
        }, auth=False))
        return int(data["BHA"]["RETURNCODE"]) == 1

    """
    Turn on the IR lights.
    
    :return: JSON
    """
    def turn_light_on(self):
        data = self.__request(self.__url("light-on.cgi", auth=False))
        code = data["BHA"]["RETURNCODE"]
        return int(code) == 1

    """
    A past image stored in the cloud.

    :param index: Index of the history images, where 1 is the latest 
    history image
    :return: The URL of the image.
    """
    def history_image_url(self, index, event):
        return self.__url("history.cgi", {
            "index": index,
            "event": event
        })

    """
    Get schedule settings.
    
    :return: A list of DoorBirdScheduleEntry objects
    """
    def schedule(self):
        data = self.__request(self.__url("schedule.cgi", auth=False))
        return DoorBirdScheduleEntry.parse_all(data)

    """
    Add or replace a schedule entry.
    
    :param entry: A DoorBirdScheduleEntry object to replace on the device
    :return: A tuple containing the success status (True/False) and the HTTP response code
    """
    def change_schedule(self, entry):
        url = self.__url("schedule.cgi", auth=False)
        response, content = self._http.request(url, "POST", json.dumps(entry.export),
                                               headers={"Content-Type": "application/json"})
        return int(response["status"]) == 200, response["status"]

    """
    Delete a schedule entry.
    
    :param event: Event type (doorbell, motion, rfid, input)
    :param param: param value of schedule entry to delete
    :return: True if OK, False if not
    """
    def delete_schedule(self, event, param=""):
        url = self.__url("schedule.cgi", {
            "action": "remove",
            "input": event,
            "param": param
        }, auth=False)
        response, content = self._http.request(url)
        return int(response["status"]) == 200

    """
    The current state of the doorbell.
    
    :return: True for pressed, False for idle
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
    
    :return: True for motion, False for idle
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
    Get information about the device.
    
    :return: A dictionary of the device information:
    - FIRMWARE
    - BUILD_NUMBER
    - WIFI_MAC_ADDR (if the device is connected via WiFi)
    - RELAYS list (if firmware version >= 000108) 
    - DEVICE-TYPE (if firmware version >= 000108)
    """
    def info(self):
        url = self.__url("info.cgi", auth=False)
        data = self.__request(url)
        return data["BHA"]["VERSION"][0]

    """
    Get all saved favorites.
    
    :return: dict, as defined by the API.
    Top level items will be the favorite types (http, sip),
    which each reference another dict that maps ID
    to a dict with title and value keys.
    """
    def favorites(self):
        return self.__request(self.__url("favorites.cgi", auth=False))

    """
    Add a new saved favorite or change an existing one.
    
    :param fav_type: sip or http
    :param title: Short description
    :param value: URL including protocol and credentials
    :param fav_id: The ID of the favorite, only used when editing existing favorites
    :return: successful, True or False
    """
    def change_favorite(self, fav_type, title, value, fav_id=None):
        args = {
            "action": "save",
            "type": fav_type,
            "title": title,
            "value": value
        }

        if fav_id:
            args["id"] = int(fav_id)

        url = self.__url("favorites.cgi", args, auth=False)
        response, content = self._http.request(url)
        return int(response["status"]) == 200

    """
    Delete a saved favorite.

    :param fav_type: sip or http
    :param fav_id: The ID of the favorite
    :return: successful, True or False
    """
    def delete_favorite(self, fav_type, fav_id):
        url = self.__url("favorites.cgi", {
            "action": "remove",
            "type": fav_type,
            "id": fav_id
        }, auth=False)

        response, content = self._http.request(url)
        return int(response["status"]) == 200

    """
    Live video request over RTSP.
    
    :param http: Set to True to use RTSP over HTTP
    :return: The URL for the MPEG H.264 live video stream
    """
    @property
    def rtsp_live_video_url(self, http=False):
        return self.__url("mpeg/media.amp", port=(8557 if http else 554))

    """
    The HTML5 viewer for interaction from other platforms.
    
    :return: The URL of the viewer
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
    :return: The full URL
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

    """
    Call a URL on the device.
    
    :param url: The full URL to the API call
    :return: The JSON-decoded data sent by the device
    """
    def __request(self, url):
        response, content = self._http.request(url)
        body_json = content.decode(encoding='utf-8')
        body_data = json.loads(body_json)
        return body_data
