import requests
import re
import os
from bot.utils import logger


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


def x_appl_version(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        match = re.search(r'const\s+h\s*=\s*"([^"]*)"', content)

        if match:
            return match.group(1)
        else:
            logger.info("Could not find 'const h' in the content.")
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

def get_app_version():
    base_url = "https://cexp.cex.io/"
    main_js_formats = get_main_js_format(base_url)

    if main_js_formats:
        for format in main_js_formats:
            logger.info(f"Trying format: {format}")
            full_url = f"https://cexp.cex.io{format}"
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
