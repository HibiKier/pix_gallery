from loguru import logger
from tortoise.functions import Count

from pix_gallery.api.base_models import Result
from pix_gallery.api.tag.models import TagItem
from pix_gallery.auth import auth_superuser
from pix_gallery.database.models.tag_stat import TagStat

from ...database.models.pix_gallery import PixGallery
from ...router import router


@router.get(
    "/tag_rank",
    dependencies=[auth_superuser()],
    description="tag统计",
)
async def _(num: int = 10):
    if num > 50:
        return Result.fail("查询数量不能大于50...")
    data_list = (
        await TagStat.annotate(n=Count("id"))
        .group_by("tag")
        .order_by("-n")
        .limit(num)
        .values_list("tag", "n")
    )
    result_list = [TagItem(tag=tag, num=n) for tag, n in data_list]
    return Result.ok(result_list)


@router.post(
    "/tag_split",
    dependencies=[auth_superuser()],
    description="tag分割",
)
async def _():
    logger.info("开始分割PID tag")
    pid_list = await TagStat.annotate().distinct().values_list("pid", flat=True)
    pix_list = await PixGallery.filter(pid__not_in=pid_list, img_p=0).values_list(
        "pid", "tags"
    )
    create_list = []
    for pid, tags in pix_list:
        for tag in tags.split(","):
            if s_tag := tag.strip():
                create_list.append(TagStat(pid=pid, tag=s_tag))
                logger.debug(f"tag stat 添加 pid: {pid} tag: {s_tag}")
    await TagStat.bulk_create(create_list, batch_size=1000)
    logger.info(f"分割PID tag完成，共添加 {len(create_list)} 条记录!")
