#!/usr/bin/env python3
"""
Main script to run the Africa Digital Consultancy Radar
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import logging
import schedule
import time

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, '/app')

# Load environment variables
load_dotenv()

from src.utils.logger import setup_logger
from src.utils.email_sender import EmailSender
from src.utils.exporter import Exporter
from src.scraper.scraper_factory import ScraperFactory
from src.ai.classifier import Classifier
from src.database.local_db import LocalDatabase

logger = setup_logger()

# Initialize components
scraper_factory = ScraperFactory()
classifier = Classifier()
db_handler = LocalDatabase("data")

def run_scan():
    """Execute the main scanning workflow"""
    try:
        logger.info("Starting radar scan...")
        
        # Initialize scraper
        scraper = scraper_factory.get_scraper('default')
        data = scraper.fetch()
        
        # Process with AI
        classified_data = classifier.classify(data)
        
        # Store results
        db_handler.save_results(classified_data)
        
        logger.info("Scan completed successfully")
    except Exception as e:
        logger.error(f"Scan failed: {e}", exc_info=True)

def schedule_scans():
    """Setup scheduled scans"""
    interval = int(os.getenv('SCHEDULE_INTERVAL', 3600))
    schedule.every(interval).seconds.do(run_scan)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    """Main entry point"""
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description='Africa Digital Consultancy Radar')
    parser.add_argument('--no-email', action='store_true', help='Skip sending email')
    parser.add_argument('--no-export', action='store_true', help='Skip exporting data')
    parser.add_argument('--config', default='config/settings.yaml', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Run the radar
    run_scan()
    
    if not args.no_email or not args.no_export:
        try:
            from src.database.local_db import LocalDatabase
            from src.ai.summarizer import WeeklySummarizer
            
            # Re-initialize components
            local_db = LocalDatabase("data")
            openai_key = os.getenv('OPENAI_API_KEY')
            
            if not args.no_export:
                # Export data to various formats
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                insights = {}
                
                # Export to JSON
                json_data = Exporter.to_json(data, f"data/export_{timestamp}.json")
                
                # Export to CSV
                csv_data = Exporter.to_csv(data, f"data/export_{timestamp}.csv")
                
                # Export to Markdown (for easy reading)
                md_data = Exporter.to_markdown(data)
                with open(f"data/digest_{timestamp}.md", 'w') as f:
                    f.write(md_data)
                
                logger.info("Data exported to multiple formats")
                
                insights = {
                    "exported_files": {
                        "json": f"data/export_{timestamp}.json",
                        "csv": f"data/export_{timestamp}.csv",
                        "markdown": f"data/digest_{timestamp}.md"
                    }
                }
            
            if not args.no_email:
                # Send weekly digest email
                email_sender = EmailSender()
                recipients = ["example@example.com"]  # Replace with actual recipients
                email_sender.send_digest(data, insights, recipients)
                logger.info("Weekly digest email sent")
        
        except Exception as e:
            logger.error(f"Error in post-scan processes: {e}", exc_info=True)

if __name__ == "__main__":
    schedule_scans()
    # main()  # Uncomment this line to enable manual run