from enum import Enum

import requests


BASE_URL = "https://api.jamendo.com/v3.0/"


# from https://developer.jamendo.com/v3.0/response-codes
class ErrCode(Enum):
    SUCCSESS = 0
    EXCEPTION = 1
    HTTP_METHOD = 2
    TYPE = 3
    REQUIRED_PARAM = 4
    INVALID_CLIENT_ID = 5
    RATE_LIMIT_EXCEEDED = 6
    METHOD_NOT_FOUND = 7
    NEEDED_PARAMETER = 8
    FORMAT = 9
    ENTRY_POINT = 10
    SUSPENDED_APPLICATION = 11
    ACCESS_TOKEN = 12
    INSUFFICIENT_SCOPE = 13
    INVALID_USER = 21
    EMAIL_ALREADY_EXIST = 22
    DUPLICATE_VALUE = 23
    INVALID_PLAYLIST = 24
    ACCESS_CODE = 101


class JamendoError(Exception):
    def __init__(self, code, msg):
        self.error_code = code
        self.error_msg = msg


class JamendoNetworkError(JamendoError):
    pass


class JamendoAPIError(JamendoError):
    pass


ARTISTS_PATH = "artists"
ARTISTS_FIELDS = {"id", "name", "website", "image"}

ALBUMS_PATH = "albums"
ALBUMS_FIELDS = {"id", "name", "artist_id", "artist_name", "image"}

TRACKS_PATH = "tracks"
TRACKS_FIELDS = {
    "id",
    "name",
    "duration",
    "position",
    "album_id",
    "album_name",
    "artist_id",
    "artist_name",
    "album_image",
    "audiodownload",
}


class JamendoAPI:
    def __init__(self, client_id, defaults={}):
        if not client_id or not isinstance(client_id, str):
            raise ValueError("'client_id' should be non-empty string")
        self.client_id = client_id
        if not isinstance(defaults, dict):
            raise ValueError("'defaults' should be dictionary")
        self.defaults = defaults

    def _do_request(self, func_path, params, fields):
        if not func_path or not isinstance(func_path, str):
            raise ValueError("'func_path' should be non-empty string")
        if not isinstance(params, dict):
            raise (ValueError("'params' should be dictionary"))
        if not isinstance(fields, set):
            raise (ValueError("'fields' should be set instance"))
        prms = {}
        prms.update(self.defaults)
        prms.update(params)
        prms["client_id"] = self.client_id
        r = requests.get(BASE_URL + func_path, prms)
        if r.status_code // 100 != 2:
            raise JamendoNetworkError(r.status_code, r.reason)
        headers = r.json()["headers"]
        err = headers["code"]
        if err:
            raise JamendoAPIError(err, headers["error_message"])
        res = []
        for elem in r.json()["results"]:
            res.append({key: val for key, val in elem.items() if key in fields})
        return res

    def search_artists(self, search_str, limit=0, offset=0):
        params = {"namesearch": search_str}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        return self._do_request(ARTISTS_PATH, params, ARTISTS_FIELDS)

    def search_albums(self, search_str="", limit=0, offset=0):
        params = {"namesearch": search_str}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        return self._do_request(ALBUMS_PATH, params, ALBUMS_FIELDS)

    def search_tracks(self, search_str="", limit=0, offset=0):
        params = {"namesearch": search_str}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        res = self._do_request(TRACKS_PATH, params, TRACKS_FIELDS)
        # check url for download track present
        return [r for r in res if r["audiodownload"]]

    def get_artist_albums(self, artist_id):
        params = {"artist_id": artist_id}
        return self._do_request(ALBUMS_PATH, params, ALBUMS_FIELDS)

    def get_album_tracks(self, album_id):
        params = {"album_id": album_id}
        return sorted(self._do_request(TRACKS_PATH, params, TRACKS_FIELDS), key=lambda x: x["position"])
