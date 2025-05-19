import time
import logging
import os
from CloudflareBypasser import CloudflareBypasser
from DrissionPage import ChromiumPage, ChromiumOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cloudflare_bypass.log', mode='w')
    ]
)

def get_chromium_options(browser_path: str, arguments: list) -> ChromiumOptions:
    """
    Configures and returns Chromium options.
    
    :param browser_path: Path to the Chromium browser executable.
    :param arguments: List of arguments for the Chromium browser.
    :return: Configured ChromiumOptions instance.
    """
    options = ChromiumOptions().auto_port()
    options.set_paths(browser_path=browser_path)
    for argument in arguments:
        options.set_argument(argument)
    return options

def main():
    # Toggle headless mode here:
    isHeadless = False  # Set True to test headless after confirming non-headless works

    if isHeadless:
        from pyvirtualdisplay import Display
        display = Display(visible=0, size=(1920, 1080))
        display.start()
    else:
        display = None

    browser_path = os.getenv('CHROME_PATH', "/usr/bin/google-chrome")
    # Example for Windows:
    # browser_path = os.getenv('CHROME_PATH', r"C:/Program Files/Google/Chrome/Application/chrome.exe")

    # Arguments for Chromium browser
    arguments = [
        "-no-first-run",
        "-force-color-profile=srgb",
        "-metrics-recording-only",
        "-password-store=basic",
        "-use-mock-keychain",
        "-export-tagged-pdf",
        "-no-default-browser-check",
        "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
        "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
        "-deny-permission-prompts",
        "-disable-gpu",
        "-accept-lang=en-US",
    ]

    if isHeadless:
        arguments.append("--headless=new")  # or '--headless' depending on your Chromium version
        arguments.append("--disable-gpu")

    options = get_chromium_options(browser_path, arguments)

    driver = ChromiumPage(addr_or_opts=options)
    try:
        logging.info('Navigating to the demo page.')
        driver.get('https://cikgumall.com/aff/4212')

        logging.info('Starting Cloudflare bypass.')
        cf_bypasser = CloudflareBypasser(driver)
        cf_bypasser.bypass()

        # Confirm success by logging title and URL
        current_title = driver.title
        current_url = driver.current_url
        logging.info(f"Bypass success. Page title: {current_title}")
        logging.info(f"Current URL: {current_url}")

        print(f"Bypass success. Title: {current_title}")
        print(f"Current URL: {current_url}")

        # Optional: Save screenshot for verification
        driver.save_screenshot("after_bypass.png")
        logging.info("Saved screenshot as 'after_bypass.png'.")

        # Sleep to allow manual check if running non-headless
        if not isHeadless:
            time.sleep(5)

        return True
    except Exception as e:
        logging.error(f"Error during bypass: {e}")
        print(f"Error during bypass: {e}")
        return False
    finally:
        logging.info('Closing browser...')
        driver.quit()
        if display:
            display.stop()

if __name__ == "__main__":
    success = main()
    if not success:
        print("Bypass test failed.")
    else:
        print("Bypass test succeeded.")
