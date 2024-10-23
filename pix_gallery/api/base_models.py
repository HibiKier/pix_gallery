from typing import Generic, TypeVar

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
