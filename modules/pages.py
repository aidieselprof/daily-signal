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
        data["kp_now"] = str(last[1]) if isinstance(last, list) and len(last) > 1 else ""
    except Exception as e:
        logging.warning("Kp fetch error: %s", e)
    try:
        txt = requests.get("https://services.swpc.noaa.gov/text/3-day-geomag-forecast.txt", timeout=25).text
        data["forecast_text"] = txt[:4000]
    except Exception as e:
        logging.warning("Geomag forecast error: %s", e)
    return {"slug":"aurora","title":"Aurora & Space Weather (Daily)","template":"page.html","context":{"kind":"aurora","aurora":data}}

def quakes_region_page(slug, title, bbox, days=7, minmag=3.0):
    minlat, maxlat, minlon, maxlon = bbox
    startdate = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    params = dict(format="geojson", starttime=startdate, minmagnitude=minmag,
                  minlatitude=minlat, maxlatitude=maxlat, minlongitude=minlon, maxlongitude=maxlon,
                  orderby="time")
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?" + urlencode(params)
    quakes=[]
    try:
        j = requests.get(url, timeout=25).json()
        for f in j.get("features", []):
            p = f.get("properties", {})
            quakes.append({"mag": p.get("mag"), "place": p.get("place"), "time": _utc(p.get("time")), "url": p.get("url")})
    except Exception as e:
        logging.warning("USGS region fetch error (%s): %s", slug, e)
    return {"slug":slug, "title":title, "template":"page.html", "context":{"kind":"quakes","region":title.split("—")[-1].strip(), "quakes": quakes}}

def resources_page(cfg):
    items = cfg.get("resources", [])
    if not items:
        items = [
            {"title":"Aurora Forecast Map", "url":"https://www.swpc.noaa.gov/products/aurora-30-minute-forecast", "note":"Official NOAA nowcast (free)"},
            {"title":"Emergency Quake Kit", "url":"https://www.amazon.com/dp/B0B5H7QK1F?tag=AFFID", "note":"Swap AFFID for your Amazon tag"},
            {"title":"Astronomy Picture of the Day Prints", "url":"https://apod.nasa.gov/apod/lib/about_apod.html", "note":"Learn about APOD (prints via credited sources)"},
            {"title":"Beginner’s Stargazing Book", "url":"https://www.amazon.com/dp/1615194799?tag=AFFID", "note":"Replace AFFID with your tag"},
            {"title":"USGS Latest Earthquakes", "url":"https://earthquake.usgs.gov/earthquakes/map/", "note":"Official live map"}
        ]
    return {"slug":"resources","title":"Resources (Affiliate-ready)","template":"page.html","context":{"kind":"resources","items":items}}

def build_all(cfg):
    pages = [aurora_page()]
    # Regions: BC, Alaska, California, Japan
    pages += [
        quakes_region_page("earthquakes-bc", "Earthquakes — British Columbia (Last 7 Days)", (48,62,-141,-114)),
        quakes_region_page("earthquakes-alaska", "Earthquakes — Alaska (Last 7 Days)", (51,72,-170,-129)),
        quakes_region_page("earthquakes-california", "Earthquakes — California (Last 7 Days)", (32,42,-125,-114)),
        quakes_region_page("earthquakes-japan", "Earthquakes — Japan (Last 7 Days)", (24,46,123,146)),
    ]
    pages.append(resources_page(cfg))
    return pages
