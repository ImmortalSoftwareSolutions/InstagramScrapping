from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from scrapper import scrape_instagram_profile
from data_handler import save_to_file 
from anti_detect import apply_anti_detection
from config import BROWSER_CONFIG, VIEWPORT_CONFIG, get_random_user_agent
from data_handler import save_to_file  # Added to restore file-saving functionality
import random
import logging

def main():
    print("Starting Instagram Scraper (No Login Required)...")
app = Flask(__name__)
logger = logging.getLogger(__name__)  # Set up logging for error handling

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    print(f"🚀 Scraping Instagram profile: {username}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(**BROWSER_CONFIG)
        context = browser.new_context(
            user_agent=get_random_user_agent(),
            viewport=random.choice(VIEWPORT_CONFIG['presets'])
        )
        page = context.new_page()
        apply_anti_detection(page)
        
        scraped_data = scrape_instagram_profile(username, context)
        
        browser.close()
        
        if not scraped_data:
            return jsonify({'error': 'Failed to scrape data'}), 500
        
        # Save the scraped data to files as in the original setup
        try:
            # Wrap profile in a list since save_to_file expects a list of profiles
            save_to_file([scraped_data['profile']], scraped_data['posts'], filename=username)
            print(f"✅ Saved data for {username}")
        except Exception as e:
            logger.error(f"❌ Failed to save data for {username}: {str(e)}")
            # Continue to return data even if saving fails
        
        return jsonify(scraped_data)

if __name__ == "__main__":
    app.run(debug=True)
