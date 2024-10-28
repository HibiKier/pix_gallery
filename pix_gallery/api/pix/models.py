from typing import Literal

from pydantic import BaseModel


class PostData(BaseModel):
    tags: list[str] = []
    num: int = 1
    size: Literal["large", "medium", "original", "square_medium"] = "large"
    nsfw_tag: list[int] | None = []
    ai: bool | None = None
    r18: bool | None = None


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
