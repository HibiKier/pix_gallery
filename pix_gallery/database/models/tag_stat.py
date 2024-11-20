from tortoise import fields
from tortoise.models import Model


class TagStat(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    pid = fields.CharField(255)
    """pid"""
    tag = fields.CharField(255)
    """tag名称"""
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    """创建时间"""

    class Meta:  # type: ignore
        table = "tag_stat"
        table_description = "tag分割表"
