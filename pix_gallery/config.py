from pydantic import BaseModel
from strenum import StrEnum


class ConfigModel(BaseModel):

    db_url: str
    """数据库链接"""
    token: str
    """token"""
    secret_key: str
    """secret_key"""


class KwType(StrEnum):
    """关键词类型"""

    KEYWORD = "KEYWORD"
    """关键词"""
    UID = "UID"
    """用户uid"""
    PID = "PID"
    """图片pid"""


class KwHandleType(StrEnum):
    """关键词类型"""

    PASS = "PASS"
    """通过"""
    IGNORE = "IGNORE"
    """忽略"""
    FAIL = "FAIL"
    """未通过"""
    BLACK = "BLACK"
    """黑名单"""
