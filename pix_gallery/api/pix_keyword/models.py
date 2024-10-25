from pydantic import BaseModel

from ...config import KwHandleType, KwType


class PixAddData(BaseModel):
    content: str
    """内容"""
    add_type: KwType
    """添加类型"""


class PixHandleData(BaseModel):
    id: int
    """id"""
    handle_type: KwHandleType
    """操作类型"""
