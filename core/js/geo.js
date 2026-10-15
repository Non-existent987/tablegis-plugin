/**
 * TableGIS Core — 表格地理计算算法核心（JavaScript）
 * MIT License · https://github.com/Non-existent987/tablegis-plugin
 *
 * 与 TableGIS 插件内部实现一致，可直接用于任何项目（Node / 浏览器 / WPS / Office 加载项）。
 * 无任何依赖。
 */

/* ============================================================
 * 距离与方位角
 * ============================================================ */

/** 地球平均半径（米），Haversine 公式标准取值 */
const EARTH_RADIUS = 6371000;

const toRad = (deg) => (deg * Math.PI) / 180;
const toDeg = (rad) => (rad * 180) / Math.PI;

/**
 * 两点间地表距离（Haversine 球面距离）
 * @param {number} lon1 经度1（十进制度，东经为正）
 * @param {number} lat1 纬度1（十进制度，北纬为正）
 * @param {number} lon2 经度2
 * @param {number} lat2 纬度2
 * @returns {number} 距离（米）
 */
export function distance(lon1, lat1, lon2, lat2) {
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return EARTH_RADIUS * c;
}

/**
 * 两点间大圆初始方位角
 * @returns {number} 方位角（度，0-360，正北为 0，顺时针）
 */
export function azimuth(lon1, lat1, lon2, lat2) {
  const lat1Rad = toRad(lat1);
  const lat2Rad = toRad(lat2);
  const dLonRad = toRad(lon2 - lon1);

  const y = Math.sin(dLonRad) * Math.cos(lat2Rad);
  const x =
    Math.cos(lat1Rad) * Math.sin(lat2Rad) -
    Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLonRad);

  const brng = toDeg(Math.atan2(y, x));
  return (brng + 360) % 360;
}

/* ============================================================
 * WGS84 / GCJ02 / BD09 坐标互转
 * Krasovsky 椭球：a = 6378245.0，ee = 0.00669342162296594323
 * ============================================================ */

const PI = 3.1415926535897932384626;
const A = 6378245.0;
const EE = 0.00669342162296594323;
const X_PI = (PI * 3000.0) / 180.0;

/** 是否在中国境外（境外不做偏移） */
function outOfChina(lng, lat) {
  return !(lng > 73.66 && lng < 135.05 && lat > 3.86 && lat < 53.55);
}

function transformLat(x, y) {
  let ret =
    -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x));
  ret += ((20.0 * Math.sin(6.0 * x * PI) + 20.0 * Math.sin(2.0 * x * PI)) * 2.0) / 3.0;
  ret += ((20.0 * Math.sin(y * PI) + 40.0 * Math.sin((y / 3.0) * PI)) * 2.0) / 3.0;
  ret += ((160.0 * Math.sin((y / 12.0) * PI) + 320 * Math.sin((y * PI) / 30.0)) * 2.0) / 3.0;
  return ret;
}

function transformLon(x, y) {
  let ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x));
  ret += ((20.0 * Math.sin(6.0 * x * PI) + 20.0 * Math.sin(2.0 * x * PI)) * 2.0) / 3.0;
  ret += ((20.0 * Math.sin(x * PI) + 40.0 * Math.sin((x / 3.0) * PI)) * 2.0) / 3.0;
  ret += ((150.0 * Math.sin((x / 12.0) * PI) + 300.0 * Math.sin((x / 30.0) * PI)) * 2.0) / 3.0;
  return ret;
}

/**
 * WGS84（GPS 原始坐标）→ GCJ02（高德、腾讯地图）
 * @returns {{lng:number, lat:number}}
 */
export function wgs84ToGcj02(lng, lat) {
  if (outOfChina(lng, lat)) return { lng, lat };

  let dLat = transformLat(lng - 105.0, lat - 35.0);
  let dLon = transformLon(lng - 105.0, lat - 35.0);
  const radLat = (lat / 180.0) * PI;
  let magic = Math.sin(radLat);
  magic = 1 - EE * magic * magic;
  const sqrtMagic = Math.sqrt(magic);

  dLat = (dLat * 180.0) / (((A * (1 - EE)) / (magic * sqrtMagic)) * PI);
  dLon = (dLon * 180.0) / ((A / sqrtMagic) * Math.cos(radLat) * PI);

  return { lng: lng + dLon, lat: lat + dLat };
}

/**
 * GCJ02 → WGS84（逆算，非迭代）
 * 精度约 1-2 米，表格数据够用；需要亚米级请用二分迭代版。
 */
export function gcj02ToWgs84(lng, lat) {
  if (outOfChina(lng, lat)) return { lng, lat };

  let dLat = transformLat(lng - 105.0, lat - 35.0);
  let dLon = transformLon(lng - 105.0, lat - 35.0);
  const radLat = (lat / 180.0) * PI;
  let magic = Math.sin(radLat);
  magic = 1 - EE * magic * magic;
  const sqrtMagic = Math.sqrt(magic);

  dLat = (dLat * 180.0) / (((A * (1 - EE)) / (magic * sqrtMagic)) * PI);
  dLon = (dLon * 180.0) / ((A / sqrtMagic) * Math.cos(radLat) * PI);

  return { lng: lng * 2 - (lng + dLon), lat: lat * 2 - (lat + dLat) };
}

/** GCJ02 → BD09（百度地图） */
export function gcj02ToBd09(lng, lat) {
  const z = Math.sqrt(lng * lng + lat * lat) + 0.00002 * Math.sin(lat * X_PI);
  const theta = Math.atan2(lat, lng) + 0.000003 * Math.cos(lng * X_PI);
  return { lng: z * Math.cos(theta) + 0.0065, lat: z * Math.sin(theta) + 0.006 };
}

/** BD09 → GCJ02 */
export function bd09ToGcj02(bdLng, bdLat) {
  const x = bdLng - 0.0065;
  const y = bdLat - 0.006;
  const z = Math.sqrt(x * x + y * y) - 0.00002 * Math.sin(y * X_PI);
  const theta = Math.atan2(y, x) - 0.000003 * Math.cos(x * X_PI);
  return { lng: z * Math.cos(theta), lat: z * Math.sin(theta) };
}

/** WGS84 → BD09 */
export function wgs84ToBd09(lng, lat) {
  const g = wgs84ToGcj02(lng, lat);
  return gcj02ToBd09(g.lng, g.lat);
}

/** BD09 → WGS84 */
export function bd09ToWgs84(lng, lat) {
  const g = bd09ToGcj02(lng, lat);
  return gcj02ToWgs84(g.lng, g.lat);
}

/* ============================================================
 * 度分秒互转
 * ============================================================ */

const pad2 = (n) => String(Math.floor(n)).padStart(2, '0');

/**
 * 十进制经纬度 → 度分秒字符串
 * @param {number} value 十进制度，负数表示南纬/西经
 * @param {number} [secondsDigits=0] 秒保留小数位
 * @returns {string} 例：116.3975 → "116°23′51″"，-33.5 → "S 33°30′00″"
 */
export function decToDms(value, secondsDigits = 0) {
  const sign = value < 0 ? -1 : 1;
  const abs = Math.abs(value);
  const deg = Math.floor(abs);
  const minFloat = (abs - deg) * 60;
  const min = Math.floor(minFloat);
  let sec = (minFloat - min) * 60;

  // 四舍五入后可能进位到 60 秒
  sec = Number(sec.toFixed(secondsDigits));
  let d = deg;
  let m = min;
  if (sec >= 60) {
    sec -= 60;
    m += 1;
  }
  if (m >= 60) {
    m -= 60;
    d += 1;
  }

  const secStr = secondsDigits > 0 ? sec.toFixed(secondsDigits) : pad2(sec);
  return `${sign < 0 ? '-' : ''}${d}°${pad2(m)}′${secStr}″`;
}

/**
 * 度分秒 → 十进制度
 * 支持写法：116°23′51″ / 116 23 51 / 116d23m51s / -116.5 / 116°23.5′
 * @param {string|number} input
 * @returns {number} 十进制度（无法解析返回 NaN）
 */
export function dmsToDec(input) {
  if (typeof input === 'number') return input;
  if (!input) return NaN;

  let str = String(input).trim();
  if (str === '') return NaN;

  // 纯数字直接返回
  if (/^-?\d+(\.\d+)?$/.test(str)) return parseFloat(str);

  // 半球前缀
  let sign = 1;
  const headMatch = str.match(/^([NSEWnsew])\s*/);
  if (headMatch) {
    const h = headMatch[1].toUpperCase();
    if (h === 'S' || h === 'W') sign = -1;
    str = str.slice(headMatch[0].length);
  }
  if (/^-/.test(str)) {
    sign = -1;
    str = str.replace(/^-/, '');
  }

  // 提取数字：兼容 ° ′ ″ d m s 空格 及全角符号
  const nums = str.match(/\d+(\.\d+)?/g);
  if (!nums || nums.length === 0) return NaN;

  const deg = parseFloat(nums[0]) || 0;
  const min = parseFloat(nums[1]) || 0;
  const sec = parseFloat(nums[2]) || 0;

  return sign * (deg + min / 60 + sec / 3600);
}
