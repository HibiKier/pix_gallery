import secrets
from pathlib import Path
from typing import Any, ClassVar

import httpx
import ujson as json
from httpx import Response
from loguru import logger

from ..config import ConfigModel, KwType


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


class AsyncHttpx:
    proxy: ClassVar[dict[str, str | None]] = {
        "http://": "http://127.0.0.1:7890",
        "https://": "http://127.0.0.1:7890",
    }

    @classmethod
    async def get(
        cls,
        url: str | list[str],
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        verify: bool = True,
        use_proxy: bool = True,
        proxy: dict[str, str] | None = None,
        timeout: int = 30,
        **kwargs,
    ) -> Response:
        """Get

        参数:
            url: url
            params: params
            headers: 请求头
            cookies: cookies
            verify: verify
            use_proxy: 使用默认代理
            proxy: 指定代理
            timeout: 超时时间
        """
        logger.debug(f"GET {url} {params}")
        urls = [url] if isinstance(url, str) else url
        return await cls._get_first_successful(
            urls,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            use_proxy=use_proxy,
            proxy=proxy,
            timeout=timeout,
            **kwargs,
        )

    @classmethod
    async def _get_first_successful(
        cls,
        urls: list[str],
        **kwargs,
    ) -> Response:
        last_exception = None
        for url in urls:
            try:
                return await cls._get_single(url, **kwargs)
            except Exception as e:
                last_exception = e
                if url != urls[-1]:
                    logger.warning(f"获取 {url} 失败, 尝试下一个")
        raise last_exception or Exception("All URLs failed")

    @classmethod
    async def _get_single(
        cls,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        verify: bool = True,
        use_proxy: bool = True,
        proxy: dict[str, str] | None = None,
        timeout: int = 30,
        **kwargs,
    ) -> Response:
        _proxy = proxy or (cls.proxy if use_proxy else None)
        async with httpx.AsyncClient(proxies=_proxy, verify=verify) as client:  # type: ignore
            return await client.get(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                **kwargs,
            )


class Config:
    def __init__(self) -> None:
        self.file = Path() / "config.json"
        if self.file.exists():
            self.data = ConfigModel.parse_file(self.file)
            logger.info(f"成功加载配置: {self.data}")
        else:
            self.data = ConfigModel(
                db_url="", token="", secret_key=secrets.token_urlsafe(32)
            )
            self.save()
            logger.info("已生成配置文件...")

    def save(self):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data.dict(), f, ensure_ascii=False, indent=4)

    @property
    def db_url(self) -> str:
        return self.data.db_url

    @property
    def bookmarks(self) -> int:
        return self.data.bookmarks

    @property
    def token(self) -> str:
        return self.data.token

    @property
    def secret_key(self) -> str:
        return self.data.secret_key

    @property
    def limit_time(self) -> int:
        return self.data.limit_time


config = Config()
