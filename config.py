import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Proxy Settings (if needed)
PROXY = os.getenv("PROXY")

# Scraping Parameters
TARGET_USERNAMES = ["virat.kohli"]  # List of usernames to scrape
POST_LIMIT = 5  # Number of posts per profile

# Anti-detection Configuration
DELAY_CONFIG = {
    'range': (3, 7),  # Min/max seconds
    'type': 'normal'  # Options: uniform, normal
}

BROWSER_CONFIG = {
    "headless": False,
    "slow_mo": 150,  # Natural human-like delays
    "args": [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-web-security"
    ]
}

VIEWPORT_CONFIG = {
    'presets': [
        {'width': 1920, 'height': 1080, 'device_scale_factor': 1},
        {'width': 1366, 'height': 768, 'device_scale_factor': 1},
        {'width': 1440, 'height': 900, 'device_scale_factor': 2}
    ]
}

WEBGL_SPOOFING = {
    'enabled': True,
    'vendor': 'Google Inc. (NVIDIA)',
    'renderer': 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)'
}

BROWSER_FEATURES = {
    'disable_webdriver': True,
    'disable_webrtc': True,
    'disable_geolocation': True,
    'disable_canvas_fingerprint': True,  # Added for extra anti-detection
    'disable_audio_fingerprint': True
}

# User-Agent Rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15"
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

INSTAGRAM_SELECTORS = {
    "name": "h1._ap3a._aaco._aacu._aacx._aad6._aade",
    "bio": "div._aacl._aaco._aacu._aacx._aad6._aade",
    "stats_xpath": "//header//ul/li[{}]//span//span"
}

# File Output Configuration
OUTPUT_CONFIG = {
    'default_filename': 'instagram_data',
    'format': 'excel',  # 'excel', 'csv', or 'json'
    'timestamp': True,
    'profile_sheet': 'Profiles',
    'posts_sheet': 'Posts'
}

FILE_EXTENSIONS = {
    'excel': '.xlsx',
    'csv': '.csv',
    'json': '.json'
}

# Anti-detection delay range (min, max) in seconds.
DELAY_RANGE = (2, 5)

HUMAN_TYPING = {
    "min_delay": 0.08,  # Seconds between keystrokes
    "max_delay": 0.15
}

