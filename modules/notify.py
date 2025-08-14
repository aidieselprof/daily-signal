from email.mime.text import MIMEText
import smtplib

def email_digest(cfg, site_info):
    em=cfg.get("email",{})
    if not em.get("enabled",False): return
    base=cfg["site"]["base_url"].rstrip("/")
    lines=["New posts:"]
    for p in site_info.get("posts",[])[:5]:
        lines.append(f"- {p['title']} — {base}/{p['filename']}")
    msg=MIMEText("\n".join(lines),"plain","utf-8")
    msg["Subject"]=f"{cfg['site']['title']} — Daily Digest"; msg["From"]=em["from_addr"]; msg["To"]=em["to_addr"]
    with smtplib.SMTP(em["smtp_host"], em["smtp_port"]) as s:
        if em.get("use_tls",True): s.starttls()
        s.login(em["username"], em["app_password"]); s.send_message(msg)
