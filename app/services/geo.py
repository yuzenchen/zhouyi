"""IP 地理位置查詢服務。使用 ip-api.com 免費 endpoint。"""
import logging

import httpx

from app.config import get_settings
from app.models.divination import GeoInfo

logger = logging.getLogger(__name__)


async def lookup_geo(ip: str) -> GeoInfo:
    """查詢 IP 對應的地理位置。失敗時回傳空 GeoInfo。"""
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.geo_api_url}{ip}")
        if resp.status_code == 200:
            data = resp.json()
            return GeoInfo(
                ip=ip,
                country=data.get("country", "") or "",
                region=data.get("regionName", "") or "",
                city=data.get("city", "") or "",
                timezone=data.get("timezone", "") or "",
                lat=data.get("lat"),
                lon=data.get("lon"),
            )
    except Exception as e:
        logger.warning("geo lookup failed for ip=%s: %s", ip, e)
    return GeoInfo(ip=ip)


def extract_client_ip(request) -> str:
    """從 FastAPI Request 物件取得真實 client IP。
    處理 Render 等反向代理會塞 X-Forwarded-For 的情況。"""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else ""
