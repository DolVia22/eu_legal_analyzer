import sqlite3
import pandas as pd
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime
import logging
import pickle
import os

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Get the project root directory (two levels up from this file)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(project_root, "data", "eu_legal_analyzer.db")
        self.db_path = db_path
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Legal acts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS legal_acts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    celex_number TEXT UNIQUE,
                    title TEXT NOT NULL,
                    document_type TEXT,
                    subject_matter TEXT,
                    directory_code TEXT,
                    date_document DATE,
                    date_force DATE,
                    date_end_validity DATE,
                    content TEXT,
                    summary TEXT,
                    keywords TEXT,
                    url TEXT,
                    embedding BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Company profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS company_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    industry TEXT,
                    business_description TEXT,
                    company_size TEXT,
                    location TEXT,
                    business_activities TEXT,
                    compliance_areas TEXT,
                    risk_profile TEXT,
                    embedding BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Analysis results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    legal_act_id INTEGER,
                    relevance_score REAL,
                    reasoning TEXT,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES company_profiles (id),
                    FOREIGN KEY (legal_act_id) REFERENCES legal_acts (id)
                )
            ''')
            
            conn.commit()
    
    def save_legal_act(self, legal_act_data: Dict) -> int:
        """Save a legal act to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO legal_acts 
                (celex_number, title, document_type, subject_matter, directory_code,
                 date_document, date_force, date_end_validity, content, summary, 
                 keywords, url, embedding, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                legal_act_data.get('celex_number'),
                legal_act_data.get('title'),
                legal_act_data.get('document_type'),
                legal_act_data.get('subject_matter'),
                legal_act_data.get('directory_code'),
                legal_act_data.get('date_document'),
                legal_act_data.get('date_force'),
                legal_act_data.get('date_end_validity'),
                legal_act_data.get('content'),
                legal_act_data.get('summary'),
                legal_act_data.get('keywords'),
                legal_act_data.get('url'),
                legal_act_data.get('embedding'),
                datetime.now()
            ))
            
            return cursor.lastrowid
    
    def save_company_profile(self, profile_data: Dict) -> int:
        """Save a company profile to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO company_profiles 
                (company_name, industry, business_description, company_size, location,
                 business_activities, compliance_areas, risk_profile, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile_data.get('company_name'),
                profile_data.get('industry'),
                profile_data.get('business_description'),
                profile_data.get('company_size'),
                profile_data.get('location'),
                profile_data.get('business_activities'),
                profile_data.get('compliance_areas'),
                profile_data.get('risk_profile'),
                profile_data.get('embedding')
            ))
            
            return cursor.lastrowid
    
    def get_legal_acts(self, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve legal acts from the database"""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM legal_acts ORDER BY created_at DESC"
            if limit:
                query += f" LIMIT {limit}"
            
            df = pd.read_sql_query(query, conn)
            return df.to_dict('records')
    
    def get_company_profiles(self) -> List[Dict]:
        """Retrieve company profiles from the database"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query("SELECT * FROM company_profiles ORDER BY created_at DESC", conn)
            return df.to_dict('records')
    
    def save_analysis_result(self, company_id: int, legal_act_id: int, 
                           relevance_score: float, reasoning: str):
        """Save analysis result to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analysis_results 
                (company_id, legal_act_id, relevance_score, reasoning)
                VALUES (?, ?, ?, ?)
            ''', (company_id, legal_act_id, relevance_score, reasoning))
    
    def get_analysis_results(self, company_id: int, limit: int = 20) -> List[Dict]:
        """Get analysis results for a company"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT ar.*, la.title, la.celex_number, la.document_type, 
                       la.subject_matter, la.url
                FROM analysis_results ar
                JOIN legal_acts la ON ar.legal_act_id = la.id
                WHERE ar.company_id = ?
                ORDER BY ar.relevance_score DESC
                LIMIT ?
            '''
            df = pd.read_sql_query(query, conn, params=(company_id, limit))
            return df.to_dict('records')
    
    def search_legal_acts(self, search_term: str, limit: int = 50) -> List[Dict]:
        """Search legal acts by title, content, or keywords"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT * FROM legal_acts 
                WHERE title LIKE ? OR content LIKE ? OR keywords LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            '''
            search_pattern = f"%{search_term}%"
            df = pd.read_sql_query(query, conn, params=(search_pattern, search_pattern, search_pattern, limit))
            return df.to_dict('records')
    
    def get_legal_act_count(self) -> int:
        """Get total number of legal acts in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM legal_acts")
            return cursor.fetchone()[0]