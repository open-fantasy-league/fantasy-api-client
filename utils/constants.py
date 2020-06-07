# Necessary to strf datetimes into this format before sending to api
# TODO write a custom json serializer to use in websocket_client.py to serialize date-times on entry/exit
DATE_FMT = "%Y-%m-%dT%H:%M:%S%z"

# Logging
TRUNCATED_MESSAGE_LENGTH = 25