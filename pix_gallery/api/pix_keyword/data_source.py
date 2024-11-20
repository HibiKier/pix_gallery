from loguru import logger

from pix_gallery.api.pix_seek.models import UidModel

from ...config import KwHandleType, KwType
from ...database.models.pix_gallery import PixGallery
from ...database.models.pix_keyword import PixKeyword
from ...utils.utils import AsyncHttpx, config, get_api


class KeywordManage:
    handle2cn = {
        "PASS": "通过",
        "IGNORE": "忽略",
        "FAIL": "未通过",
        "BLACK": "黑名单",
    }  # noqa: RUF012

    @classmethod
    async def add_keyword(
        cls, ip: str, keyword: list[str] | str, token: str | None
    ) -> str:
        """添加关键词

        参数:
            ip: ip
            keyword: 关键词
            token: token

        返回:
            str: 返回消息
        """
        return await cls.__add_content(ip, KwType.KEYWORD, keyword, token)

    @classmethod
    async def add_uid(cls, ip: str, uid: list[str] | str, token: str | None) -> str:
        """添加关键词

        参数:
            ip: ip
            uid: 用户uid
            token: token

        返回:
            str: 返回消息
        """
        if isinstance(uid, str):
            uid = [uid]
        allow_uid = []
        exist_uid = []
        error_uid = []
        for u in set(uid):
            u = u.strip()
            if await PixKeyword.exists(content=u, kw_type=KwType.UID):
                exist_uid.append(u)
                continue
            try:
                if result := await cls.__check_id_exists(u, KwType.UID):
                    error_uid.append(u)
                    continue
            except Exception as e:
                logger.error(f"检测uid失败: {u}, 错误信息: {type(e)}: {e}")
            allow_uid.append(u)
        result = await cls.__add_content(ip, KwType.UID, allow_uid, token)
        if exist_uid:
            result += f"\n当前UID: {','.join(exist_uid)}已收录图库中，请勿重复添加！"
        if error_uid:
            result += f"\n当前UID: {','.join(error_uid)}检测失败，请检查UID是否正确或稍后重试..."
        return result

    @classmethod
    async def add_pid(cls, ip: str, pid: list[str] | str, token: str | None) -> str:
        """添加关键词

        参数:
            ip: ip
            pid: 图片pid
            token: token

        返回:
            str: 返回消息
        """
        if isinstance(pid, str):
            pid = [pid]
        allow_pid = []
        exist_pid = []
        error_pid = []
        for p in set(pid):
            p = p.strip()
            if await PixKeyword.exists(content=p, kw_type=KwType.PID):
                exist_pid.append(p)
                continue
            try:
                if result := await cls.__check_id_exists(p, KwType.PID):
                    error_pid.append(p)
                    continue
            except Exception as e:
                logger.error(f"检测pid失败: {p}, 错误信息: {type(e)}: {e}")
            allow_pid.append(p)
        result = await cls.__add_content(ip, KwType.PID, allow_pid, token)
        if exist_pid:
            result += f"\n当前PID: {','.join(exist_pid)}已收录图库中，请勿重复添加！"
        if error_pid:
            result += f"\n当前PID: {','.join(error_pid)}检测失败，请检查PID是否正确或稍后重试..."
        return result

    @classmethod
    async def handle_keyword(
        cls,
        operator_id: str,
        id: int | None,
        kw_type: KwType | None,
        handle_type: KwHandleType,
        content: str | None = None,
        token: str | None = None,
    ) -> str:
        """处理关键词

        参数:
            operator_id: 操作ip
            keyword: 关键词
            kw_type: 关键词类型
            handle_type: 处理类型
            content: 内容
            token: token

        返回:
            str: 返回消息
        """
        if id:
            data = await PixKeyword.get_or_none(id=id, handle_type__isnull=True)
        else:
            data = await PixKeyword.get_or_none(
                content=content, kw_type=kw_type, handle_type__isnull=True
            )
        if not data:
            if handle_type == KwHandleType.BLACK and content:
                data = await PixKeyword.create(
                    content=content, kw_type=kw_type, ip=operator_id, token=token
                )
            else:
                return f"当前未处理的指定内容/id: {id or content} 不存在..."
        data.handle_type = handle_type
        data.operator_id = operator_id
        await data.save(update_fields=["handle_type", "operator_id"])
        if handle_type == KwHandleType.BLACK and content:
            if "-" in content:
                content_split = content.split("-")
                await PixGallery.filter(
                    pid=content_split[0], img_p=content_split[1]
                ).update(block_level=2)
            else:
                await PixGallery.filter(pid=content).update(block_level=2)
            logger.info(f"已将pid: {content}设置为黑名单!")
        return f"已成功将内容/id: {id or content}设置为{cls.handle2cn[handle_type]}!"

    @classmethod
    async def add_black_pid(cls, ip: str, pid: str, token: str | None) -> str:
        """添加黑名单pid

        参数:
            ip: ip
            pid: 图片pid
            token: token

        返回:
            str: 返回消息
        """
        return await cls.handle_keyword(
            ip, None, KwType.PID, KwHandleType.BLACK, pid, token
        )

    @classmethod
    async def __add_content(
        cls, ip: str, kw_type: KwType, content: list[str] | str, token: str | None
    ) -> str:
        """添加内容

        参数:
            ip: ip
            kw_type: 类型
            content: 内容
            token: token

        返回:
            str: 返回消息
        """
        if isinstance(content, str):
            content = [content]
        for c in content:
            data = await PixKeyword.get_or_none(content=c, kw_type=kw_type)
            if data:
                return f"当前content: {c}，{kw_type}已存在，状态: {cls.handle2cn[data.handle_type]}"
        pkd_list = []
        exists_content = await PixKeyword.filter(
            content__in=content, kw_type=kw_type
        ).values_list("content", flat=True)
        ignore_kw = []
        for c in content:
            c = c.strip()
            if c not in exists_content:
                handle_type = None
                operator_id = None
                if token == config.token:
                    logger.debug("超级用户token，直接通过...")
                    handle_type = KwHandleType.PASS
                    operator_id = ip
                pkd_list.append(
                    PixKeyword(
                        ip=ip,
                        content=c,
                        kw_type=kw_type,
                        token=token,
                        handle_type=handle_type,
                        operator_id=operator_id,
                    )
                )
            else:
                ignore_kw.append(c)
                logger.warning(f"关键词: {c} 已存在，跳过添加")
        result = f"已成功添加pix搜图{kw_type}: {content}!"
        if ignore_kw:
            result += "\n以下关键词已存在，跳过添加: " + ", ".join(ignore_kw)
        result += "\n请等待管理员通过该关键词！"
        if pkd_list:
            await PixKeyword.bulk_create(pkd_list, 10)
        return result

    @classmethod
    async def __check_id_exists(cls, id: str, type: KwType) -> str:
        """检查uid/pid是否存在

        参数:
            id: pid/uid
            type: pid/uid

        返回:
            bool: 是否存在
        """
        api = get_api(type)  # type: ignore
        res = await AsyncHttpx.get(api, params={"id": id})
        res.raise_for_status()
        data = res.json()
        if er := data.get("error"):
            return er.get("user_message") or er.get("message")
        if type == KwType.UID:
            model = UidModel(**data)
            if model == 0 or not model.illusts:
                return "uid不存在或uid作品为空..."
        return ""
