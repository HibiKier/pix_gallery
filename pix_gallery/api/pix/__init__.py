from nonebot_plugin_uninfo import Uninfo
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Args,
    Match,
    Query,
    Option,
    Alconna,
    Arparma,
    on_alconna,
)

from zhenxun.services.log import logger
from zhenxun.utils.message import MessageUtils
from zhenxun.configs.utils import BaseBlock, RegisterConfig, PluginExtraData

from .data_source import PixManage

__plugin_meta__ = PluginMetadata(
    name="PIX",
    description="这里是PIX图库！",
    usage="""
    指令：
        pix ?*[tags]: 通过 tag 获取相似图片，不含tag时随机抽取
        
        示例：pix 萝莉 白丝
        示例：pix 萝莉 白丝 10  （10为数量）
        示例：pix #02      （当tag只有1个tag且为数字时，使用#标记，否则将被判定为数量）
    """.strip(),
    extra=PluginExtraData(
        author="HibiKier",
        version="0.1",
        superuser_help="""
        指令：
            pix -s ?*[tags]: 通过tag获取色图，不含tag时随机
            pix -r ?*[tags]: 通过tag获取r18图，不含tag时随机
        """,
        menu_type="来点好康的",
        limits=[BaseBlock(result="您有PIX图片正在处理，请稍等...")],
        configs=[
            RegisterConfig(
                key="MAX_ONCE_NUM2FORWARD",
                value=None,
                help="单次发送的图片数量达到指定值时转发为合并消息",
                default_value=None,
                type=int,
            ),
            RegisterConfig(
                key="ALLOW_GROUP_SETU",
                value=False,
                help="允许非超级用户使用-s参数",
                default_value=False,
                type=bool,
            ),
            RegisterConfig(
                key="ALLOW_GROUP_R18",
                value=False,
                help="允许非超级用户使用-r参数",
                default_value=False,
                type=bool,
            ),
        ],
    ).dict(),
)

# pix = on_command("pix", aliases={"PIX", "Pix"}, priority=5, block=True)

_matcher = on_alconna(
    Alconna(
        "pix",
        Args["tags?", str] / "\n",
        Option("-n|--num", Args["num", int]),
    ),
    priority=5,
    block=True,
)


@_matcher.handle()
async def _(
    session: Uninfo,
    arparma: Arparma,
    tags: Match[str],
    num: Query[int] = Query("num", 1),
):
    tags_list = tags.result.split() if tags.available else []
    result_list = await PixManage.get_pix(tags_list, num.result)
    logger.info(f"pix tags: {tags_list}", arparma.header_result, session=session)
    for result in result_list:
        if image := await PixManage.get_image(result):
            await MessageUtils.build_message(image).send()
        else:
            await MessageUtils.build_message(
                f"PID: {result.pid}_p{result.img_p}\n图片下载失败！"
            ).send()
