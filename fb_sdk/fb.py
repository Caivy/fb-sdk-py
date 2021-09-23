import hashlib
import hmac
import requests
import binascii
import base64
import requests
import json
import re
from urllib.parse import parse_qs, urlencode, urlparse

FACEBOOK_GRAPH_URL = "https://graph.facebook.com/"
FACEBOOK_WEB = "https://www.facebook.com/"
FACEBOOK_0AUTH = "dialog/oauth?"
VALID_API_VERSIONS = ["4.0", "5.0", "6.0", "7.0", "8.0", "9.0", "10.0", "11.0", "12.0"]
VALID_SEARCH_TYPES = ["place", "placetopic"]

class SDK(object):
    def __init__(self,
    access_token = None,
    timeout=None,
    version=None,
    proxies=None,
    session=None,
    app_secret=None
    ):
        default_version = VALID_API_VERSIONS[8]

        self.access_token = access_token
        self.timeout = timeout
        self.proxies = proxies
        self.session = session or requests.Session()
        self.app_secret_hmac = None

        if version:
            version_regex = re.compile(r"^\d\.\d{1,2}$")
            match = version_regex.search(str(version))
            if match is not None:
                if str(version) not in VALID_API_VERSIONS:
                    raise Facebook_SDK_Error(
                        "Valid API versions are "
                        + str(VALID_API_VERSIONS).strip("[]")
                    )
                else:
                    self.version = "v" + str(version)
            else:
                raise Facebook_SDK_Error(
                    "Version number should be in the"
                    " following format: #.# (e.g. 2.0)."
                )
        else:
            self.version = "v" + default_version  

        if app_secret and access_token:
            self.app_secret_hmac = hmac.new(
                app_secret.encode("ascii"),
                msg=access_token.encode("ascii"),
                digestmod=hashlib.sha256,
            ).hexdigest()

    def get_permissions(self, user_id):
        response = self.request(f"{self.version}/{user_id}/permissions"), {} ["data"] 
        return { x["permissions"]
        for x in response 
            if x["status"] == "grandted"
        }
    def get_object(self, id, **args):
        args["id"] = ",".join(id)
        
        return self.request(self.version + ",", args)
    def get_connections(self, id, connection_name, **args):
        return self.request(
            f"{self.version}/{id}/{connection_name}", args
        )
    def put_object(self, parent_object, connections_name, **data):
        assert self.access_token
        return self.request(f"{self.version}/{parent_object}/{connections_name}", post_args = data, method="POST")
    
    def put_message(self, parent_object, connections_name, user_id, message):
        url = f"{FACEBOOK_GRAPH_URL}/{self.version}/{parent_object}/{connections_name}?access_token={self.access_token}"
        param = {
        "messaging_type": "MESSAGE_TAG",
        "tag": "ACCOUNT_UPDATE", 
        "recipient":{
        "id": user_id
        },
        "message":{
        "text": message
        }
    }
        return requests.post(url, json=param)
    
    def request(
        self, path, args=None, post_args=None, files=None, method=None
    ):
        if args is None:
            args = dict()
        if post_args is not None:
            method = "POST"

        # Add `access_token` and app secret proof (`app_secret_hmac`) to
        # post_args or args if they exist and have not already been included.
        def _add_to_post_args_or_args(arg_name, arg_value):
            # If post_args exists, we assume that args either does not exists
            # or it does not need updating.
            if post_args and arg_name not in post_args:
                post_args[arg_name] = arg_value
            elif arg_name not in args:
                args[arg_name] = arg_value

        if self.access_token:
            _add_to_post_args_or_args("access_token", self.access_token)
        if self.app_secret_hmac:
            _add_to_post_args_or_args("appsecret_proof", self.app_secret_hmac)

        try:
            response = self.session.request(
                method or "GET",
                FACEBOOK_GRAPH_URL + path,
                timeout=self.timeout,
                params=args,
                data=post_args,
                proxies=self.proxies,
                files=files,
            )
        except requests.HTTPError as e:
            response = json.loads(e.read())
            raise Facebook_SDK_Error(response)

        headers = response.headers
        if "json" in headers["content-type"]:
            result = response.json()
        elif "image/" in headers["content-type"]:
            mimetype = headers["content-type"]
            result = {
                "data": response.content,
                "mime-type": mimetype,
                "url": response.url,
            }
        elif "access_token" in parse_qs(response.text):
            query_str = parse_qs(response.text)
            if "access_token" in query_str:
                result = {"access_token": query_str["access_token"][0]}
                if "expires" in query_str:
                    result["expires"] = query_str["expires"][0]
            else:
                raise Facebook_SDK_Error(response.json())
        else:
            raise Facebook_SDK_Error("Maintype was not text, image, or querystring")

        if result and isinstance(result, dict) and result.get("error"):
            raise Facebook_SDK_Error(result)
        return result



class SDK_Error(Exception):
    def __init__(self, result):
        self.result = result
        self.code = None
        self.error_subcode = None

        try:
            self.type = result["error_code"]
        except (KeyError, TypeError):
            self.type = ""

        # OAuth 2.0 Draft 10
        try:
            self.message = result["error_description"]
        except (KeyError, TypeError):
            # OAuth 2.0 Draft 00
            try:
                self.message = result["error"]["message"]
                self.code = result["error"].get("code")
                self.error_subcode = result["error"].get("error_subcode")
                if not self.type:
                    self.type = result["error"].get("type", "")
            except (KeyError, TypeError):
                # REST server style
                try:
                    self.message = result["error_msg"]
                except (KeyError, TypeError):
                    self.message = result

        Exception.__init__(self, self.message)
