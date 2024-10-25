from tortoise import fields
from tortoise.models import Model


class CallLog(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    ip = fields.CharField(255)
    """ip"""
    token = fields.CharField(255)
    """token"""
    tags = fields.CharField(255)
    """tags"""
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    """创建时间"""

    class Meta:  # type: ignore
        table = "call_log"
        table_description = "调用日志表"
