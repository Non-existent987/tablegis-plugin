# TableGIS Core — 开源地理计算算法核心

与 TableGIS 插件内部实现**完全一致**的通用地理计算算法。零依赖，MIT 授权，随便用。

> 这些是教科书级公式（Haversine、国内坐标系偏移、度分秒换算），本来就到处都有实现。放在这里是为了让在表格/脚本里处理经纬度的人少踩坑。
> **插件本体不在这里**，完整功能见官网 <https://www.tablegis.com>。

## 目录

```
core/
├── js/geo.js                     JavaScript（ESM，浏览器/Node/WPS 加载项通用）
├── csharp/GeoCalculator.cs       C# 距离与方位角
├── csharp/CoordinateConverter.cs C# 坐标转换
└── python/tablegis_geo.py        Python 版（含 pandas 向量化示例）
```

## 有什么

| 函数 | 说明 |
|---|---|
| `distance(lon1, lat1, lon2, lat2)` | Haversine 球面距离（米），地球半径 6371000 |
| `azimuth(lon1, lat1, lon2, lat2)` | 大圆初始方位角（0-360°，正北 0°，顺时针） |
| `wgs84ToGcj02(lng, lat)` / `gcj02ToWgs84` | GPS 原始坐标 ↔ 高德/腾讯坐标 |
| `gcj02ToBd09(lng, lat)` / `bd09ToGcj02` | 高德 ↔ 百度坐标 |
| `wgs84ToBd09(lng, lat)` / `bd09ToWgs84` | GPS ↔ 百度坐标 |
| `decToDms(value)` / `dmsToDec(text)` | 十进制 ↔ 度分秒 |

## 用法

### JavaScript

```javascript
import { distance, azimuth, wgs84ToGcj02 } from './core/js/geo.js';

distance(116.3975, 39.9087, 121.4737, 31.2304);  // 1068138.868（北京 → 上海，米）
azimuth(116.3975, 39.9087, 121.4737, 31.2304);   // 153.038361（东南方向）
wgs84ToGcj02(116.3975, 39.9087);                 // { lng: 116.40374357, lat: 39.91010350 }
```

### C\#

```csharp
using TableGis.Core;

double m  = GeoCalculator.CalculateDistance(116.3975, 39.9087, 121.4737, 31.2304);
double az = GeoCalculator.CalculateAzimuth(116.3975, 39.9087, 121.4737, 31.2304);
var (lng, lat) = CoordinateConverter.Wgs84ToGcj02(116.3975, 39.9087);
```

### Python

```python
from tablegis_geo import distance, azimuth, wgs84_to_gcj02

distance(116.3975, 39.9087, 121.4737, 31.2304)   # 1068138.868
wgs84_to_gcj02(116.3975, 39.9087)                # (116.40374357, 39.9101035)
```

三种语言实现结果一致（已互校）。

## 几个容易被忽略的坑

**1. 坐标系不统一是表格数据最大的坑。**
手机上 GPS 记的是 WGS84，高德抓的是 GCJ02，百度抓的是 BD09。混着算距离，误差能从几米到几百米。算之前先确认坐标是什么系——TableGIS 插件里做这一步是因为手工判断太容易出错。

**2. 境外坐标不做偏移。**
GCJ02 的加密偏移只在中国境内生效。`core` 里的实现按中国经纬度范围（`73.66 < lng < 135.05 && 3.86 < lat < 53.55`）判断，境外原样返回。

**3. GCJ02 → WGS84 是近似逆算。**
正向偏移没有解析逆函数，代码里用的是线性近似（精度约 1-2 米）。表格数据、基站工参这类场景完全够用；需要亚米级请改用迭代逼近。

**4. 方位角是「大圆初始方位角」。**
沿大圆走，方位角会一路变化。长距离（比如跨国）算出来的初始方位角和「看着地图量的角度」不一样，这是正常的。几百米到几公里范围内可视为恒定。

**5. 距离是球面距离，不是投影距离。**
Haversine 用的是球体模型（R=6371000），比椭球模型（WGS84 椭球）误差约 0.3%。做「最近站」「站间距」这类比较，误差可以忽略；做测量级成果请换 Vincenty 公式。

## 授权

MIT License。可商用、可修改、可分发，唯一要求是保留版权声明。
