import os, pathlib
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

SITE_DIR="site"

# Optional OG image generator
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = ImageDraw = ImageFont = None

def _slugify(s):
    import re
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+","-",s).strip("-")
    return s[:80]

def _make_og_image(title, outpath, site_title="Daily Signal"):
    if Image is None:  # Pillow not available
        return
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (11, 13, 16))  # #0b0d10
    d = ImageDraw.Draw(img)
    # border
    d.rectangle([30, 30, W-30, H-30], outline=(125, 211, 252), width=6)  # accent
    # fonts
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 64)
        font_site  = ImageFont.truetype("DejaVuSans.ttf", 28)
    except Exception:
        font_title = ImageFont.load_default()
        font_site  = ImageFont.load_default()
    # wrap title
    import textwrap
    lines = textwrap.wrap(title, width=24)
    y = 150
    for line in lines[:5]:
        d.text((80, y), line, font=font_title, fill=(232,234,237))
        y += 78
    d.text((80, H-100), site_title, font=font_site, fill=(154,160,166))
    img.save(outpath, "PNG")

def write_posts_and_site(cfg, items, extra_pages=None):
    pathlib.Path(SITE_DIR).mkdir(exist_ok=True)
    env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
    ti = env.get_template("index.html")
    tp = env.get_template("post.html")
    tr = env.get_template("rss.xml")

    posts=[]
    for it in items:
        slug = _slugify(it["title"]+"-"+it["source"])
        fname = f"{slug}.html"

        # Prepare image (fallback OG if missing)
        img_url = it.get("image","")
        if (not img_url) and (Image is not None):
            og_dir = os.path.join(SITE_DIR, "og")
            os.makedirs(og_dir, exist_ok=True)
            og_path = os.path.join(og_dir, f"{slug}.png")
            _make_og_image(it["title"], og_path, cfg["site"].get("title","Daily Signal"))
            img_url = f"og/{slug}.png"

        post = {
            "title": it["title"], "source": it["source"],
            "summary": it.get("summary",""), "image": img_url,
            "link": it.get("link",""), "license": it.get("license",""),
            "attribution": it.get("attribution",""),
            "slug": slug, "filename": fname,
            "created": datetime.utcnow().isoformat()+"Z"
        }
        posts.append(post)
        with open(os.path.join(SITE_DIR, fname),"w",encoding="utf-8") as f:
            f.write(tp.render(site=cfg["site"], post=post, monetization=cfg.get("monetization",{})))
    posts.sort(key=lambda x: x["created"], reverse=True)

    # Extra pages
    rendered_extra=[]
    if extra_pages:
        tpage = env.get_template("page.html")
        for ep in extra_pages:
            fname = f"{ep['slug']}.html"
            out = tpage.render(site=cfg["site"], page=ep, monetization=cfg.get("monetization",{}))
            with open(os.path.join(SITE_DIR, fname), "w", encoding="utf-8") as f:
                f.write(out)
            ep["filename"] = fname
            rendered_extra.append(ep)

    # index + feed
    with open(os.path.join(SITE_DIR, "index.html"),"w",encoding="utf-8") as f:
        f.write(ti.render(site=cfg["site"], posts=posts, monetization=cfg.get("monetization",{})))
    with open(os.path.join(SITE_DIR, "feed.xml"),"w",encoding="utf-8") as f:
        f.write(tr.render(site=cfg["site"], posts=posts))

    # legal
    for name,html in {
        "terms.html":"<html><body><h1>Terms</h1><p>No warranties. Automated content.</p></body></html>",
        "privacy.html":"<html><body><h1>Privacy</h1><p>No personal data collected by the static pages.</p></body></html>"
    }.items():
        with open(os.path.join(SITE_DIR,name),"w",encoding="utf-8") as f: f.write(html)

    # robots + sitemap
    base = cfg["site"]["base_url"].rstrip("/")
    with open(os.path.join(SITE_DIR,"robots.txt"),"w",encoding="utf-8") as f:
        f.write(f"Sitemap: {base}/sitemap.xml\nUser-agent: *\nAllow: /\n")
    urls = ["index.html","feed.xml","terms.html","privacy.html"]+[p["filename"] for p in posts]
    if rendered_extra:
        urls += [ep["filename"] for ep in rendered_extra]
    now = datetime.utcnow().strftime("%Y-%m-%d")
    sm = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>","<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"]
    for u in urls:
        sm += ["  <url>", f"    <loc>{base}/{u}</loc>", f"    <lastmod>{now}</lastmod>", "  </url>"]
    sm.append("</urlset>")
    with open(os.path.join(SITE_DIR,"sitemap.xml"),"w",encoding="utf-8") as f:
        f.write("\n".join(sm))

    return {"posts": posts, "extra_pages": rendered_extra}
