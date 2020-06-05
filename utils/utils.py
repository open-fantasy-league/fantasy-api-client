import dataclasses
from uuid import UUID

import requests
import json
import time
import traceback


def rate_limited_retrying_request(url, sleep=1, max_tries=4):
    print(f"requesting url: {url}")
    tries = 0
    resp = None
    while resp is None:
        try:
            tries += 1
            resp = requests.get(url)
        except Exception:
            traceback.print_exc()
            sleep *= 4
            if tries > max_tries:
                raise Exception("Failed getting url {} after max tries {}".format(url, max_tries))
        finally:
            time.sleep(sleep)
    return resp.json()


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return obj.__dict__
        elif isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        # TODO datetime ser
        # Base class default() raises TypeError:
        return json.JSONEncoder.default(self, obj)


def simplified_str(name):
    return ''.join((c.lower()) for c in name if c.isalnum())
