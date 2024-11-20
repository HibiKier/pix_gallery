from tortoise import fields
from tortoise.models import Model


class PidSearchLog(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    pid = fields.CharField(255)
    """pid"""
    ip = fields.CharField(255, null=True)
    """ip"""
    token = fields.CharField(255, null=True)
    """token"""
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    """创建时间"""

    class Meta:  # type: ignore
        table = "pid_search_log"
        table_description = "PID搜索记录表"
