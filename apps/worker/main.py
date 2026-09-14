"""Worker placeholder. Production deployments can attach Celery/RQ here.
The deterministic generation script is intentionally usable without a queue."""
import time
if __name__ == "__main__":
    print("AdForge worker ready; use scripts/generate_storyclaw_ad.py for a run")
    while True: time.sleep(3600)
