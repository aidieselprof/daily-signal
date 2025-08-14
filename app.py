import argparse, time, logging
from datetime import timedelta
from modules.config import load_config, now_local
from modules.pipeline import run_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main(loop=False):
    cfg = load_config()
    target_h, target_m = 7, 10
    if not loop:
        run_pipeline(cfg)
        return
    while True:
        now = now_local(cfg)
        if now.hour == target_h and now.minute >= target_m:
            run_pipeline(cfg)
            nextday = (now + timedelta(days=1)).replace(hour=target_h, minute=0, second=0, microsecond=0)
            time.sleep((nextday - now).total_seconds())
        else:
            time.sleep(60)

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--loop", action="store_true"); a=p.parse_args(); main(loop=a.loop)
