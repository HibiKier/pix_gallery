from .config import KwType


def get_api(t: KwType) -> str:
    """返回接口api地址

    参数:
        t: KwType

    返回:
        str: api地址
    """
    hibiapi = "https://api.obfs.dev"
    if t == KwType.PID:
        return f"{hibiapi}/api/pixiv/illust"
    elif t == KwType.UID:
        return f"{hibiapi}/api/pixiv/member_illust"
    return f"{hibiapi}/api/pixiv/search"
