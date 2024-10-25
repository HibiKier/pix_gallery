from tortoise import fields
from tortoise.models import Model


class TokenConsole(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    ip = fields.CharField(255)
    """ip"""
    token = fields.CharField(255)
    """token"""
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    """创建时间"""

    class Meta:  # type: ignore
        table = "token_console"
        table_description = "token数据表"
