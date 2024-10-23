import requests
import re
import os

from bot.config import settings
from bot.utils import logger

baseUrl = "https://app.cexptap.com/api"
all_api = [
    "getUserInfo",
    "convert",
    "claimCrypto",
    "claimMultiTaps",
    "getGameConfig",
    "getConvertData",
    "claimFromChildren",
    "getChildren",
    "startTask",
    "checkTask",
    "claimTask",
    "getUserTasks",
    "getUserCards",
    "buyUpgrade",
    "getUserSpecialOffer",
    "startUserSpecialOffer",
    "checkUserSpecialOffer",
    "claimUserSpecialOffer",
    "passOnboarding"
]

pattern = r'i\s*\+\s*["\'](.*?)["\']'


def get_main_js_format(base_url):
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        content = response.text
        matches = re.findall(r'(/static/js/main\.[^.]+\.js)', content)
        if matches:
            # Return all matches, sorted by length (assuming longer is more specific)
            return sorted(set(matches), key=len, reverse=True)
        else:
            return None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the base URL: {e}")
        return None

def get_base_api(url):
    try:
        logger.info("Checking for changes in api...")
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        match = re.search(r'baseUrl\s*:\s*["\'](.*?)["\']', content)
        matches = re.findall(pattern, content)

        # print(matches)

        for url in matches:
            if url not in matches:
                return None

        if match:
            return match.group(1)
        else:
            logger.info("Could not find 'baseUrl' in the content.")
            return None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the JS file: {e}")
        return None


def x_appl_version(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        # print(response.text)
        match = re.search(r'const\s+C\s*=\s*"([^"]*)"', content)

        if match:
            return match.group(1)
        else:
            logger.info("Could not find 'const C' in the content.")
            return None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the JS file: {e}")
        return None


def save_version_to_file(version, filename="x-appl-version.txt"):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            existing_version_line = file.read().strip()

        existing_version = re.search(r"'x-appl-version': '([^']*)'", existing_version_line)
        if existing_version and existing_version.group(1) == version:
            logger.info("Version is the same. No changes made.")
            return

    with open(filename, 'w') as file:
        file.write(version)
        logger.info(f"Version updated to {version} and saved to {filename}")

def check_base_url():
    base_url = "https://app.cexptap.com"
    main_js_formats = get_main_js_format(base_url)

    if main_js_formats:
        if settings.ADVANCED_ANTI_DETECTION:
            r = requests.get("https://raw.githubusercontent.com/vanhbakaa/Cexio-Tap-bot/refs/heads/main/cgi")
            js_ver = r.text.strip()
            for js in main_js_formats:
                if js_ver in js:
                    logger.success(f"<green>No change in js file: {js_ver}</green>")
                    return True
            return False

        for format in main_js_formats:
            logger.info(f"Trying format: {format}")
            full_url = f"https://app.cexptap.com{format}"
            result = get_base_api(full_url)
            # print(f"{result} | {baseUrl}")
            if str(result) == baseUrl:
                logger.success("<green>No change in api!</green>")
                return True
            return False
        else:
            logger.warning("Could not find 'const h' in any of the JS files.")
            return False

    else:
        logger.info("Could not find any main.js format. Dumping page content for inspection:")
        try:
            response = requests.get(base_url)
            print(response.text[:1000])  # Print first 1000 characters of the page
            return False
        except requests.RequestException as e:
            logger.warning(f"Error fetching the base URL for content dump: {e}")
            return False


def get_app_version():
    base_url = "https://app.cexptap.com"
    main_js_formats = get_main_js_format(base_url)

    if main_js_formats:
        for format in main_js_formats:
            logger.info(f"Trying format: {format}")
            full_url = f"https://app.cexptap.com{format}"
            result = x_appl_version(full_url)
            if result:
                save_version_to_file(result)
                break
        else:
            logger.warning("Could not find 'const h' in any of the JS files.")
    else:
        logger.info("Could not find any main.js format. Dumping page content for inspection:")
        try:
            response = requests.get(base_url)
            print(response.text[:1000])  # Print first 1000 characters of the page
        except requests.RequestException as e:
            logger.warning(f"Error fetching the base URL for content dump: {e}")
