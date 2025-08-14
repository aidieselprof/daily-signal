import requests, logging, datetime

def nasa_apod():
    try:
        r = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY", timeout=25)
        if r.ok:
            j=r.json()
            return [{"source":"NASA APOD","title":j.get("title","NASA APOD"),"summary":j.get("explanation",""),"image":j.get("url",""),"link":"https://apod.nasa.gov/apod/astropix.html","license":"Public Domain (NASA)","attribution":"Image and text courtesy of NASA APOD"}]
    except Exception as e:
        logging.warning("NASA APOD error: %s", e)
    return []

def usgs_quakes():
    try:
        r=requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson", timeout=25)
        if r.ok:
            j=r.json(); out=[]
            for feat in j.get("features", [])[:10]:
                p=feat.get("properties",{})
                out.append({"source":"USGS","title":f"M{p.get('mag')} — {p.get('place')}","summary":p.get("title",""),"image":"","link":p.get("url",""),"license":"Public Domain (USGS)","attribution":"Data courtesy of USGS"})
            return out
    except Exception as e:
        logging.warning("USGS error: %s", e)
    return []

def noaa_space():
    try:
        r=requests.get("https://services.swpc.noaa.gov/products/summary/weekly.txt", timeout=25)
        if r.ok:
            text=r.text.strip(); head="\n".join(text.splitlines()[:40])
            return [{"source":"NOAA SWPC","title":"Space Weather Highlights","summary":head[:2000],"image":"","link":"https://www.swpc.noaa.gov/","license":"Public Domain (NOAA)","attribution":"Summary courtesy of NOAA SWPC"}]
    except Exception as e:
        logging.warning("NOAA error: %s", e)
    return []

def on_this_day():
    try:
        today=datetime.datetime.utcnow().strftime("%B_%d")
        url=f"https://en.wikipedia.org/api/rest_v1/page/summary/{today}"
        r=requests.get(url, timeout=25, headers={"User-Agent":"DailySignal/1.0 (contact: you@example.com)"})
        if r.ok:
            j=r.json(); title=j.get("title","On This Day"); desc=(j.get("extract","") or '')[:2000]; thumb=(j.get("thumbnail",{}) or {}).get("source","" ); page=(j.get("content_urls",{}).get("desktop",{}) or {}).get("page","")
            return [{"source":"Wikipedia","title":f"On This Day — {title}","summary":desc+"\n\nAttribution: Text from Wikipedia, licensed CC BY-SA 4.0.","image":thumb,"link":page,"license":"CC BY-SA 4.0","attribution":"Text from Wikipedia (CC BY-SA 4.0); link back included."}]
    except Exception as e:
        logging.warning("On-This-Day error: %s", e)
    return []

def fetch_all(cfg):
    items=[]; s=cfg.get("sources", {})
    if s.get("nasa_apod",True): items+=nasa_apod()
    if s.get("usgs_quakes",True): items+=usgs_quakes()
    if s.get("noaa_space",True): items+=noaa_space()
    if s.get("on_this_day",True): items+=on_this_day()
    return items
