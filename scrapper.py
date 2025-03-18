import json
from playwright.sync_api import sync_playwright
from config import TARGET_USERNAMES, MOBILE_VIEWPORT, MOBILE_USER_AGENT, PROXY
from anti_detect import apply_anti_detection
import logging
import time
import re
import random

logger = logging.getLogger(__name__)

def convert_insta_number(num_str):
    try:
        clean = num_str.lower().replace('followers', '').replace('following', '').replace('posts', '').strip()
        if 'm' in clean:
            return int(float(clean.replace('m', '')) * 1_000_000)
        if 'k' in clean:
            return int(float(clean.replace('k', '')) * 1_000)
        return int(clean.replace(',', ''))
    except:
        return num_str

def handle_popups(page):
    popup_closed = False
    try:
        # Attempt to close any login popups
        close_button = page.locator('svg[aria-label="Close"]').first
        if close_button.is_visible(timeout=5000):
            close_button.click()  # Close the popup if found
            print("Closed login popup via SVG close button")
            popup_closed = True
            page.wait_for_timeout(2000)  # Wait after closing the popup
    except Exception as e:
        print("Popup close error:", e)

def scrape_profile(page, username, context):
    url = f"https://www.instagram.com/{username}/"
    print(f"Navigating to {url}")
    
    try:
        page.goto(url, timeout=120000, wait_until="networkidle")
        page.wait_for_selector("header section", state="attached", timeout=120000)
        handle_popups(page)
    except Exception as e:
        print(f"🚨 Main profile navigation failed: {e}")
        return None
    # Profile scraping
    try:
        stats_elements = page.locator("header section ul li").all()
        profile_data = {
            "Name": page.locator("header h2").first.inner_text(),
            "Bio": page.locator("header section div").nth(1).inner_text(),  # Fixed bio extraction
            "Posts": convert_insta_number(stats_elements[0].inner_text()) if len(stats_elements) > 0 else "N/A",
            "Followers": convert_insta_number(stats_elements[1].inner_text()) if len(stats_elements) > 1 else "N/A",
            "Following": convert_insta_number(stats_elements[2].inner_text()) if len(stats_elements) > 2 else "N/A"
        }
        print("✅ Profile data extracted")
    except Exception as e:
        print(f"❌ Profile extraction error: {e}")
        return None

    # Post link collection with retries
    post_links = []
    desired_post_count = 15
    max_scroll_attempts = 3
    scroll_attempts = 0
    # Scroll and try to find enough posts (maximum attempts)
    while scroll_attempts < max_scroll_attempts:
        post_elements = page.locator("a[href*='/p/'], a[href*='/reel/']").all()
        current_count = len(post_elements)
        print(f"Scrolling attempt {scroll_attempts+1}: found {current_count} links")
        if current_count >= desired_post_count:
            break
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # Scroll to the bottom of the page
        page.wait_for_timeout(5000)  # Wait for the page to load more posts
        scroll_attempts += 1

    try:
        # Click 'Show more' button if it exists
        show_more_button = page.locator("button:has-text('more')")
        if show_more_button.is_visible(timeout=3000):
            print("Found 'Show more' button. Clicking it...")
            show_more_button.click()
            page.wait_for_timeout(5000)
    except Exception as e:
        print("No 'Show more' button found or error:", e)

    # Final scroll attempt
    scroll_attempts = 0
    while scroll_attempts < max_scroll_attempts:
        post_elements = page.locator("a[href*='/p/'], a[href*='/reel/']").all()
        current_count = len(post_elements)
        print(f"Scrolling attempt {scroll_attempts+1}: found {current_count} links")
        if current_count >= desired_post_count:
            break
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(5000)
        scroll_attempts += 1
        
    # Get the final count of post links
    post_elements = page.locator("a[href*='/p/'], a[href*='/reel/']").all()
    final_count = len(post_elements)
    print(f"Final count of links on the page: {final_count}")

    # Filter the post links and construct the full URL for each post
    post_links = [post.get_attribute('href') for post in post_elements if post.get_attribute('href')]
    post_links = [f"https://www.instagram.com{link}" if link.startswith('/') else link for link in post_links]
    print(f"Filtered to {len(post_links)} post links")

    if not post_links:
        print("No posts found.")
        return []  # Return empty if no posts are found

    # Mobile context setup
    mobile_context = context.browser.new_context(
        user_agent=MOBILE_USER_AGENT,
        viewport=MOBILE_VIEWPORT,
        is_mobile=True,
        has_touch=True,
        java_script_enabled=True,
        locale="en-US",
        timezone_id="America/New_York",
        proxy=PROXY if PROXY else None
    )
    
    post_data = []
    
    for link in post_links[:desired_post_count]:
        mobile_page = None
        try:
            mobile_page = mobile_context.new_page()
            apply_anti_detection(mobile_page)
            mobile_page.set_default_navigation_timeout(120000)
            mobile_page.set_default_timeout(30000)

            # Navigate with retries
            for retry in range(2):
                try:
                    response = mobile_page.goto(
                        link, 
                        wait_until="networkidle",
                        referer=f"https://www.instagram.com/{username}/"
                    )
                    if response.status >= 400:
                        raise Exception(f"HTTP Error {response.status}")
                    break
                except Exception as e:
                    if retry == 1:
                        raise
                    print(f"Retrying post navigation: {e}")
                    mobile_page.wait_for_timeout(5000)

            # Content verification
            mobile_page.wait_for_function(
                """() => document.querySelector('article') || document.querySelector('video')"""
            )
            
            post_details = {
                "post_url": link,
                "caption": "No Caption",
                "likes": 0,
                "comments_count": 0,
                "hashtags": [],
                "media_url": "No Media"
            }

            # Likes extraction
            try:
                likes_element = mobile_page.locator(
                    'span.xdj266r.x11i5rnm.xat24cr.x1mh8g0r:visible'
                ).first
                post_details["likes"] = convert_insta_number(likes_element.inner_text())
            except Exception as e:
                print(f"⚠️ Likes error: {e}")

            # Comments handling
            try:
                # Updated selector to find the comment count span that includes the text "View all X comments"
                comments_selector = 'span:has-text("View all")'
                comments_element = mobile_page.locator(comments_selector).first

                if comments_element:
                    # Extracting the count text (e.g., "View all 1234 comments")
                    count_text = comments_element.inner_text()
        
                    # Using regex to capture the number of comments from the string like "View all 1234 comments"
                    numbers = re.findall(r'[\d,]+', count_text)
        
                    if numbers:
                        # Clean the number and convert it to an integer
                        post_details["comments_count"] = int(numbers[-1].replace(',', ''))
                else:
                    post_details["comments_count"] = 0
        
                print(f"Comments Count: {post_details['comments_count']}")
            except Exception as e:
                print(f"⚠️ Comments error: {e}")
            
            # Caption and Hashtags extraction
            try:
                # Locate the caption within the h1 element (initial part)
                caption_element = mobile_page.locator('h1._ap3a').first
                caption_text = caption_element.inner_text() if caption_element else "No Caption"
    
                # Check if the caption is truncated (by looking for the "more" button)
                more_button = mobile_page.locator('div[aria-disabled="false"][role="button"]').first
                if more_button.is_visible():
                    print("Caption is truncated, clicking 'More' to reveal the full caption.")
        
                    # Wait for the "more" button to be clickable
                    more_button.wait_for(state="visible", timeout=10000)  # wait up to 5 seconds
        
                    # Click the "more" button to reveal the full caption
                    more_button.click()

                    # Wait for the full caption to appear after clicking the "more" button
                    mobile_page.wait_for_timeout(5000)  # wait for 2 seconds (adjust this if needed)
        
                    # Re-fetch the full caption after the "more" button click
                    caption_element = mobile_page.locator('h1._ap3a').first
                    caption_text = caption_element.inner_text() if caption_element else "No Caption"
    
                # Store the full caption in post_details
                post_details["caption"] = caption_text

                # Extract hashtags using regex
                hashtags = re.findall(r'#\w+', caption_text)
                post_details["hashtags"] = hashtags

                # Print the extracted information
                print(f"Caption: {caption_text}")
                print(f"Hashtags: {hashtags}")

            except Exception as e:
                print(f"⚠️ Caption and Hashtags extraction error: {e}")


            
            
            try:
                media = mobile_page.locator('img.x5yr21d, video.x1lliihq').first
                post_details["media_url"] = (
                    media.get_attribute('src') 
                    or media.get_attribute('poster') 
                    or media.get_attribute('srcset').split()[0]
                )
            except Exception as e:
                print(f"⚠️ Media error: {e}")

            post_data.append(post_details)
            print(f"✅ Processed post: {link}")

        except Exception as e:
            print(f"🚨 Post processing failed: {str(e)[:200]}")
            if mobile_page:
                try:
                    mobile_page.screenshot(path=f"error_{int(time.time())}.png")
                except:
                    pass
        finally:
            if mobile_page:
                mobile_page.close()

    mobile_context.close()
    return {
        "profile": profile_data,
        "posts": post_data
    }

def scrape_instagram_profile(username, context):
    try:
        page = context.new_page()
        apply_anti_detection(page)
        page.set_default_navigation_timeout(120000)
        return scrape_profile(page, username, context)
    except Exception as e:
        logger.error(f"🔥 Critical error: {str(e)}")
        return None
    finally:
        try:
            page.close()
        except:
            pass

# Main execution
if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(**config.BROWSER_CONFIG)
        context = browser.new_context(**config.BROWSER_CONFIG.get("context", {}))
        
        results = []
        for username in config.TARGET_USERNAMES:
            print(f"\n=== Scraping {username} ===")
            data = scrape_instagram_profile(username, context)
            if data:
                results.append(data)
                with open(f"{username}_data.json", "w") as f:
                    json.dump(data, f, indent=2)
                print(f"✅ Saved data for {username}")
        
        context.close()
        browser.close()

