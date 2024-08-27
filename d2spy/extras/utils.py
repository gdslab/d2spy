import json
from http import HTTPStatus
from typing import Any, Dict, List, Union

from requests import Response


http_status_lookup = {status.value: status.name for status in list(HTTPStatus)}


def ensure_dict(
    response_data: Union[Dict[Any, Any], List[Dict[Any, Any]]]
) -> Dict[Any, Any]:
    """Verifies that the API response data is a dictionary before returning it.

    Args:
        response_data (Union[Dict[Any, Any], List[Dict[Any, Any]]]): API response data.

    Raises:
        Exception: Raised if the response data is not a dictionary.

    Returns:
        Dict[Any, Any]: Response data after verification.
    """
    if not isinstance(response_data, Dict):
        raise Exception("Response data must be type Dict[Any, Any]")
    return response_data


def ensure_list_of_dict(
    response_data: Union[Dict[Any, Any], List[Dict[Any, Any]]]
) -> List[Dict[Any, Any]]:
    """Verifies that the API response data is a list of dictionaries or
    empty list before returning it.

    Args:
        response_data (Union[Dict[Any, Any], List[Dict[Any, Any]]]): API response data.

    Raises:
        Exception: Raised if the response data is not a list of dicts or an empty list.

    Returns:
        Dict[Any, Any]: Response data after verification.
    """
    if (
        not isinstance(response_data, List)
        or len(response_data) > 0
        and not isinstance(response_data[0], Dict)
    ):
        raise Exception("Response data must be type List[Dict[Any, Any]]")
    return response_data


def pretty_print_response(response: Response):
    """Pretty prints an API response's status code and message.

    Args:
        response (Response): Response from an API request.
    """
    print(f"{response.status_code}: {http_status_lookup.get(response.status_code)}")
    print(json.dumps(response.json(), indent=4))
