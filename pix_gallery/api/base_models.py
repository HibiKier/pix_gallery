from typing import Any, Generic, TypeVar

from pydantic import BaseModel

RT = TypeVar("RT")


class Result(Generic[RT], BaseModel):
    """
    总体返回
    """

    suc: bool
    """调用状态"""
    code: int = 200
    """code"""
    info: str = "操作成功"
    """info"""
    warning: str | None = None
    """警告信息"""
    data: RT = None
    """返回数据"""

    @classmethod
    def warning_(cls, info: str, code: int = 200) -> "Result[RT]":
        return cls(suc=True, warning=info, code=code)

    @classmethod
    def fail(cls, info: str = "异常错误", code: int = 500) -> "Result[RT]":
        return cls(suc=False, info=info, code=code)

    @classmethod
    def ok(
        cls, data: Any = None, info: str = "操作成功", code: int = 200
    ) -> "Result[RT]":
        return cls(suc=True, info=info, code=code, data=data)
