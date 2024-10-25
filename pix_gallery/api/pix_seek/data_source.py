import asyncio
import threading
from asyncio import Semaphore, Task
from copy import deepcopy
from typing import Literal

from loguru import logger
from tortoise.expressions import F
from tortoise.functions import Concat

from ...config import KwHandleType, KwType
from ...database.models.pix_gallery import PixGallery
from ...database.models.pix_keyword import PixKeyword
from ...utils import AsyncHttpx, get_api
from .models import KeywordModel, PidModel, UidModel


class PixSeekManage:
    @classmethod
    async def start_seek(
        cls,
        seek_type: Literal["u", "p", "k", "a"],
        num: int | None,
        only_not_update: bool = True,
    ) -> str:
        """获取关键词数据

        参数:
            seek_type: 搜索类型
            num: 数量
            only_not_update: 仅仅搜索未更新过的数据.

        返回:
            tuple[int, int]: 保存数量, 重复数据
        """
        query = PixKeyword.filter(handle_type=KwHandleType.PASS)
        if only_not_update:
            query = query.filter(seek_count=0)
        if seek_type == "u":
            query = query.filter(kw_type=KwType.UID)
        elif seek_type == "p":
            query = PixKeyword.filter(kw_type=KwType.PID)
        elif seek_type == "k":
            query = PixKeyword.filter(kw_type=KwType.KEYWORD)
        if num:
            query = query.annotate().order_by("-create_time").limit(num)
        data_list = await query.all()
        if not data_list:
            raise ValueError("没有需要收录的数据...")
        return await cls.seek(data_list)

    @classmethod
    async def __seek(
        cls, t: KwType, api: str, params: dict, semaphore: Semaphore
    ) -> PidModel | UidModel | KeywordModel:
        """搜索关键词

        参数:
            t: 关键词类型
            api: api
            params: 参数
            semaphore: 信号量
        """
        async with semaphore:
            logger.debug(f"访问API: {api}, 参数: {params}")
            res = await AsyncHttpx.get(api, params=params)
            if res.status_code != 200:
                logger.warning(
                    f"PIX搜索失败,api:{api},params:{params},httpCode: {res.status_code}"
                )
            if t == KwType.PID:
                model = PidModel(**res.json()["illust"])
            elif t == KwType.UID:
                model = UidModel(**res.json())
            elif t == KwType.KEYWORD:
                model = KeywordModel(**res.json())
            return model

    @classmethod
    async def get_exists_id(cls) -> list[str]:
        """获取已存在的pid以及img_P

        返回:
            list[str]: pid_img_p
        """
        return await PixGallery.annotate(t=Concat("pid", "_", F("img_p"))).values_list(
            "t", flat=True
        )  # type: ignore

    @classmethod
    async def seek(cls, data_list: list[PixKeyword]) -> str:
        """搜索关键词

        参数:
            data_list: 数据列表

        返回:
            tuple[int, int]: 保存数量, 重复数据
        """
        task_list = []
        semaphore = asyncio.Semaphore(10)
        for data in data_list:
            logger.debug(f"PIX开始收录 {data.kw_type}: {data.content}")
            if data.kw_type == KwType.PID:
                task_list.append(
                    asyncio.create_task(cls.seek_pid(data.content, semaphore))
                )
            elif data.kw_type == KwType.UID:
                task_list.append(
                    asyncio.create_task(cls.seek_uid(data.content, semaphore))
                )
            elif data.kw_type == KwType.KEYWORD:
                for page in range(1, 30):
                    logger.debug(
                        f"PIX开始收录 {data.kw_type}: {data.content} | page: {page}"
                    )
                    task_list.append(
                        asyncio.create_task(
                            cls.seek_keyword(data.content, page, semaphore)
                        )
                    )
        threading.Thread(target=cls.thread_func, args=[task_list, data_list]).start()
        return f"成功提交收录请求, 正在收录 {[p.content for p in data_list]}"

    @classmethod
    def thread_func(cls, task_list: list[Task], data_list: list[PixKeyword]):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(cls._run_to_db(task_list, data_list))
        loop.close()

    @classmethod
    async def _run_to_db(
        cls, task_list: list[Task], data_list: list[PixKeyword]
    ) -> tuple[int, int]:
        result = await asyncio.gather(*task_list)
        for data in data_list:
            data.seek_count += 1
        logger.debug(f"共收录: {len(data_list)} 条数据.")
        await PixKeyword.bulk_update(data_list, fields=["seek_count"])
        return await cls.data_to_db(result)

    @classmethod
    async def data_to_db(
        cls, data_list: list[KeywordModel | PidModel | UidModel]
    ) -> tuple[int, int]:
        """将数据保存到数据库

        参数:
            data_list: 数据列表

        返回:
            tuple[int, int]: 保存数量, 重复数据
        """
        model_list: list[PixGallery] = []
        for data in data_list:
            if isinstance(data, PidModel):
                model_list.extend(cls.pid2model(data))
            elif isinstance(data, UidModel):
                model_list.extend(cls.uid2model(data))
            elif isinstance(data, KeywordModel):
                model_list.extend(cls.keyword2model(data))
        exists = await cls.get_exists_id()
        model_list_s = []
        in_list = []
        exists_count = 0
        for model in model_list:
            k = f"{model.pid}_{model.img_p}"
            if model and k not in exists and k not in in_list:
                in_list.append(f"{model.pid}_{model.img_p}")
                model_list_s.append(model)
            else:
                logger.debug(f"pix收录已存在: {model.pid}_{model.img_p}...")
                exists_count += 1
        if model_list_s:
            logger.debug(f"pix收录保存数据数量: {len(model_list_s)}")
            await PixGallery.bulk_create(model_list_s, 10)
        return len(model_list_s), exists_count

    @classmethod
    def keyword2model(cls, model: KeywordModel) -> list[PixGallery]:
        data_list = []
        for illust in model.illusts:
            if illust.total_bookmarks >= 500:
                data_list.extend(cls.pid2model(illust))
            else:
                logger.debug(
                    f"pix PID: {illust.id} 收录收藏数不足: {illust.total_bookmarks}, 已跳过"
                )
        return data_list

    @classmethod
    def uid2model(cls, model: UidModel) -> list[PixGallery]:
        data_list = []
        for illust in model.illusts:
            if illust.total_bookmarks >= 500:
                data_list.extend(cls.pid2model(illust))
            else:
                logger.debug(
                    f"pix PID: {illust.id} 收录收藏数不足: {illust.total_bookmarks}, 已跳过"
                )
        return data_list

    @classmethod
    def pid2model(cls, model: PidModel, img_p: int = 0) -> list[PixGallery]:
        data_list = []
        data_json = model.dict()
        del data_json["id"]
        data_json["pid"] = model.id
        data_json["uid"] = model.user.id
        data_json["author"] = model.user.name
        data_json["tags"] = model.tags_text
        if "r18" in model.tags_text.lower() or "r-18" in model.tags_text.lower():
            data_json["nsfw_tag"] = 2
        else:
            data_json["nsfw_tag"] = 0
        data_json["is_ai"] = "ai," in model.tags_text.lower()
        data_json["img_p"] = img_p
        if model.meta_pages:
            for meta_page in model.meta_pages:
                copy_data = deepcopy(data_json)
                copy_data["img_p"] = img_p
                copy_data["image_urls"] = meta_page["image_urls"]
                img_p += 1
                logger.debug(f"pix收录: {copy_data}")
                data_list.append(PixGallery(**copy_data))
        else:
            data_json["img_p"] = img_p
            logger.debug(f"pix收录: {data_json}")
            data_list.append(PixGallery(**data_json))
        return data_list

    @classmethod
    async def seek_pid(cls, pid: str, semaphore: Semaphore) -> Task:
        api = get_api(KwType.PID)
        params = {"id": pid}
        return asyncio.create_task(cls.__seek(KwType.PID, api, params, semaphore))

    @classmethod
    async def seek_uid(cls, uid: str, semaphore: Semaphore) -> Task:
        api = get_api(KwType.UID)
        params = {"id": uid}
        return asyncio.create_task(cls.__seek(KwType.UID, api, params, semaphore))

    @classmethod
    async def seek_keyword(cls, keyword: str, page: int, semaphore: Semaphore) -> Task:
        api = get_api(KwType.KEYWORD)
        params = {"word": keyword, "page": page}
        return asyncio.create_task(cls.__seek(KwType.KEYWORD, api, params, semaphore))
