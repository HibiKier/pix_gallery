import asyncio
import io
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path

from fastapi.responses import StreamingResponse

from pix_gallery.config import KwHandleType, KwType
from pix_gallery.utils._build_image import BuildImage

from ...database.models.pix_gallery import PixGallery
from ...database.models.pix_keyword import PixKeyword
from ...router import router
from ...utils._image_template import ImageTemplate

stat_time = 0

file_path = Path() / "stat.png"


@router.get(
    "/stat",
    description="统计",
)
async def _():
    global stat_time
    if time.time() - stat_time < 60 * 60 and file_path.exists():
        result = BuildImage.open(file_path)
    else:
        uid_count = await PixKeyword.filter(
            kw_type=KwType.UID, handle_type=KwHandleType.PASS
        ).count()
        pid_count = await PixKeyword.filter(
            kw_type=KwType.PID, handle_type=KwHandleType.PASS
        ).count()
        keyword_count = await PixKeyword.filter(
            kw_type=KwType.KEYWORD, handle_type=KwHandleType.PASS
        ).count()
        result = await asyncio.gather(
            *[
                PixGallery.annotate().count(),
                PixGallery.filter(nsfw_tag__not=2).annotate().count(),
                PixGallery.filter(nsfw_tag=1).annotate().count(),
                PixGallery.filter(nsfw_tag=2).annotate().count(),
                PixGallery.filter(is_ai=True).annotate().count(),
            ]
        )
        now = str(datetime.now().replace(microsecond=0))
        data_list = [
            [
                uid_count,
                pid_count,
                keyword_count,
                "",
                result[0],
                result[1],
                result[2],
                result[3],
                result[4],
            ]
        ]
        result = await asyncio.to_thread(
            ImageTemplate.table_page,
            "PIX收录统计",
            f"截至: {now}",
            [
                "UID",
                "PID",
                "关键词",
                "丨",
                "图片总数",
                "普通",
                "色图(已标记)",
                "R18(已标记)",
                "AI",
            ],
            data_list,
        )
        result.save(file_path)
        stat_time = time.time()
    buf = BytesIO()
    result.markImg.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(io.BytesIO(buf.getvalue()), media_type="image/png")
