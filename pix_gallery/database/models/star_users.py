from tortoise import fields
from tortoise.models import Model


class StarUsers(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    user_id = fields.CharField(255, unique=True)
    """约束id"""
    pids = fields.TextField(default="")
    """pid"""
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    """创建时间"""

    class Meta:  # type: ignore
        table = "star_users"
        table_description = "用户收藏表"
