import yaml
from datetime import datetime
from dateutil import tz

def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f: return yaml.safe_load(f)

def now_local(cfg):
    return datetime.now(tz.gettz(cfg["site"]["timezone"]))
