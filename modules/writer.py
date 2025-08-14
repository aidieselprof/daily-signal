import os, pathlib
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

SITE_DIR = "site"

def _slugify(s):
    import re
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+","-",s).strip("-")
    return s[:80]

def write_posts_and_site(cfg, items, extra_pages=None):
    pathlib.Path(SITE_DIR).mkdir(exist_ok=True)
    env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
    t_index = env.get_template("index.html")
    t_post  = env.get_template("post.html")
    t_rss   = env.get_template("rss.xml")

    # Render posts
    posts = []
    for it in items:
        slug = _slugify(it["title"] + "-" + it["source"])
        fname = f"{slug}.html"
        post = {
            "title": it["title"],
            "source": it["source"],
            "summary": it.get("summary",""),
            "image": it.get("image",""),
            "link": it.get("link",""),
            "license": it.get("license",""),
            "attribution": it.get("attribution",""),
            "slug": slug,
            "filename": fname,
            "created": datetime.utcnow().isoformat()+"Z",
        }
        posts.append(post)
        with open(os.path.join(SITE_DIR, fname), "w", encoding="utf-8") as f:
            f.write(t_post.render(site=cfg["site"], post=post, monetization=cfg.get("monetization",{})))

    posts.sort(key=lambda x: x["created"], reverse=True)

    # Render extra pages (aurora, quakes regions, resources)
    rendered_extra = []
    if extra_pages:
        t_page = env.get_template("page.html")
        for ep in extra_pages:
            fname = f"{ep['slug']}.html"
            html  = t_page.render(site=cfg["site"], page=ep, monetization=cfg.get("monetization",{}))
            with open(os.path.join(SITE_DIR, fname), "w", encoding="utf-8") as f:
                f.write(html)
            ep["filename"] = fname
            rendered_extra.append(ep)

    # Index and RSS
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(t_index.render(site=cfg["site"], posts=posts, monetization=cfg.get("monetization",{})))
    with open(os.path.join(SITE_DIR, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(t_rss.render(site=cfg["site"], posts=posts))

    # Basic legal pages
    legal = {
        "terms.html":   "<html><body><h1>Terms</h1><p>No warranties. Automated content.</p></body></html>",
        "privacy.html": "<html><body><h1>Privacy</h1><p>No personal data collected by the static pages.</p></body></html>",
    }
    for name, html in legal.items():
        with open(os.path.join(SITE_DIR, name), "w", encoding="utf-8") as f:
            f.write(html)

    # robots.txt + sitemap.xml
    base = cfg["site"]["base_url"].rstrip("/")
    with open(os.path.join(SITE_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"Sitemap: {base}/sitemap.xml\nUser-agent: *\nAllow: /\n")

    urls = ["index.html", "feed.xml", "terms.html", "privacy.html"] + [p["filename"] for p in posts]
    if rendered_extra:
        urls += [ep["filename"] for ep in rendered_extra]
    lastmod = datetime.utcnow().strftime("%Y-%m-%d")
    sm = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for u in urls:
        sm += [ "  <url>", f"    <loc>{base}/{u}</loc>", f"    <lastmod>{lastmod}</lastmod>", "  </url>" ]
    sm.append("</urlset>")
    with open(os.path.join(SITE_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm))

    return {"posts": posts, "extra_pages": rendered_extra}
