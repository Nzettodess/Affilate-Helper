import argparse
import asyncio
import sys
import requests
import random
import time
import os
import logging
from concurrent.futures import ThreadPoolExecutor
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import aiohttp
from aiohttp import BasicAuth
import sys
from datetime import datetime   

sys.stdout.reconfigure(encoding='utf-8')

# Create logs folder if not exists
os.makedirs("logs", exist_ok=True)

# Log file name with timestamp
log_filename = datetime.now().strftime("Local Run/logs/run_%Y%m%d_%H%M%S.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)  # output to CMD
    ]
)

# Suppress asyncio SSLProtocol noisy errors
logging.getLogger('asyncio').setLevel(logging.CRITICAL)

# Fix for Windows compatibility with aiodns
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Config
STARTER_URL = "https://cikgumall.com/aff/4212"
PROXY_FILE_PATH = "data/input/proxies.txt"
LOG_FILE_PATH = "data/logs/valid_proxies_history.txt"
VISITS_PER_PROXY = 1  # Number of visits per valid proxy with different user-agents

TARGET_URLS = [
    "https://cikgumall.com/product/tvia-kordial-buah-asli-1-liter/aff/4212",
    "https://cikgumall.com/product/ryverra-panned-chocolate-40g/aff/4212",
    "https://cikgumall.com/product/premium-lite-edition-brownies-cookies-cocoa-bakers/aff/4212",
    "https://cikgumall.com/product/nyambal-sambal-ikan-masin/aff/4212",
    "https://cikgumall.com/aff/4212",
    "https://cikgumall.com/product/hotel-toiletries-by-anastays/aff/4212",
    "https://cikgumall.com/product/mrs-refreshing-scent-mini-pack-10ml/aff/4212",
    "https://cikgumall.com/product/teega-crispy-machos-salted-100g-2/aff/4212",
    "https://cikgumall.com/product/estana-tiramisu-choco-dates-milk-chocolate-150g/aff/4212",
    "https://cikgumall.com/product/estana-bar-chocolate-45g/aff/4212",
]

def solve_captcha_with_proxy(proxy, url):
    import logging
    from CloudflareBypasser import CloudflareBypasser
    from DrissionPage import ChromiumPage, ChromiumOptions

    logging.info(f"[🧩] Attempting manual CAPTCHA bypass using proxy: {proxy}")

    options = ChromiumOptions().auto_port()
    options.set_paths(browser_path="/usr/bin/google-chrome")
    options.headless(False)

    options.set_argument("-no-first-run")
    options.set_argument("-incognito")
    options.set_argument("-disable-gpu")
    options.set_argument("-window-size=1280,800")
    options.set_argument(f"--proxy-server=http://{proxy}")

    driver = ChromiumPage(addr_or_opts=options)

    try:
        driver.get(url)
        cf_bypasser = CloudflareBypasser(driver)
        cf_bypasser.bypass()

        logging.info(f"[✓] CAPTCHA bypass succeeded: {driver.current_url}")
        time.sleep(10)  # Stay for a bit
        driver.quit()
        return True
    except Exception as e:
        logging.warning(f"[x] CAPTCHA solver failed: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

def load_proxies(path):
    proxies = set()
    if os.path.exists(path):
        with open(path, 'r') as file:
            proxies.update(line.strip() for line in file if line.strip())
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'r') as file:
            proxies.update(line.strip() for line in file if line.strip())
    return list(proxies)

async def validate_proxy_async(session, proxy):
    parts = proxy.strip().split(":")
    
    # Authenticated proxy (username:password)
    if len(parts) == 4:
        ip, port, user, pwd = parts
        proxy_url = f"http://{ip}:{port}"
        auth = BasicAuth(user, pwd)
        try:
            async with session.get(
                "http://httpbin.org/ip",
                proxy=proxy_url,
                proxy_auth=auth,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as res:
                if res.status == 200:
                    print(f"[✓] Authenticated proxy works: {proxy_url}")
                    return proxy
        except Exception as e:
            print(f"[x] Authenticated proxy failed: {proxy_url} | {e}")
        return None

    # Unauthenticated proxy (no username:password)
    elif len(parts) == 2:
        ip, port = parts
        schemes = ["http", "https", "socks4", "socks5"]
        for scheme in schemes:
            proxy_url = f"{scheme}://{ip}:{port}"
            try:
                async with session.get(
                    "http://httpbin.org/ip",
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as res:
                    if res.status == 200:
                        print(f"[✓] Unauthenticated proxy works: {proxy_url}")
                        return proxy
            except Exception:
                continue
        print(f"[x] Proxy failed all schemes: {proxy}")
        return None

    else:
        print(f"[!] Invalid proxy format: {proxy}")
        return None

async def validate_proxies_async(proxies):
    validated = []
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [validate_proxy_async(session, proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks)
        validated = [r for r in results if r]
    return validated

def simulate_visit_with_proxy(proxy, target_url, user_agent):
    error_keywords = [
        "ERR_TIMED_OUT", "ERR_CONNECTION_RESET",
        "ERR_TUNNEL_CONNECTION_FAILED", "ERR_EMPTY_RESPONSE", "ERR_NO_SUPPORTED_PROXIES"
    ]
    server_debug_signatures = [
        "REMOTE_ADDR", "REQUEST_METHOD", "REQUEST_URI", "HTTP_USER_AGENT"
    ]

    try:
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument(f"--user-agent={user_agent}")
        chrome_options.add_argument(f"--proxy-server=http://{proxy}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--allow-insecure-localhost")
        #chrome_options.add_argument("--headless=new")

        print(f"[→] Launching Chrome with proxy {proxy} and user-agent: {user_agent}")
        driver = uc.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)

        driver.get(STARTER_URL)
        time.sleep(random.uniform(2, 5))
        if any(err in driver.page_source for err in error_keywords):
            print(f"[x] Proxy {proxy} failed on STARTER page.")
            driver.quit()
            return False
        if any(sig in driver.page_source for sig in server_debug_signatures):
            print(f"⚠️ Proxy {proxy} hit debug/info dump page.")
            driver.quit()
            return False

        driver.get(target_url)
        time.sleep(random.uniform(5, 8))
        if any(err in driver.page_source for err in error_keywords):
            print(f"[x] Proxy {proxy} failed on TARGET page. Trying manual CAPTCHA bypass...")
            driver.quit()
            if solve_captcha_with_proxy(proxy, target_url):
                print(f"[✓] Manual bypass succeeded for {proxy}")
                return True
            return False

        for _ in range(random.randint(3, 6)):
            driver.execute_script("window.scrollBy(0, window.innerHeight / 2);")
            time.sleep(random.uniform(1, 2))

        wait_time = random.randint(10, 15)
        print(f"[✓] Stayed {wait_time}s on {target_url}")
        time.sleep(wait_time)
        driver.quit()
        return True

    except Exception as e:
        print(f"[x] Proxy {proxy} failed on STARTER page. Trying manual CAPTCHA bypass...")
        driver.quit()
        if solve_captcha_with_proxy(proxy, STARTER_URL):
            print(f"[✓] Manual bypass succeeded for {proxy}")
            return True
        return False

def run_parallel_visits(all_proxies, target_urls, workers=500):
    print("[*] Validating proxies asynchronously...")
    validated = asyncio.run(validate_proxies_async(all_proxies))

    print(f"[✓] Found {len(validated)} working proxies.")
    logging.info(f"[✓] Found {len(validated)} working proxies.")
    total_valid_proxies = len(validated)
    total_attempts = 0
    total_successes = 0

    ua = UserAgent()

    for proxy in validated:
        for _ in range(VISITS_PER_PROXY):
            user_agent = ua.random
            target = random.choice(target_urls)
            success = simulate_visit_with_proxy(proxy, target, user_agent)
            total_attempts += 1
            if success:
                total_successes += 1
            else:
                break  # Stop using this proxy if it fails once

        print(f"\n[📊 STATS]")
        print(f"  Total working proxies: {total_valid_proxies}")
        print(f"  Visit progress: {total_attempts}")
        print(f"  Successful visits (no error/debug): {total_successes}\n")
        logging.info(f"  Successful visits (no error/debug): {total_successes}\n")

        if total_successes >= total_valid_proxies * VISITS_PER_PROXY:
            break  # Early exit if desired count is met

    print("[✔] Visit simulation completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=500, help="Concurrent threads for validating and visiting")
    args = parser.parse_args()

    all_proxies = load_proxies(PROXY_FILE_PATH)
    random.shuffle(all_proxies)
    print(f"[*] Loaded {len(all_proxies)} total proxies.")
    logging.info(f"[*] Loaded {len(all_proxies)} total proxies.")
    run_parallel_visits(all_proxies, TARGET_URLS, workers=args.workers)
    logging.info("=== Run ended ===\n") 
