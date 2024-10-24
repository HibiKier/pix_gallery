from typing import Literal

from pydantic import BaseModel


class PixAddData(BaseModel):

    content: str
    """内容"""
    add_type: Literal["u", "k", "p", "b"]
    """添加类型"""


class PixHandleData(BaseModel):

    id: int
    """id"""
    handle_type: Literal["a", "f", "i", "b"]
    """操作类型"""
