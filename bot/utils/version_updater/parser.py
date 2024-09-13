import requests
import re
import os
from bot.utils import logger

def x_appl_version(url):
    # Fetch the content of the URL
    response = requests.get(url)
    # Search for const g = "..." in the content
    content = response.text
    match = re.search(r'const\s+g\s*=\s*"([^"]*)"', content)
    
    if match:
        return match.group(1)
    else:
        return None

def save_version_to_file(version, filename="x-appl-version.txt"):
    # Check if the file exists
    if os.path.exists(filename):
        # Read the current version from the file
        with open(filename, 'r') as file:
            existing_version_line = file.read().strip()
        
        # Extract the current version from the format 'x-appl-version': 'version'
        existing_version = re.search(r"'x-appl-version': '([^']*)'", existing_version_line)
        if existing_version and existing_version.group(1) == version:
            logger.info("Version is the same. No changes made.")
            

    # If the file does not exist or the version is different, write the new version
    with open(filename, 'w') as file:
        file.write(version)
        logger.info(f"Version updated to {version} and saved to {filename}")

if __name__ == '__main__':

    url = "https://cexp.cex.io/static/js/main.0b92331a.js"

    # Fetch and extract const g
    result = x_appl_version(url)

    if result:
        save_version_to_file(result)
    else:
        print("Could not find 'const g' in the content.")
