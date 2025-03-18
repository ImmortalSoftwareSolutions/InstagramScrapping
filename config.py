import random
import os
from dotenv import load_dotenv

load_dotenv()

PROXY = os.getenv("PROXY")

TARGET_USERNAMES = ["virat.kohli"]
POST_LIMIT = 5

DELAY_CONFIG = {
    'range': (3, 7),
    'type': 'normal'
}

BROWSER_CONFIG = {
    "headless": True,  # Modified to True
    "slow_mo": 150,
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
    'disable_canvas_fingerprint': True,
    'disable_audio_fingerprint': True,
    'handle_dialogs': True  # Added
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15"
]

MOBILE_VIEWPORT = {'width': 375, 'height': 812}
MOBILE_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/537.36"

def get_random_user_agent():
    return random.choice(USER_AGENTS)

INSTAGRAM_SELECTORS = {
    "name": "h1._ap3a._aaco._aacu._aacx._aad6._aade",
    "bio": "div._aacl._aaco._aacu._aacx._aad6._aade",
    "stats_xpath": "//header//ul/li[{}]//span//span"
}

OUTPUT_CONFIG = {
    'default_filename': 'instagram_data',
    'format': 'excel',
    'timestamp': True,
    'profile_sheet': 'Profiles',
    'posts_sheet': 'Posts'
}

FILE_EXTENSIONS = {
    'excel': '.xlsx',
    'csv': '.csv',
    'json': '.json'
}

DELAY_RANGE = (2, 5)

HUMAN_TYPING = {
    "min_delay": 0.08,
    "max_delay": 0.15
}
