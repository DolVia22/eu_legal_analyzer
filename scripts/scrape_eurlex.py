#!/usr/bin/env python3
"""
EUR-Lex Comprehensive Scraping Script
Scrapes the EUR-Lex directory and populates the database with legal acts
"""

import sys
import os
import argparse
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from scraper.directory_scraper import EURLexDirectoryScraper
from database.db_manager import DatabaseManager

def main():
    parser = argparse.ArgumentParser(description='Scrape EUR-Lex directory and populate database')
    parser.add_argument('--max-acts', type=int, default=1000, 
                       help='Maximum number of acts to scrape (default: 1000)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--workers', type=int, default=3,
                       help='Number of worker threads (default: 3)')
    parser.add_argument('--stats-only', action='store_true',
                       help='Only show current database statistics')
    
    args = parser.parse_args()
    
    print("🇪🇺 EUR-Lex Comprehensive Scraper")
    print("=" * 50)
    
    # Initialize scraper
    scraper = EURLexDirectoryScraper(delay=args.delay, max_workers=args.workers)
    
    # Show current stats
    stats = scraper.get_scraping_stats()
    print(f"📊 Current Database Statistics:")
    print(f"   Total legal acts: {stats['total_acts_in_db']}")
    print(f"   Processed CELEX numbers: {stats['processed_celexes']}")
    print(f"   Last updated: {stats['timestamp']}")
    print()
    
    if args.stats_only:
        return
    
    print(f"🚀 Starting scraping process...")
    print(f"   Max acts to scrape: {args.max_acts}")
    print(f"   Request delay: {args.delay}s")
    print(f"   Worker threads: {args.workers}")
    print()
    
    start_time = datetime.now()
    
    try:
        # Run comprehensive scraping
        scraped_count = scraper.scrape_comprehensive_legal_acts(max_acts=args.max_acts)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print()
        print("✅ Scraping completed successfully!")
        print(f"   Acts scraped: {scraped_count}")
        print(f"   Duration: {duration}")
        print(f"   Rate: {scraped_count / duration.total_seconds():.2f} acts/second")
        
        # Show final stats
        final_stats = scraper.get_scraping_stats()
        print()
        print(f"📊 Final Database Statistics:")
        print(f"   Total legal acts: {final_stats['total_acts_in_db']}")
        print(f"   Processed CELEX numbers: {final_stats['processed_celexes']}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Scraping interrupted by user")
        
        # Show partial stats
        partial_stats = scraper.get_scraping_stats()
        print(f"📊 Partial Results:")
        print(f"   Total legal acts: {partial_stats['total_acts_in_db']}")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()