import time

from fastapi import APIRouter


router = APIRouter(prefix="/pix_seek")

@router.get(
    "/get_base_info",
    dependencies=[authentication()],
    response_model=Result[list[BaseInfo]],
    response_class=JSONResponse,
    description="基础信息",
)


@_matcher.handle()
async def _(
    session: Uninfo,
    arparma: Arparma,
    seek_type: Match[str],
    num: Match[int],
):
    st = seek_type.result if seek_type.available else "a"
    n = num.result if num.available else None
    try:
        start = time.time()
        result = await PixSeekManage.start_seek(st, n)  # type: ignore
        end = time.time()
        await MessageUtils.build_message(
            f"累计耗时: {int(end-start)} 秒\n共保存 {result[0]} 条数据!"
            f"\n已存在数据: {result[1]} 条!"
        ).send()
        logger.info(f"PIX 添加结果: {result}", arparma.header_result, session=session)
    except ValueError:
        await MessageUtils.build_message("没有需要收录的数据...").send()
