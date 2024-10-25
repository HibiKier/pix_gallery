import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWEInvalidAuth
from pydantic import BaseModel, ValidationError

from ..utils import config

JWT_SUBJECT: str = "access"
ALGORITHM: str = "HS256"
EXPIRE_SECONDS: int = 60 * 60 * 24 * 365


class JWTMeta(BaseModel):
    exp: datetime
    sub: str


def create_jwt(
    payload: Dict[str, str], secret_key: str, expire_seconds: timedelta
) -> str:
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + expire_seconds
    to_encode.update(JWTMeta(exp=expire, sub=JWT_SUBJECT).model_dump())
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)


def create_access_for_header() -> str:
    return create_jwt(
        payload={"token": str(uuid.uuid4())},
        secret_key=config.secret_key,
        expire_seconds=timedelta(seconds=EXPIRE_SECONDS),
    )


def verify_and_read_jwt(token: str, secret_key: str) -> Any:
    try:
        return jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise ValueError("Session(token) has expired.")
    except JWEInvalidAuth:
        raise ValueError("Invalid token.")
    except ValidationError:
        raise ValueError("Malformed payload in token.")
    except Exception as err:
        raise ValueError(f"Unknown error: {err}")
