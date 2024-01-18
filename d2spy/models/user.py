from dataclasses import dataclass
from typing import Union
from uuid import UUID


@dataclass
class User:
    id: UUID
    email: str
    first_name: str
    last_name: str
    is_email_confirmed: bool
    is_approved: bool
    profile_url: Union[str, None]

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
        )
