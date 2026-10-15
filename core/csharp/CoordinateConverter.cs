/**
 * TableGIS Core — 坐标转换（C#）
 * MIT License · https://github.com/Non-existent987/tablegis-plugin
 *
 * WGS84 / GCJ02 / BD09 互转。
 * Krasovsky 椭球参数: a=6378245.0, ee=0.00669342162296594323
 */

using System;

namespace TableGis.Core
{
    /// <summary>
    /// 坐标转换: WGS84/GCJ02/BD09 互转
    /// </summary>
    public static class CoordinateConverter
    {
        private const double PI = 3.1415926535897932384626;
        private const double A = 6378245.0;
        private const double EE = 0.00669342162296594323;
        private const double X_PI = PI * 3000.0 / 180.0;

        /// <summary>WGS84 → GCJ02 (高德坐标)</summary>
        public static (double lng, double lat) Wgs84ToGcj02(double lng, double lat)
        {
            if (OutOfChina(lng, lat)) return (lng, lat);

            double dLat = TransformLat(lng - 105.0, lat - 35.0);
            double dLon = TransformLon(lng - 105.0, lat - 35.0);
            double radLat = lat / 180.0 * PI;
            double magic = Math.Sin(radLat);
            magic = 1 - EE * magic * magic;
            double sqrtMagic = Math.Sqrt(magic);
            dLat = (dLat * 180.0) / ((A * (1 - EE)) / (magic * sqrtMagic) * PI);
            dLon = (dLon * 180.0) / (A / sqrtMagic * Math.Cos(radLat) * PI);
            return (lng + dLon, lat + dLat);
        }

        /// <summary>GCJ02 → WGS84 (粗略逆算，精度约 1-2 米)</summary>
        public static (double lng, double lat) Gcj02ToWgs84(double lng, double lat)
        {
            if (OutOfChina(lng, lat)) return (lng, lat);

            double dLat = TransformLat(lng - 105.0, lat - 35.0);
            double dLon = TransformLon(lng - 105.0, lat - 35.0);
            double radLat = lat / 180.0 * PI;
            double magic = Math.Sin(radLat);
            magic = 1 - EE * magic * magic;
            double sqrtMagic = Math.Sqrt(magic);
            dLat = (dLat * 180.0) / ((A * (1 - EE)) / (magic * sqrtMagic) * PI);
            dLon = (dLon * 180.0) / (A / sqrtMagic * Math.Cos(radLat) * PI);
            return (lng * 2 - (lng + dLon), lat * 2 - (lat + dLat));
        }

        /// <summary>GCJ02 → BD09 (百度坐标)</summary>
        public static (double lng, double lat) Gcj02ToBd09(double lng, double lat)
        {
            double z = Math.Sqrt(lng * lng + lat * lat) + 0.00002 * Math.Sin(lat * X_PI);
            double theta = Math.Atan2(lat, lng) + 0.000003 * Math.Cos(lng * X_PI);
            return (z * Math.Cos(theta) + 0.0065, z * Math.Sin(theta) + 0.006);
        }

        /// <summary>BD09 → GCJ02</summary>
        public static (double lng, double lat) Bd09ToGcj02(double bdLon, double bdLat)
        {
            double x = bdLon - 0.0065;
            double y = bdLat - 0.006;
            double z = Math.Sqrt(x * x + y * y) - 0.00002 * Math.Sin(y * X_PI);
            double theta = Math.Atan2(y, x) - 0.000003 * Math.Cos(x * X_PI);
            return (z * Math.Cos(theta), z * Math.Sin(theta));
        }

        /// <summary>WGS84 → BD09 (百度坐标)</summary>
        public static (double lng, double lat) Wgs84ToBd09(double lng, double lat)
        {
            var gcj = Wgs84ToGcj02(lng, lat);
            return Gcj02ToBd09(gcj.lng, gcj.lat);
        }

        /// <summary>BD09 → WGS84</summary>
        public static (double lng, double lat) Bd09ToWgs84(double lng, double lat)
        {
            var gcj = Bd09ToGcj02(lng, lat);
            return Gcj02ToWgs84(gcj.lng, gcj.lat);
        }

        /// <summary>判断坐标是否在中国境外</summary>
        private static bool OutOfChina(double lng, double lat)
        {
            return !(lng > 73.66 && lng < 135.05 && lat > 3.86 && lat < 53.55);
        }

        private static double TransformLat(double x, double y)
        {
            double ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.Sqrt(Math.Abs(x));
            ret += (20.0 * Math.Sin(6.0 * x * PI) + 20.0 * Math.Sin(2.0 * x * PI)) * 2.0 / 3.0;
            ret += (20.0 * Math.Sin(y * PI) + 40.0 * Math.Sin(y / 3.0 * PI)) * 2.0 / 3.0;
            ret += (160.0 * Math.Sin(y / 12.0 * PI) + 320 * Math.Sin(y * PI / 30.0)) * 2.0 / 3.0;
            return ret;
        }

        private static double TransformLon(double x, double y)
        {
            double ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.Sqrt(Math.Abs(x));
            ret += (20.0 * Math.Sin(6.0 * x * PI) + 20.0 * Math.Sin(2.0 * x * PI)) * 2.0 / 3.0;
            ret += (20.0 * Math.Sin(x * PI) + 40.0 * Math.Sin(x / 3.0 * PI)) * 2.0 / 3.0;
            ret += (150.0 * Math.Sin(x / 12.0 * PI) + 300.0 * Math.Sin(x / 30.0 * PI)) * 2.0 / 3.0;
            return ret;
        }
    }
}
