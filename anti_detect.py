import time
import random
import logging
from config import (
    get_random_user_agent,
    DELAY_CONFIG,
    VIEWPORT_CONFIG,
    WEBGL_SPOOFING,
    BROWSER_FEATURES
)

logger = logging.getLogger(__name__)

def apply_anti_detection(page):
    """Advanced anti-detection measures with multiple fingerprint protections."""
    try:
        # Add dialog handler first
        if BROWSER_FEATURES.get('handle_dialogs', False):
            page.on('dialog', lambda dialog: dialog.dismiss())
            
        # Rest of the existing code
        user_agent = get_random_user_agent()
        page.set_extra_http_headers({"User-Agent": user_agent})
        logger.info(f"🔄 Set User-Agent to: {user_agent}")

        viewport = get_viewport_config()
        page.set_viewport_size(viewport)
        logger.info(f"🖥️ Set viewport to: {viewport['width']}x{viewport['height']}")

        if BROWSER_FEATURES['disable_webdriver']:
            page.add_init_script("delete Object.getPrototypeOf(navigator).webdriver")

        page.add_init_script("Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });")
        page.add_init_script("Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });")
        page.add_init_script("window.chrome = { runtime: {} };")
        page.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
        """)

        if BROWSER_FEATURES['disable_webrtc']:
            page.add_init_script("""
                Object.defineProperty(navigator, 'credentials', { get: () => undefined });
                RTCPeerConnection = undefined;
            """)

        if WEBGL_SPOOFING['enabled']:
            page.add_init_script(f"""
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    if (parameter === 37445) {{ return '{WEBGL_SPOOFING['vendor']}'; }}
                    if (parameter === 37446) {{ return '{WEBGL_SPOOFING['renderer']}'; }}
                    return getParameter(parameter);
                }};
            """)

        if BROWSER_FEATURES.get('disable_canvas_fingerprint', False):
            page.add_init_script("""
                HTMLCanvasElement.prototype.toDataURL = function() { return ""; };
                HTMLCanvasElement.prototype.getContext = function() { return null; };
            """)

        if BROWSER_FEATURES.get('disable_audio_fingerprint', False):
            page.add_init_script("""
                AudioContext = function() { this.createOscillator = function() { return { start: function() {} }; }; };
            """)

        page.add_init_script("Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });")
        apply_behavioral_delay()
        page.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})

    except Exception as e:
        logger.error(f"❌ Anti-detection error: {str(e)}")

def get_viewport_config():
    return random.choice(VIEWPORT_CONFIG['presets'])

def apply_behavioral_delay():
    min_delay, max_delay = DELAY_CONFIG['range']
    delay_type = DELAY_CONFIG.get('type', 'uniform')
    
    if delay_type == 'normal':
        delay = random.normalvariate((min_delay + max_delay) / 2, (max_delay - min_delay) / 4)
    else:
        delay = random.uniform(min_delay, max_delay)
    
    delay = max(min(delay, max_delay), min_delay)
    logger.info(f"⏳ Applying {delay_type} delay: {round(delay, 2)}s")
    time.sleep(delay)
