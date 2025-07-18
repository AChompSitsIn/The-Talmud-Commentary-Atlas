#!/usr/bin/env python3
"""
Corrected Talmudic Commentary Extractor
Final version with proper filtering and structure handling.
"""

import pymongo
import json
import os
from collections import defaultdict
import re

class TalmudExtractor:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["sefaria"]
        self.collection = self.db["texts"]
        
        # Babylonian Talmud tractates
        self.talmudic_tractates = [
            "Berakhot", "Shabbat", "Eruvin", "Pesachim", "Yoma", "Sukkah", 
            "Beitzah", "Rosh Hashanah", "Taanit", "Megillah", "Moed Katan", 
            "Chagigah", "Yevamot", "Ketubot", "Nedarim", "Nazir", "Sotah", 
            "Gittin", "Kiddushin", "Bava Kamma", "Bava Metzia", "Bava Batra", 
            "Sanhedrin", "Makkot", "Shevuot", "Avodah Zarah", "Horayot", 
            "Zevachim", "Menachot", "Chullin", "Bekhorot", "Arakhin", 
            "Temurah", "Keritot", "Meilah", "Niddah"
        ]
        
        self.extraction_stats = {
            'total_documents': 0,
            'successful_extractions': 0,
            'scholars_found': set(),
            'tractates_found': set(),
            'total_sections': 0,
            'total_text_blocks': 0
        }
    
    def find_talmudic_commentaries(self):
        """Find all Talmudic commentary documents."""
        print("=== FINDING TALMUDIC COMMENTARIES ===")
        
        # Create regex pattern for Talmudic tractates
        tractate_pattern = "|".join(self.talmudic_tractates)
        pattern = {
            "title": {
                "$regex": f"^(.+) on ({tractate_pattern})$", 
                "$options": "i"
            },
            "language": "he"  # Only Hebrew content
        }
        
        documents = list(self.collection.find(pattern))
        print(f"Found {len(documents)} Talmudic commentary documents")
        
        return documents
    
    def extract_hebrew_content(self, doc):
        """Extract Hebrew content from a document."""
        title = doc['title']
        chapter = doc.get('chapter', {})
        
        hebrew_content = {}
        
        if isinstance(chapter, list):
            # Handle list structure (like Rashi, Tosafot)
            for i, section in enumerate(chapter):
                if isinstance(section, list) and section:
                    # Check if content is Hebrew
                    text_content = []
                    for item in section:
                        if isinstance(item, str) and self.is_hebrew(item):
                            text_content.append(item)
                    
                    if text_content:
                        hebrew_content[f"section_{i+1}"] = text_content
        
        elif isinstance(chapter, dict):
            # Handle dict structure (like Meiri)
            for key, value in chapter.items():
                if isinstance(value, list) and value:
                    # Check if content is Hebrew
                    text_content = []
                    for item in value:
                        if isinstance(item, str) and self.is_hebrew(item):
                            text_content.append(item)
                    
                    if text_content:
                        hebrew_content[key] = text_content
        
        return hebrew_content
    
    def is_hebrew(self, text):
        """Check if text contains Hebrew characters."""
        if not isinstance(text, str) or not text.strip():
            return False
        
        # Hebrew Unicode range: 0x0590-0x05FF
        hebrew_chars = sum(1 for char in text if 0x0590 <= ord(char) <= 0x05FF)
        return hebrew_chars > 0
    
    def extract_all_commentaries(self):
        """Extract all Talmudic commentaries."""
        print("=== EXTRACTING ALL TALMUDIC COMMENTARIES ===")
        
        documents = self.find_talmudic_commentaries()
        self.extraction_stats['total_documents'] = len(documents)
        
        # Create output directory
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(output_dir, exist_ok=True)
        
        successful_extractions = {}
        
        for doc in documents:
            title = doc['title']
            
            # Extract scholar and tractate
            try:
                scholar, tractate = title.split(' on ')
                self.extraction_stats['scholars_found'].add(scholar)
                self.extraction_stats['tractates_found'].add(tractate)
            except ValueError:
                print(f"  Error parsing title: {title}")
                continue
            
            # Extract Hebrew content
            hebrew_content = self.extract_hebrew_content(doc)
            
            if hebrew_content:
                # Convert to API format
                api_format = {}
                for key, content in hebrew_content.items():
                    api_key = f"{scholar.replace(' ', '_')}_on_{tractate}.{key}"
                    api_format[api_key] = content
                
                # Save to file
                scholar_dir = os.path.join(output_dir, scholar.replace(' ', '_'))
                os.makedirs(scholar_dir, exist_ok=True)
                
                filename = f"{tractate}.json"
                filepath = os.path.join(scholar_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(api_format, f, ensure_ascii=False, indent=2)
                
                section_count = len(hebrew_content)
                text_block_count = sum(len(content) for content in hebrew_content.values())
                
                self.extraction_stats['total_sections'] += section_count
                self.extraction_stats['total_text_blocks'] += text_block_count
                self.extraction_stats['successful_extractions'] += 1
                
                successful_extractions[title] = {
                    'sections': section_count,
                    'text_blocks': text_block_count,
                    'file_path': filepath
                }
                
                print(f"  ✓ {title}: {section_count} sections, {text_block_count} text blocks")
        
        return successful_extractions
    
    def generate_extraction_report(self, successful_extractions):
        """Generate detailed extraction report."""
        print("\n=== EXTRACTION REPORT ===")
        print(f"Total documents processed: {self.extraction_stats['total_documents']}")
        print(f"Successful extractions: {self.extraction_stats['successful_extractions']}")
        print(f"Success rate: {self.extraction_stats['successful_extractions']/self.extraction_stats['total_documents']*100:.1f}%")
        print(f"Unique scholars found: {len(self.extraction_stats['scholars_found'])}")
        print(f"Tractates covered: {len(self.extraction_stats['tractates_found'])}")
        print(f"Total sections extracted: {self.extraction_stats['total_sections']:,}")
        print(f"Total text blocks extracted: {self.extraction_stats['total_text_blocks']:,}")
        
        print(f"\nTop 20 scholars by extractions:")
        scholar_extractions = defaultdict(int)
        scholar_text_blocks = defaultdict(int)
        
        for title, data in successful_extractions.items():
            scholar = title.split(' on ')[0]
            scholar_extractions[scholar] += 1
            scholar_text_blocks[scholar] += data['text_blocks']
        
        for scholar, count in sorted(scholar_extractions.items(), key=lambda x: x[1], reverse=True)[:20]:
            text_blocks = scholar_text_blocks[scholar]
            print(f"  {scholar}: {count} tractates, {text_blocks:,} text blocks")
        
        # Save detailed report
        report_data = {
            'extraction_stats': {
                'total_documents': self.extraction_stats['total_documents'],
                'successful_extractions': self.extraction_stats['successful_extractions'],
                'success_rate': round(self.extraction_stats['successful_extractions']/self.extraction_stats['total_documents']*100, 1),
                'scholars_found': sorted(list(self.extraction_stats['scholars_found'])),
                'tractates_found': sorted(list(self.extraction_stats['tractates_found'])),
                'total_sections': self.extraction_stats['total_sections'],
                'total_text_blocks': self.extraction_stats['total_text_blocks']
            },
            'scholar_summary': {
                scholar: {
                    'tractates': scholar_extractions[scholar],
                    'text_blocks': scholar_text_blocks[scholar]
                }
                for scholar in sorted(scholar_extractions.keys())
            },
            'successful_extractions': successful_extractions
        }
        
        report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extraction_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\nDetailed report saved to: {report_path}")
        
        return report_data
    
    def close(self):
        """Close database connection."""
        self.client.close()

def main():
    """Main execution function."""
    extractor = TalmudExtractor()
    
    try:
        successful_extractions = extractor.extract_all_commentaries()
        report_data = extractor.generate_extraction_report(successful_extractions)
        return report_data
    finally:
        extractor.close()

if __name__ == "__main__":
    main()