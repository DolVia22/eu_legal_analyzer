#!/usr/bin/env python3
"""
Test script to verify all modules are working correctly
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_database():
    """Test database functionality"""
    print("Testing database module...")
    try:
        from database.db_manager import DatabaseManager
        db = DatabaseManager("data/test.db")
        print("✅ Database module loaded successfully")
        
        # Test basic operations
        count = db.get_legal_act_count()
        print(f"✅ Legal acts count: {count}")
        
        profiles = db.get_company_profiles()
        print(f"✅ Company profiles count: {len(profiles)}")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_scraper():
    """Test scraper functionality"""
    print("\nTesting scraper module...")
    try:
        from scraper.eurlex_scraper import EURLexScraper
        scraper = EURLexScraper()
        print("✅ Scraper module loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False

def test_text_analyzer():
    """Test text analyzer functionality"""
    print("\nTesting text analyzer module...")
    try:
        from models.text_analyzer import TextAnalyzer
        print("Loading AI models (this may take a while)...")
        analyzer = TextAnalyzer()
        print("✅ Text analyzer module loaded successfully")
        
        # Test embedding generation
        test_text = "This is a test document about data protection."
        embedding = analyzer.generate_embedding(test_text)
        print(f"✅ Embedding generated successfully (dimension: {len(embedding)})")
        
        return True
    except Exception as e:
        print(f"❌ Text analyzer test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing EU Legal Analyzer Modules\n")
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    tests = [
        test_database,
        test_scraper,
        test_text_analyzer
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! The application should work correctly.")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()