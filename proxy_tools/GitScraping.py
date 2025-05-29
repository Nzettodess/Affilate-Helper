import requests
import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import pickle
import sys
from datetime import datetime   
import logging

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

INPUT_DIR = "data/input"
COOKIE_FILE = os.path.join(INPUT_DIR, "hidemyname_cookies.pkl")

webshare_api_key = "yourapikey" #you can use environment variable to setup as well
webshare_base_url = f"https://proxy.webshare.io/api/v2/proxy/list/download/jrdtdufojdsasvlhuvrftmdnwskxbvgmouoculej/-/any/username/direct/-/"

webshare_headers = {
    "Authorization": f"Token {webshare_api_key}"
}

# Optional: Add filters here
webshare_params = {
    # "country": "US",           # Uncomment to filter by country
    # "type": "socks5",          # socks4, socks5, http, https
    # "mode": "direct"           # direct or rotate
}


import requests

def fetch_from_webshare():
    print("[*] Downloading proxy list from Webshare.io...")
    proxies = set()
    
    try:
        url = "https://proxy.webshare.io/api/v2/proxy/list/download/jrdtdufojdsasvlhuvrftmdnwskxbvgmouoculej/-/any/username/direct/-/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        for line in response.text.strip().splitlines():
            # Each line should be in the format ip:port:username:password
            parts = line.strip().split(":")
            if len(parts) == 4:
                proxies.add(line.strip())

        print(f"[✓] Fetched {len(proxies)} proxies from Webshare.io")
    
    except requests.exceptions.RequestException as e:
        print(f"[✗] Webshare request error: {e}")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")

    return proxies
            
# === API Configuration ===
proxy_pool_api_key = "yourapikey"
proxy_pool_api_url = "https://proxy-pool-api.onrender.com/get_proxy"
proxy_titan_api_key = "yourapikey"

api_params = {
    "country": "US",
    "max_ping": 800,
    "limit": 1000,
    "api_key": proxy_pool_api_key
}

# === Directory Setup ===
BASE_DIR = os.getcwd()
INPUT_DIR = os.path.join(BASE_DIR, "data", "input")
os.makedirs(INPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(INPUT_DIR, "proxies.txt")

# === Public Proxy Sources ===
urls = [
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/https/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks4.txt",
    "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt",
    "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5_checked.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks4_checked.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http_checked.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    "https://raw.githubusercontent.com/proxylist-to/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/proxylist-to/proxy-list/main/socks4.txt",
    "https://raw.githubusercontent.com/proxylist-to/proxy-list/main/socks5.txt",
    "https://raw.githubusercontent.com/thenasty1337/free-proxy-list/main/data/latest/types/http/proxies.txt",
    "https://raw.githubusercontent.com/thenasty1337/free-proxy-list/main/data/latest/types/socks4/proxies.txt",
    "https://raw.githubusercontent.com/thenasty1337/free-proxy-list/main/data/latest/types/socks5/proxies.txt",
    "https://raw.githubusercontent.com/dpangestuw/Free-Proxy/main/http_proxies.txt",
    "https://raw.githubusercontent.com/dpangestuw/Free-Proxy/main/socks4_proxies.txt",
    "https://raw.githubusercontent.com/dpangestuw/Free-Proxy/main/socks5_proxies.txt",
    "https://raw.githubusercontent.com/casals-ar/proxy-list/main/http",
    "https://raw.githubusercontent.com/casals-ar/proxy-list/main/socks4",
    "https://raw.githubusercontent.com/casals-ar/proxy-list/main/socks5",
    "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt"
]

# === ProxyTitan ===
def fetch_from_proxytitan():
    print("[*] Fetching from ProxyTitan...")
    base_url = "https://proxytitan.com/api/v1.0/free/proxies"
    proxy_types = ["http", "socks4", "socks5"]
    proxies = set()

    for proto in proxy_types:
        params = {"apiKey": proxy_titan_api_key, "timeout": 10000, "output": "json", "protocol": proto}
        try:
            res = requests.get(base_url, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()
            for item in data.get("proxies", []):
                if isinstance(item, str):
                    proxies.add(item.strip())
                elif isinstance(item, dict) and "ip_port" in item:
                    proxies.add(item["ip_port"].strip())
        except Exception as e:
            print(f"[!] Error fetching ProxyTitan {proto}: {e}")
    return proxies

# === ProxyPool API ===
def fetch_from_api():
    print("[*] Fetching from ProxyPool API...")
    proxies = set()
    try:
        res = requests.get(proxy_pool_api_url, params=api_params, timeout=10)
        res.raise_for_status()
        data = res.json()
        for proxy in data.get("proxies", []):
            ip_port = proxy.get("ip_port") or f"{proxy.get('ip')}:{proxy.get('port')}"
            if ip_port:
                proxies.add(ip_port)
    except Exception as e:
        print(f"[!] ProxyPool API error: {e}")
    return proxies

# === Public Sources ===
def fetch_from_sources():
    print("[*] Fetching from public sources...")
    proxies = set()
    for url in urls:
        try:
            res = requests.get(url, timeout=15)
            res.raise_for_status()
            for line in res.text.splitlines():
                line = line.strip()
                if ':' in line and not line.startswith(('#', '//', '[')):
                    proxies.add(line.split("://")[-1])
        except Exception as e:
            print(f"[!] Failed to fetch {url}: {e}")
    return proxies

# === ProxyScrape via Selenium ===
def fetch_from_proxyscrape():
    print("[*] Scraping ProxyScrape via Selenium...")
    proxies = set()
    try:
        options = uc.ChromeOptions()
        options.binary_location = "/usr/bin/google-chrome"  # or /opt/chrome/chrome
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        driver = uc.Chrome(options=options, driver_executable_path="/usr/local/bin/chromedriver")
        driver.get("https://proxyscrape.com/free-proxy-list")

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        time.sleep(2)

        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                if ip and port:
                    proxies.add(f"{ip}:{port}")
        driver.quit()
    except Exception as e:
        print(f"[!] ProxyScrape error: {e}")
    return proxies

# === Proxiware via JS Injection ===
def fetch_from_proxiware():
    print("[*] Scraping Proxiware...")
    proxies = set()
    try:
        options = uc.ChromeOptions()
        options.binary_location = "/usr/bin/google-chrome"  # or /opt/chrome/chrome
        options.headless = True
        options.add_argument("--window-size=1920,1080")
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        driver = uc.Chrome(options=options, driver_executable_path="/usr/local/bin/chromedriver")
        driver.get("https://proxiware.com/free-proxy-list")
        time.sleep(5)

        js_script = """
        window.collectedProxies = [];
        function scrapePage(page = 0) {
            if (page >= 15) return;
            const rows = Array.from(document.querySelectorAll('td'));
            for (let i = 0; i < rows.length - 1; i++) {
                const ip = rows[i].innerText.trim();
                const port = rows[i + 1].innerText.trim();
                if (/^\\d+\\.\\d+\\.\\d+\\.\\d+$/.test(ip) && /^\\d+$/.test(port)) {
                    window.collectedProxies.push(ip + ':' + port);
                }
            }
            const nextBtn = document.querySelector('.next-button');
            if (nextBtn) {
                nextBtn.click();
                setTimeout(() => scrapePage(page + 1), 1500);
            }
        }
        document.querySelector('#speedSelect').value = 'fast';
        document.querySelector('#speedSelect').dispatchEvent(new Event('change'));
        setTimeout(() => scrapePage(), 1000);
        """
        driver.execute_script(js_script)
        time.sleep(20)

        proxies.update(driver.execute_script("return window.collectedProxies;"))
        driver.quit()
    except Exception as e:
        print(f"[!] Proxiware scraping error: {e}")
    return proxies
    
# === Save Results ===
def save_proxies(proxy_list):
    with open(OUTPUT_FILE, "w") as f:
        for proxy in sorted(proxy_list):
            f.write(proxy + "\n")
    print("[✓] Saved {} proxies to {}".format(len(proxy_list), OUTPUT_FILE), flush=True)
    logging.info("[✓] Saved {} proxies to {}".format(len(proxy_list), OUTPUT_FILE))


# === MAIN ===
if __name__ == "__main__":
    all_proxies = set()
    
    webshare_proxies = fetch_from_webshare()
    other_proxies = set()

    other_proxies |= fetch_from_proxytitan()
    other_proxies |= fetch_from_api()
    other_proxies |= fetch_from_sources()
    other_proxies |= fetch_from_proxyscrape()
    other_proxies |= fetch_from_proxiware()

    # Combine with Webshare last to preserve full format
    all_proxies = webshare_proxies | (other_proxies - webshare_proxies)

    save_proxies(all_proxies)

