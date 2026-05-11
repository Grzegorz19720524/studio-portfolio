import math

EARTH_RADIUS_KM = 6371.0
EARTH_RADIUS_MI = 3958.8


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return round(2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a)), 4)


def distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return round(haversine(lat1, lon1, lat2, lon2) * EARTH_RADIUS_MI / EARTH_RADIUS_KM, 4)


def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    return round((math.degrees(math.atan2(x, y)) + 360) % 360, 2)


def midpoint(lat1: float, lon1: float, lat2: float, lon2: float) -> tuple[float, float]:
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    bx = math.cos(lat2) * math.cos(dlon)
    by = math.cos(lat2) * math.sin(dlon)
    mid_lat = math.atan2(
        math.sin(lat1) + math.sin(lat2),
        math.sqrt((math.cos(lat1) + bx) ** 2 + by ** 2),
    )
    mid_lon = lon1 + math.atan2(by, math.cos(lat1) + bx)
    return round(math.degrees(mid_lat), 6), round(math.degrees(mid_lon), 6)


def is_valid_lat(lat: float) -> bool:
    return -90.0 <= lat <= 90.0


def is_valid_lon(lon: float) -> bool:
    return -180.0 <= lon <= 180.0


def is_valid_coords(lat: float, lon: float) -> bool:
    return is_valid_lat(lat) and is_valid_lon(lon)


def bbox(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    return min(lats), min(lons), max(lats), max(lons)


def point_in_bbox(lat: float, lon: float, box: tuple[float, float, float, float]) -> bool:
    min_lat, min_lon, max_lat, max_lon = box
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon


def km_to_miles(km: float) -> float:
    return round(km * EARTH_RADIUS_MI / EARTH_RADIUS_KM, 4)


def miles_to_km(miles: float) -> float:
    return round(miles * EARTH_RADIUS_KM / EARTH_RADIUS_MI, 4)


def decimal_to_dms(decimal: float) -> tuple[int, int, float]:
    degrees = int(decimal)
    minutes_full = abs(decimal - degrees) * 60
    minutes = int(minutes_full)
    seconds = round((minutes_full - minutes) * 60, 4)
    return degrees, minutes, seconds


def dms_to_decimal(degrees: int, minutes: int, seconds: float) -> float:
    return round(degrees + minutes / 60 + seconds / 3600, 6)


if __name__ == "__main__":
    warsaw = (52.2297, 21.0122)
    berlin = (52.5200, 13.4050)
    paris = (48.8566, 2.3522)
    london = (51.5074, -0.1278)

    print("haversine Warsaw-Berlin:  ", haversine(*warsaw, *berlin), "km")
    print("haversine Warsaw-Paris:   ", haversine(*warsaw, *paris), "km")
    print("haversine Warsaw-London:  ", haversine(*warsaw, *london), "km")

    print("\ndistance_miles Warsaw-Berlin:", distance_miles(*warsaw, *berlin), "mi")

    print("\nbearing Warsaw-Berlin:", bearing(*warsaw, *berlin), "deg")
    print("bearing Warsaw-Paris: ", bearing(*warsaw, *paris), "deg")

    mid = midpoint(*warsaw, *berlin)
    print("\nmidpoint Warsaw-Berlin:", mid)

    print("\nis_valid_coords(52.23, 21.01):", is_valid_coords(52.23, 21.01))
    print("is_valid_coords(91.0, 0.0):   ", is_valid_coords(91.0, 0.0))

    cities = [warsaw, berlin, paris, london]
    box = bbox(cities)
    print("\nbbox(cities):", box)
    print("point_in_bbox(warsaw, box):  ", point_in_bbox(*warsaw, box))
    print("point_in_bbox(0,0, box):     ", point_in_bbox(0, 0, box))

    print("\nkm_to_miles(100):  ", km_to_miles(100))
    print("miles_to_km(100):  ", miles_to_km(100))

    print("\ndecimal_to_dms(52.2297):", decimal_to_dms(52.2297))
    print("dms_to_decimal(52,13,46.92):", dms_to_decimal(52, 13, 46.92))
