from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from ..utils import config
from .security import create_access_for_header, verify_and_read_jwt

router = APIRouter(prefix="/pix")


@router.post("/token")
async def login_for_access_token():
    access_token = create_access_for_header()
    return {"access_token": access_token, "token_type": "bearer"}


def authentication():
    """权限验证

    异常:
        JWTError: JWTError
        HTTPException: HTTPException
    """

    def inner(request: Request):
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        token = authorization.split()[1]
        try:
            payload = verify_and_read_jwt(token, config.data.secret_key)
            return payload
        except Exception as err:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(err)}
            )

    return Depends(inner)
