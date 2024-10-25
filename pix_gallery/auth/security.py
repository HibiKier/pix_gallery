import secrets
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
    is_superuser: bool = False


def create_jwt(
    payload: Dict[str, str],
    secret_key: str,
    expire_seconds: timedelta,
    is_superuser: bool = False,
) -> str:
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + expire_seconds
    to_encode.update(
        JWTMeta(exp=expire, sub=JWT_SUBJECT, is_superuser=is_superuser).dict()
    )
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)


def generate_secure_token(length: int = 32) -> str:
    return secrets.token_hex(length)


def create_access_for_header(is_superuser: bool = False) -> str:
    return create_jwt(
        payload={"token": generate_secure_token()},
        secret_key=config.secret_key,
        expire_seconds=timedelta(seconds=EXPIRE_SECONDS),
        is_superuser=is_superuser,
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
