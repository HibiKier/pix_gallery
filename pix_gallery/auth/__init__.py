from time import time

from fastapi import Depends, HTTPException, Request, status
from loguru import logger

from ..database.models.token_console import TokenConsole
from ..router import router
from ..utils.utils import config
from .security import create_access_for_header, verify_and_read_jwt

ip_last_request_time = {}


@router.post("/token")
async def login_for_access_token(request: Request):
    access_token = create_access_for_header()
    ip = request.client.host if request.client else ""
    await TokenConsole.create(ip=ip, token=access_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "is_superuser": False,
    }


def init_superuser_token():
    return create_access_for_header(is_superuser=True)


def auth_superuser():
    """

    异常:
        JWTError: JWTError
        HTTPException: HTTPException
    """

    def inner(request: Request):
        authorization = request.headers.get("Authorization")

        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        token = authorization.split()[1]
        payload = verify_and_read_jwt(token, config.data.secret_key)
        # 检查是否超级用户
        if not payload.get("is_superuser", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superuser privileges required.",
            )

        return payload

    return Depends(inner)


def authentication(validate_token: bool = False):
    """

    异常:
        JWTError: JWTError
        HTTPException: HTTPException
    """

    def inner(request: Request):
        authorization_str = request.headers.get("Authorization")
        client_ip = request.client.host if request.client else ""
        current_time = time()
        logger.debug(f"client_ip: {client_ip}, token: {authorization_str}")
        if validate_token and not authorization_str:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        if authorization_str:
            token = authorization_str.split()[1]
            payload = verify_and_read_jwt(token, config.data.secret_key)
            return payload
        else:
            if client_ip in ip_last_request_time:
                last_request_time = ip_last_request_time[client_ip]
                if current_time - last_request_time < config.limit_time:
                    raise HTTPException(
                        status_code=429,
                        detail="Too Many Requests: Please wait 5 seconds.",
                    )

            ip_last_request_time[client_ip] = current_time
            return {"message": "Access without token, IP rate limited."}

    return Depends(inner)
