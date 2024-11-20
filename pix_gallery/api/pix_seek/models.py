from pydantic import BaseModel

from ...config import KwType, SeekType


class PostData(BaseModel):
    """post数据模型"""

    seek_type: SeekType | None = SeekType.ALL
    """搜索类型"""
    num: int | None = None
    """数量"""


class User(BaseModel):
    """用户模型"""

    id: int
    """uid"""
    name: str
    """用户名"""
    account: str
    """账号"""
    profile_image_urls: dict[str, str]
    """头像"""
    is_followed: bool | None = None
    """是否关注"""


class Tag(BaseModel):
    """标签模型"""

    name: str
    """标签名"""
    translated_name: str | None
    """翻译名称"""


class PidModel(BaseModel):
    """pid模型"""

    id: int
    """图片pid"""
    title: str
    """图片标题"""
    type: str
    """类型"""
    image_urls: dict[str, str]
    """图片链接"""
    user: User
    """用户模型"""
    tags: list[Tag]
    """标签列表"""
    create_date: str
    """创建时间"""
    page_count: int
    """页数"""
    width: int
    """宽度"""
    height: int
    """高度"""
    sanity_level: int
    """安全等级"""
    x_restrict: int
    """x等级"""
    meta_single_page: dict[str, str]
    """meta_single_page"""
    meta_pages: list[dict[str, dict[str, str]]] | None
    """meta_pages"""
    total_view: int
    """总浏览量"""
    total_bookmarks: int
    """总收藏量"""
    is_bookmarked: bool
    """是否收藏"""
    visible: bool
    """是否可见"""
    is_muted: bool
    """是否静音"""
    total_comments: int = 0
    """总评论数"""
    illust_ai_type: int
    """插画ai类型"""
    illust_book_style: int
    """插画书类型"""
    comment_access_control: int | None = None
    """评论访问控制"""

    @property
    def tags_text(self) -> str:
        tags = []
        if self.tags:
            for tag in self.tags:
                tags.append(tag.name)
                if tag.translated_name:
                    tags.append(tag.translated_name)
        return ",".join(tags)


class UidModel(BaseModel):
    """uid模型"""

    user: User
    """用户模型"""
    illusts: list[PidModel]
    """插画列表"""
    next_url: str | None
    """下一页链接"""


class KeywordModel(BaseModel):
    """关键词模型"""

    keyword: str
    """关键词"""
    illusts: list[PidModel]
    """插画列表"""
    next_url: str | None
    """下一页链接"""
    search_span_limit: int
    """搜索时间限制"""
    show_ai: bool
    """是否显示ai插画"""


class NoneModel(BaseModel):
    content: str
    """内容"""
    kw_type: KwType
    """关键词类型"""
    error: str
    """错误信息"""
