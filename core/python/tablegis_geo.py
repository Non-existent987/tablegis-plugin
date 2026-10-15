"""
TableGIS Core — 表格地理计算算法核心（Python）
MIT License · https://github.com/Non-existent987/tablegis-plugin

与 TableGIS 插件内部实现一致，零第三方依赖。
若表格数据量大，建议配合 pandas 向量化使用，见文末示例。
"""

import math
from typing import Union, Tuple

EARTH_RADIUS = 6371000  # 地球平均半径（米）

__all__ = [
    "distance",
    "azimuth",
    "dec_to_dms",
    "dms_to_dec",
    "wgs84_to_gcj02",
    "gcj02_to_wgs84",
    "gcj02_to_bd09",
    "bd09_to_gcj02",
    "wgs84_to_bd09",
    "bd09_to_wgs84",
]


# ============================================================
# 距离与方位角
# ============================================================

def distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """两点间地表距离（Haversine 球面距离），单位米。"""
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS * c


def azimuth(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """两点间大圆初始方位角，度（0-360，正北为 0，顺时针）。"""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    d_lon_rad = math.radians(lon2 - lon1)

    y = math.sin(d_lon_rad) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(d_lon_rad)

    return (math.degrees(math.atan2(y, x)) + 360) % 360


# ============================================================
# WGS84 / GCJ02 / BD09 坐标互转
# Krasovsky 椭球：a = 6378245.0，ee = 0.00669342162296594323
# ============================================================

_PI = 3.1415926535897932384626
_A = 6378245.0
_EE = 0.00669342162296594323
_X_PI = _PI * 3000.0 / 180.0


def _out_of_china(lng: float, lat: float) -> bool:
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)


def _transform_lat(x: float, y: float) -> float:
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * _PI) + 20.0 * math.sin(2.0 * x * _PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * _PI) + 40.0 * math.sin(y / 3.0 * _PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * _PI) + 320 * math.sin(y * _PI / 30.0)) * 2.0 / 3.0
    return ret


def _transform_lon(x: float, y: float) -> float:
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * _PI) + 20.0 * math.sin(2.0 * x * _PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * _PI) + 40.0 * math.sin(x / 3.0 * _PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * _PI) + 300.0 * math.sin(x / 30.0 * _PI)) * 2.0 / 3.0
    return ret


def wgs84_to_gcj02(lng: float, lat: float) -> Tuple[float, float]:
    """WGS84（GPS 原始坐标）→ GCJ02（高德、腾讯地图）。返回 (lng, lat)。"""
    if _out_of_china(lng, lat):
        return lng, lat

    d_lat = _transform_lat(lng - 105.0, lat - 35.0)
    d_lon = _transform_lon(lng - 105.0, lat - 35.0)
    rad_lat = lat / 180.0 * _PI
    magic = math.sin(rad_lat)
    magic = 1 - _EE * magic * magic
    sqrt_magic = math.sqrt(magic)

    d_lat = (d_lat * 180.0) / ((_A * (1 - _EE)) / (magic * sqrt_magic) * _PI)
    d_lon = (d_lon * 180.0) / (_A / sqrt_magic * math.cos(rad_lat) * _PI)

    return lng + d_lon, lat + d_lat


def gcj02_to_wgs84(lng: float, lat: float) -> Tuple[float, float]:
    """GCJ02 → WGS84（逆算，精度约 1-2 米）。"""
    if _out_of_china(lng, lat):
        return lng, lat

    d_lat = _transform_lat(lng - 105.0, lat - 35.0)
    d_lon = _transform_lon(lng - 105.0, lat - 35.0)
    rad_lat = lat / 180.0 * _PI
    magic = math.sin(rad_lat)
    magic = 1 - _EE * magic * magic
    sqrt_magic = math.sqrt(magic)

    d_lat = (d_lat * 180.0) / ((_A * (1 - _EE)) / (magic * sqrt_magic) * _PI)
    d_lon = (d_lon * 180.0) / (_A / sqrt_magic * math.cos(rad_lat) * _PI)

    return lng * 2 - (lng + d_lon), lat * 2 - (lat + d_lat)


def gcj02_to_bd09(lng: float, lat: float) -> Tuple[float, float]:
    """GCJ02 → BD09（百度地图）。"""
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * _X_PI)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * _X_PI)
    return z * math.cos(theta) + 0.0065, z * math.sin(theta) + 0.006


def bd09_to_gcj02(bd_lng: float, bd_lat: float) -> Tuple[float, float]:
    """BD09 → GCJ02。"""
    x = bd_lng - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * _X_PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * _X_PI)
    return z * math.cos(theta), z * math.sin(theta)


def wgs84_to_bd09(lng: float, lat: float) -> Tuple[float, float]:
    """WGS84 → BD09。"""
    g_lng, g_lat = wgs84_to_gcj02(lng, lat)
    return gcj02_to_bd09(g_lng, g_lat)


def bd09_to_wgs84(lng: float, lat: float) -> Tuple[float, float]:
    """BD09 → WGS84。"""
    g_lng, g_lat = bd09_to_gcj02(lng, lat)
    return gcj02_to_wgs84(g_lng, g_lat)


# ============================================================
# 度分秒互转
# ============================================================

def dec_to_dms(value: float, seconds_digits: int = 0) -> str:
    """
    十进制经纬度 → 度分秒字符串。
    116.3975 → "116°23′51″"；负数前加 -。
    """
    sign = -1 if value < 0 else 1
    abs_v = abs(value)
    deg = int(abs_v)
    min_float = (abs_v - deg) * 60
    minute = int(min_float)
    sec = round((min_float - minute) * 60, seconds_digits)

    if sec >= 60:
        sec -= 60
        minute += 1
    if minute >= 60:
        minute -= 60
        deg += 1

    sec_str = f"{sec:0{seconds_digits + 3}.{seconds_digits}f}" if seconds_digits > 0 else f"{int(sec):02d}"
    return f"{'-' if sign < 0 else ''}{deg}°{minute:02d}′{sec_str}″"


def dms_to_dec(text: Union[str, float]) -> float:
    """
    度分秒 → 十进制度。
    支持：116°23′51″ / 116 23 51 / 116d23m51s / -116.5 / S33°30′00″
    无法解析返回 float('nan')。
    """
    if isinstance(text, (int, float)):
        return float(text)
    if not text:
        return float("nan")

    s = str(text).strip()
    if not s:
        return float("nan")

    import re

    if re.fullmatch(r"-?\d+(\.\d+)?", s):
        return float(s)

    sign = 1.0
    head = re.match(r"^([NSEWnsew])\s*", s)
    if head:
        if head.group(1).upper() in ("S", "W"):
            sign = -1.0
        s = s[len(head.group(0)):]
    if s.startswith("-"):
        sign = -1.0
        s = s[1:]

    nums = re.findall(r"\d+(?:\.\d+)?", s)
    if not nums:
        return float("nan")

    deg = float(nums[0])
    minute = float(nums[1]) if len(nums) > 1 else 0.0
    sec = float(nums[2]) if len(nums) > 2 else 0.0
    return sign * (deg + minute / 60 + sec / 3600)


# ============================================================
# 示例
# ============================================================

if __name__ == "__main__":
    # 北京 → 上海
    d = distance(116.3975, 39.9087, 121.4737, 31.2304)
    az = azimuth(116.3975, 39.9087, 121.4737, 31.2304)
    print(f"北京 → 上海  距离 {d:,.0f} 米 | 方位角 {az:.2f}°")

    print("WGS84 → GCJ02:", wgs84_to_gcj02(116.3975, 39.9087))
    print("十进制 → 度分秒:", dec_to_dms(116.3975, 2), dec_to_dms(-33.5))

    # pandas 向量化用法（可选）：
    #
    # import pandas as pd
    # from tablegis_geo import distance
    # df = pd.read_excel("工参.xlsx")
    # df["距离"] = [
    #     distance(row.经度, row.纬度, 116.3975, 39.9087)
    #     for row in df.itertuples()
    # ]
    #
    # 数据量大时建议改用 numpy 向量化重写（原理相同）：
    # import numpy as np
    # def distance_vec(lon1, lat1, lon2, lat2):
    #     r = 6371000.0
    #     p1, p2 = np.radians(lat1), np.radians(lat2)
    #     dp = p2 - p1
    #     dl = np.radians(lon2 - lon1)
    #     a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    #     return r * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
