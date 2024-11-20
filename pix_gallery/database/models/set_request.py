from tortoise import fields
from tortoise.models import Model

from ...config import KwHandleType, KwType


class SetRequest(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    pix_id = fields.CharField(255)
    """tag名称"""
    kw_type = fields.CharEnumField(KwType, description="关键词类型")
    """关键词类型"""
    block_level = fields.IntField(null=True)
    """block等级 1: 可看 2: 不可看"""
    nsfw_tag = fields.IntField(null=True)
    """nsfw标签,-1=未标记, 0=safe, 1=setu. 2=r18"""
    handle_type = fields.CharEnumField(KwHandleType, null=True, description="处理类型")
    """处理类型"""
    token = fields.CharField(255, null=True)
    """token"""
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    """创建时间"""

    class Meta:  # type: ignore
        table = "set_request"
        table_description = "修改请求表"
