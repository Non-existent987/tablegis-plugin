/**
 * TableGIS Core — 地理计算（C#）
 * MIT License · https://github.com/Non-existent987/tablegis-plugin
 *
 * Haversine 距离 + 方位角。本文件即 TableGIS Excel 版插件核心层的实现。
 */

using System;

namespace TableGis.Core
{
    /// <summary>
    /// 地理计算: Haversine 距离 + 方位角
    /// </summary>
    public static class GeoCalculator
    {
        private const double EARTH_RADIUS = 6371000; // 地球半径(米)

        /// <summary>
        /// Haversine 公式计算两点间距离(米)
        /// </summary>
        public static double CalculateDistance(double lon1, double lat1, double lon2, double lat2)
        {
            double dLat = ToRad(lat2 - lat1);
            double dLon = ToRad(lon2 - lon1);
            double a = Math.Sin(dLat / 2) * Math.Sin(dLat / 2) +
                       Math.Cos(ToRad(lat1)) * Math.Cos(ToRad(lat2)) *
                       Math.Sin(dLon / 2) * Math.Sin(dLon / 2);
            double c = 2 * Math.Atan2(Math.Sqrt(a), Math.Sqrt(1 - a));
            return EARTH_RADIUS * c;
        }

        /// <summary>
        /// 计算方位角(0-360度，正北为 0，顺时针)
        /// </summary>
        public static double CalculateAzimuth(double lon1, double lat1, double lon2, double lat2)
        {
            double lat1Rad = ToRad(lat1);
            double lat2Rad = ToRad(lat2);
            double dLonRad = ToRad(lon2 - lon1);

            double y = Math.Sin(dLonRad) * Math.Cos(lat2Rad);
            double x = Math.Cos(lat1Rad) * Math.Sin(lat2Rad) -
                       Math.Sin(lat1Rad) * Math.Cos(lat2Rad) * Math.Cos(dLonRad);

            double brng = ToDeg(Math.Atan2(y, x));
            return (brng + 360) % 360;
        }

        private static double ToRad(double deg) => deg * Math.PI / 180.0;
        private static double ToDeg(double rad) => rad * 180.0 / Math.PI;
    }
}
