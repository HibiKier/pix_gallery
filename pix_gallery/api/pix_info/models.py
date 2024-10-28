from pydantic import BaseModel

from ...config import KwHandleType, KwType


class QueryCount(BaseModel):
    tags: list[str] | None = []


class QuerySeek(BaseModel):
    seek_type: KwType | None = None


class ImageCount(BaseModel):
    count: int
    """总数量"""
    normal: int
    """普通数量"""
    r18: int
    """r18数量"""
    ai: int
    """ai数量"""


class KeywordItem(BaseModel):
    id: int
    """id"""
    content: str
    """关键词"""
    kw_type: KwType
    """关键词类型"""
    handle_type: KwHandleType
    """操作类型"""
    seek_count: int
    """搜索次数"""
