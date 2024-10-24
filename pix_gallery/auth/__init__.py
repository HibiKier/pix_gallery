from fastapi import Depends, HTTPException, Request
from jose import JWTError

from ..utils import config


def authentication():
    """权限验证

    异常:
        JWTError: JWTError
        HTTPException: HTTPException
    """

    def inner(request: Request):
        try:
            authorization = request.headers.get("Authorization")
            if authorization != config.data.token:
                raise JWTError
        except JWTError:
            raise HTTPException(status_code=400, detail="权限不足")

    return Depends(inner)
