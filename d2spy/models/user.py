from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID


@dataclass
class User:
    id: UUID
    email: str
    first_name: str
    last_name: str
    is_email_confirmed: bool
    is_approved: bool
    profile_url: Optional[str]
    api_access_token: Optional[str]
    exts: List

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data["id"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            is_email_confirmed=data["is_email_confirmed"],
            is_approved=data["is_approved"],
            profile_url=data["profile_url"],
            api_access_token=data["api_access_token"],
            exts=data["exts"],
        )
