from pydantic import BaseModel

from pix_gallery.config import KwHandleType, KwType


class SetPixPost(BaseModel):
    id: str
    """pid"""
    type: KwType
    """kw_type"""
    block_level: int | None = None
    """block等级 1: 可看 2: 不可看"""
    nsfw_tag: int | None = None
    """nsfw标签,-1=未标记, 0=safe, 1=setu. 2=r18"""


class SetPixHandle(BaseModel):
    id: int
    """id"""
    handle_type: KwHandleType
    """处理类型"""
