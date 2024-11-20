from tortoise import fields
from tortoise.models import Model


class StarLog(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    pid = fields.CharField(255)
    """约束id"""
    is_star = fields.BooleanField()
    """是否为star操作"""
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    """创建时间"""

    class Meta:  # type: ignore
        table = "star_log"
        table_description = "用户收藏表"
