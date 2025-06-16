#!/usr/bin/env python3
"""
Script to populate the database with sample legal acts for demonstration
"""

import sys
import os
from pathlib import Path
import pickle

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from database.db_manager import DatabaseManager
from models.text_analyzer import TextAnalyzer

def create_sample_legal_acts():
    """Create sample legal acts for demonstration"""
    
    sample_acts = [
        {
            'celex_number': '32016R0679',
            'title': 'General Data Protection Regulation (GDPR)',
            'document_type': 'REG',
            'subject_matter': 'Data protection and privacy',
            'directory_code': '13.10.01',
            'date_document': '2016-04-27',
            'date_force': '2018-05-25',
            'content': '''The General Data Protection Regulation (GDPR) is a regulation in EU law on data protection and privacy in the European Union and the European Economic Area. It also addresses the transfer of personal data outside the EU and EEA areas. The GDPR aims primarily to give control to individuals over their personal data and to simplify the regulatory environment for international business by unifying the regulation within the EU.''',
            'summary': 'Regulation on data protection and privacy for individuals within the European Union',
            'keywords': 'data protection, privacy, personal data, GDPR, consent, data processing',
            'url': 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679'
        },
        {
            'celex_number': '32019R2088',
            'title': 'Sustainable Finance Disclosure Regulation (SFDR)',
            'document_type': 'REG',
            'subject_matter': 'Financial services and sustainability',
            'directory_code': '09.10.10',
            'date_document': '2019-11-27',
            'date_force': '2021-03-10',
            'content': '''This Regulation lays down harmonised rules for financial market participants and financial advisers on transparency with regard to the integration of sustainability risks and the consideration of adverse sustainability impacts in their processes and the provision of sustainability‐related information with respect to financial products.''',
            'summary': 'Regulation on sustainability-related disclosures in the financial services sector',
            'keywords': 'sustainable finance, ESG, disclosure, financial services, sustainability risks',
            'url': 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R2088'
        },
        {
            'celex_number': '32022R2065',
            'title': 'Digital Services Act (DSA)',
            'document_type': 'REG',
            'subject_matter': 'Digital services and online platforms',
            'directory_code': '13.20.10',
            'date_document': '2022-10-19',
            'date_force': '2024-02-17',
            'content': '''The Digital Services Act establishes a comprehensive framework for the oversight of digital services in the EU. It sets out obligations for digital service providers to address illegal content, protect users' fundamental rights, and ensure transparency in content moderation.''',
            'summary': 'Regulation establishing rules for digital services and online platforms',
            'keywords': 'digital services, online platforms, content moderation, illegal content, transparency',
            'url': 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2065'
        },
        {
            'celex_number': '32019L2161',
            'title': 'Consumer Rights Directive Amendment',
            'document_type': 'DIR',
            'subject_matter': 'Consumer protection and digital content',
            'directory_code': '15.20.10',
            'date_document': '2019-11-27',
            'date_force': '2022-01-01',
            'content': '''This Directive amends the Consumer Rights Directive to better protect consumers in digital transactions, including rules for digital content and digital services, and enhanced transparency requirements for online marketplaces.''',
            'summary': 'Directive enhancing consumer protection in digital transactions',
            'keywords': 'consumer protection, digital content, online marketplace, transparency, consumer rights',
            'url': 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019L2161'
        },
        {
            'celex_number': '32020R0852',
            'title': 'EU Taxonomy Regulation',
            'document_type': 'REG',
            'subject_matter': 'Environmental sustainability and finance',
            'directory_code': '09.10.20',
            'date_document': '2020-06-18',
            'date_force': '2021-07-12',
            'content': '''This Regulation establishes the criteria for determining whether an economic activity qualifies as environmentally sustainable for the purposes of establishing the degree to which an investment is environmentally sustainable.''',
            'summary': 'Regulation establishing criteria for environmentally sustainable economic activities',
            'keywords': 'taxonomy, environmental sustainability, green finance, sustainable investment, climate',
            'url': 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32020R0852'
        },
        {
            'celex_number': '32022R0868',
            'title': 'Markets in Crypto-Assets Regulation (MiCA)',
            'document_type': 'REG',
            'subject_matter': 'Cryptocurrency and digital assets',
            'directory_code': '09.10.30',
            'date_document': '2022-05-31',
            'date_force': '2024-06-30',
            'content': '''This Regulation establishes uniform rules for the issuance, offering to the public and admission to trading of crypto-assets, and for the provision of services related to crypto-assets in the Union.''',
            'summary': 'Regulation on markets in crypto-assets and digital currencies',
            'keywords': 'cryptocurrency, crypto-assets, digital currency, blockchain, financial regulation',
            'url': 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0868'
        },
        {
            'celex_number': '32021L2101',
            'title': 'Whistleblower Protection Directive',
            'document_type': 'DIR',
            'subject_matter': 'Whistleblower protection and reporting',
            'directory_code': '18.10.10',
            'date_document': '2019-10-23',
            'date_force': '2021-12-17',
            'content': '''This Directive establishes minimum standards for the protection of persons who report breaches of Union law, ensuring safe channels for reporting and protection against retaliation.''',
            'summary': 'Directive on the protection of persons who report breaches of Union law',
            'keywords': 'whistleblower, protection, reporting, retaliation, compliance, internal reporting',
            'url': 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019L1937'
        },
        {
            'celex_number': '32019R0881',
            'title': 'Cybersecurity Act',
            'document_type': 'REG',
            'subject_matter': 'Cybersecurity and digital security',
            'directory_code': '13.30.10',
            'date_document': '2019-04-17',
            'date_force': '2019-06-27',
            'content': '''This Regulation establishes a framework for European cybersecurity certification and strengthens the mandate of the European Union Agency for Cybersecurity (ENISA).''',
            'summary': 'Regulation on cybersecurity certification and ENISA mandate',
            'keywords': 'cybersecurity, certification, ENISA, digital security, cyber threats',
            'url': 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0881'
        }
    ]
    
    return sample_acts

def main():
    """Populate database with sample data"""
    print("🔄 Populating database with sample legal acts...")
    
    # Initialize components
    db = DatabaseManager()
    print("Loading AI models...")
    analyzer = TextAnalyzer()
    
    sample_acts = create_sample_legal_acts()
    
    saved_count = 0
    for act in sample_acts:
        try:
            print(f"Processing: {act['title']}")
            
            # Generate embedding for the legal act
            act_text = f"{act['title']} {act['summary']} {act['content']} {act['keywords']}"
            embedding = analyzer.generate_embedding(act_text)
            act['embedding'] = pickle.dumps(embedding)
            
            # Save to database
            act_id = db.save_legal_act(act)
            saved_count += 1
            print(f"✅ Saved with ID: {act_id}")
            
        except Exception as e:
            print(f"❌ Error saving {act['title']}: {e}")
    
    print(f"\n🎉 Successfully populated database with {saved_count} legal acts!")
    print("You can now run the application and see these acts in the analysis.")

if __name__ == "__main__":
    main()