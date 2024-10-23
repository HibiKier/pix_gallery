from nonebot_plugin_uninfo import Uninfo
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import Args, Alconna, Arparma, on_alconna

from zhenxun.services.log import logger
from zhenxun.utils.message import MessageUtils
from zhenxun.configs.utils import PluginExtraData

from loguru import logger

from ...config import KwHandleType
from .data_source import KeywordManage

__plugin_meta__ = PluginMetadata(
    name="PIX添加",
    description="PIX关键词/UID/PID添加管理",
    usage="""
    指令：
        pix添加 ['u', 'p', 'k', 'b'] [content]
            u: uid
            p: pid
            k: 关键词
            b: 黑名单pid
        示例:
            pix添加 u 123456789
            pix添加 p 123456789
            pix添加 k 真寻
    """.strip(),
    extra=PluginExtraData(
        author="HibiKier",
        superuser_help="""
        pix处理 ['a', 'f', 'i', 'b'] [id]
        """.strip(),
        version="0.1",
    ).dict(),
)


_add_matcher = on_alconna(
    Alconna(
        "pix添加",
        Args["add_type", ["u", "p", "k", "b"]]["content", str],
    ),
    priority=5,
    block=True,
)

_handle_matcher = on_alconna(
    Alconna(
        "pix处理",
        Args["handle_type", ["a", "f", "i", "b"]]["id", int],
    ),
    priority=5,
    block=True,
)


@_add_matcher.handle()
async def _(
    session: Uninfo,
    arparma: Arparma,
    add_type: str,
    content: str,
):
    if add_type == "b":
        result = await KeywordManage.add_black_pid(session.user.id, content)
    elif add_type == "u":
        result = await KeywordManage.add_uid(session.user.id, content)
    elif add_type == "p":
        result = await KeywordManage.add_pid(session.user.id, content)
    else:
        result = await KeywordManage.add_keyword(session.user.id, content)
    await MessageUtils.build_message(result).send()
    logger.info(f"PIX 添加结果: {result}", arparma.header_result, session=session)


@_handle_matcher.handle()
async def _(
    session: Uninfo,
    arparma: Arparma,
    handle_type: str,
    id: int,
):
    if handle_type == "b":
        result = await KeywordManage.handle_keyword(
            session.user.id, id, None, KwHandleType.BLACK
        )
    elif handle_type == "a":
        result = await KeywordManage.handle_keyword(
            session.user.id, id, None, KwHandleType.PASS
        )
    elif handle_type == "f":
        result = await KeywordManage.handle_keyword(
            session.user.id, id, None, KwHandleType.FAIL
        )
    else:
        result = await KeywordManage.handle_keyword(
            session.user.id, id, None, KwHandleType.IGNORE
        )
    await MessageUtils.build_message(result).send()
    logger.info(f"PIX 处理结果: {result}", arparma.header_result, session=session)