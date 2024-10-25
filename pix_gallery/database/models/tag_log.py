from tortoise import fields
from tortoise.models import Model


class TagLog(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    name = fields.CharField(255)
    """tag名称"""
    token = fields.CharField(255)
    """token"""
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    """创建时间"""

    class Meta:  # type: ignore
        table = "tag_log"
        table_description = "tag搜索记录表"
