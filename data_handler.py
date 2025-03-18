import pandas as pd
import logging
from datetime import datetime
from config import OUTPUT_CONFIG, FILE_EXTENSIONS
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def save_to_file(profiles: List[Dict], posts: List[Dict], filename: Optional[str] = None) -> None:
    """
    Saves scraped data to files in Excel, CSV, and JSON formats.
    - Excel: Single file with two sheets (Profiles and Posts)
    - CSV: Separate files for profiles and posts
    - JSON: Separate files for profiles and posts

    Args:
        profiles (List[Dict]): List of dictionaries containing profile data.
        posts (List[Dict]): List of dictionaries containing post data.
        filename (Optional[str]): Base filename for output files. If not provided, defaults to the value from OUTPUT_CONFIG.
    """
    try:
        # Check if there is any data to save, if not, log a warning and return
        if not profiles and not posts:
            logger.warning("⚠️ No data to save")
            return

        # Generate base filename with timestamp if enabled in OUTPUT_CONFIG
        base_name = filename or OUTPUT_CONFIG['default_filename']
        if OUTPUT_CONFIG['timestamp']:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = f"{base_name}_{timestamp}"

        # Save data to Excel format: Single file with two sheets (Profiles and Posts)
        excel_filename = f"{base_name}{FILE_EXTENSIONS['excel']}"
        with pd.ExcelWriter(excel_filename) as writer:
            # Save profiles data to Excel if profiles are provided
            if profiles:
                pd.DataFrame(profiles).to_excel(
                    writer, 
                    sheet_name=OUTPUT_CONFIG.get('profile_sheet', 'Profiles'), 
                    index=False
                )
            # Save posts data to Excel if posts are provided
            if posts:
                pd.DataFrame(posts).to_excel(
                    writer, 
                    sheet_name=OUTPUT_CONFIG.get('posts_sheet', 'Posts'), 
                    index=False
                )
        logger.info(f"✅ Saved data to Excel file: {excel_filename}")

        # Save data to CSV format: Separate files for profiles and posts
        if profiles:
            profile_csv_filename = f"{base_name}_profiles{FILE_EXTENSIONS['csv']}"
            pd.DataFrame(profiles).to_csv(profile_csv_filename, index=False)
            logger.info(f"✅ Saved profile data to CSV file: {profile_csv_filename}")
        if posts:
            post_csv_filename = f"{base_name}_posts{FILE_EXTENSIONS['csv']}"
            pd.DataFrame(posts).to_csv(post_csv_filename, index=False)
            logger.info(f"✅ Saved post data to CSV file: {post_csv_filename}")

        # Save data to JSON format: Separate files for profiles and posts
        if profiles:
            profile_json_filename = f"{base_name}_profiles{FILE_EXTENSIONS['json']}"
            pd.DataFrame(profiles).to_json(profile_json_filename, orient='records')
            logger.info(f"✅ Saved profile data to JSON file: {profile_json_filename}")
        if posts:
            post_json_filename = f"{base_name}_posts{FILE_EXTENSIONS['json']}"
            pd.DataFrame(posts).to_json(post_json_filename, orient='records')
            logger.info(f"✅ Saved post data to JSON file: {post_json_filename}")

    except Exception as e:
        # Log error if saving data fails
        logger.error(f"❌ Failed to save data: {str(e)}")
        raise  # Re-raise the exception after logging it

