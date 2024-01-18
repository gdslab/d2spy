import json
from http import HTTPStatus
from requests import Response


http_status_lookup = {status.value: status.name for status in list(HTTPStatus)}


def pretty_print_response(response: Response):
    print(f"{response.status_code}: {http_status_lookup.get(response.status_code)}")
    print(json.dumps(response.json(), indent=4))
