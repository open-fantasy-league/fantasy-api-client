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
