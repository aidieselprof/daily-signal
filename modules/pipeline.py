import pathlib, logging
from modules.config import load_config
from modules.sources import fetch_all
from modules.writer import write_posts_and_site
from modules.notify import email_digest
from modules import pages as extra_pages

def run_pipeline(cfg):
    pathlib.Path("data").mkdir(exist_ok=True)
    items = fetch_all(cfg)
    extra = extra_pages.build_all(cfg)
    site_info = write_posts_and_site(cfg, items, extra_pages=extra)
    email_digest(cfg, site_info)
    logging.info("Generated %d post(s) and %d extra page(s).", len(site_info.get("posts", [])), len(site_info.get("extra_pages", [])))
