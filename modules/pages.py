import requests, logging
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

def _utc(ts_ms):
    try:
        return datetime.fromtimestamp(ts_ms/1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return ""

def aurora_page():
    data = {"kp_now": "", "forecast_text": "", "images": {
        "nh": "https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg",
        "sh": "https://services.swpc.noaa.gov/images/aurora-forecast-southern-hemisphere.jpg"
    }}
    try:
        j = requests.get("https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json", timeout=25).json()
        last = j[-1]
        # format is [time, Kp] in the public JSON
        data["kp_now"] = str(last[1]) if isinstance(last, list) and len(last) > 1 else ""
    except Exception as e:
        logging.warning("Kp fetch error: %s", e)
    try:
        txt = requests.get("https://services.swpc.noaa.gov/text/3-day-geomag-forecast.txt", timeout=25).text
        data["forecast_text"] = txt[:4000]
    except Exception as e:
        logging.warning("Geomag forecast error: %s", e)
    return {
        "slug": "aurora",
        "title": "Aurora & Space Weather (Daily)",
        "template": "page.html",
        "context": {"kind":"aurora", "aurora": data}
    }

def quakes_bc_page():
    # BC-ish bounding box; last 7 days, M>=3.0
    startdate = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    params = dict(format="geojson", starttime=startdate, minmagnitude=3,
                  minlatitude=48, maxlatitude=62, minlongitude=-141, maxlongitude=-114,
                  orderby="time")
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?" + urlencode(params)
    quakes = []
    try:
        j = requests.get(url, timeout=25).json()
        for f in j.get("features", []):
            p = f.get("properties", {})
            quakes.append({
                "mag": p.get("mag"),
                "place": p.get("place"),
                "time": _utc(p.get("time")),
                "url": p.get("url")
            })
    except Exception as e:
        logging.warning("USGS region fetch error: %s", e)
    return {
        "slug": "earthquakes-bc",
        "title": "Earthquakes — British Columbia (Last 7 Days)",
        "template": "page.html",
        "context": {"kind":"quakes", "region":"British Columbia", "quakes": quakes}
    }

def build_all(cfg):
    return [aurora_page(), quakes_bc_page()]
