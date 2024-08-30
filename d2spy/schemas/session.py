from typing import Any, Dict

import requests


class D2SpySession(requests.Session):
    d2s_data: Dict[str, Any]
