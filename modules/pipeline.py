import pathlib, logging
from modules.sources import fetch_all
from modules.writer import write_posts_and_site
from modules.notify import email_digest

def run_pipeline(cfg):
    pathlib.Path("data").mkdir(exist_ok=True)
    items = fetch_all(cfg)
    site_info = write_posts_and_site(cfg, items)
    email_digest(cfg, site_info)
    logging.info("Generated %d post(s).", len(site_info.get("posts", [])))
