from pydantic import BaseModel


class StarData(BaseModel):
    user_id: str
    """用户id"""
    pid: str
    """图片pid"""


class RankData(BaseModel):
    num: int = 10
    """数量"""
    nsfw: list[int] = [0, 1]
    """nsfw_tag"""


class Pix(BaseModel):
    pid: str
    uid: str
    author: str
    title: str
    sanity_level: int
    x_restrict: int
    total_view: int
    total_bookmarks: int
    nsfw_tag: int
    is_ai: bool
    url: str
    is_multiple: bool
    img_p: str
    tags: str
    star: int
