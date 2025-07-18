#!/usr/bin/env python3
"""
Comprehensive Summary of Corrected MongoDB Analysis
Provides detailed overview of all extracted Talmudic commentary data.
"""

import json
import os
from collections import defaultdict
import re

class ComprehensiveAnalyzer:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        self.report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extraction_report.json")

        # Load extraction report
        with open(self.report_path, 'r', encoding='utf-8') as f:
            self.report = json.load(f)

        self.stats = {
            'total_scholars': 0,
            'total_tractates': 0,
            'total_files': 0,
            'total_words': 0,
            'total_sections': 0,
            'total_text_blocks': 0,
            'scholar_details': {},
            'tractate_coverage': {},
            'word_distribution': {},
            'section_distribution': {}
        }

    def count_words_in_text(self, text):
        """Count Hebrew words in text."""
        if not isinstance(text, str):
            return 0

        # Remove HTML tags and special characters
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'[^\u0590-\u05FF\s]', ' ', clean_text)

        # Split on whitespace and count non-empty words
        words = [word.strip() for word in clean_text.split() if word.strip()]
        return len(words)

    def analyze_extracted_data(self):
        """Analyze all extracted data files."""
        print("=== ANALYZING EXTRACTED DATA ===")

        for scholar_dir in os.listdir(self.data_dir):
            scholar_path = os.path.join(self.data_dir, scholar_dir)
            if not os.path.isdir(scholar_path):
                continue

            scholar_name = scholar_dir.replace('_', ' ')
            print(f"Processing {scholar_name}...")

            scholar_stats = {
                'tractates': 0,
                'files': 0,
                'words': 0,
                'sections': 0,
                'text_blocks': 0,
                'tractate_list': []
            }

            for file_name in os.listdir(scholar_path):
                if not file_name.endswith('.json'):
                    continue

                tractate_name = file_name.replace('.json', '')
                file_path = os.path.join(scholar_path, file_name)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    file_word_count = 0
                    file_section_count = len(data)
                    file_text_blocks = 0

                    for section_key, content in data.items():
                        if isinstance(content, list):
                            file_text_blocks += len(content)
                            for text_block in content:
                                file_word_count += self.count_words_in_text(text_block)

                    scholar_stats['tractates'] += 1
                    scholar_stats['files'] += 1
                    scholar_stats['words'] += file_word_count
                    scholar_stats['sections'] += file_section_count
                    scholar_stats['text_blocks'] += file_text_blocks
                    scholar_stats['tractate_list'].append(tractate_name)

                    # Track tractate coverage
                    if tractate_name not in self.stats['tractate_coverage']:
                        self.stats['tractate_coverage'][tractate_name] = []
                    self.stats['tractate_coverage'][tractate_name].append(scholar_name)

                except Exception as e:
                    print(f"  Error processing {file_path}: {e}")

            if scholar_stats['files'] > 0:
                self.stats['scholar_details'][scholar_name] = scholar_stats
                self.stats['total_scholars'] += 1
                self.stats['total_files'] += scholar_stats['files']
                self.stats['total_words'] += scholar_stats['words']
                self.stats['total_sections'] += scholar_stats['sections']
                self.stats['total_text_blocks'] += scholar_stats['text_blocks']

                # Track word distribution
                self.stats['word_distribution'][scholar_name] = scholar_stats['words']
                self.stats['section_distribution'][scholar_name] = scholar_stats['sections']

        self.stats['total_tractates'] = len(self.stats['tractate_coverage'])

        print(f"Analysis complete: {self.stats['total_scholars']} scholars, {self.stats['total_tractates']} tractates")

    def generate_comprehensive_summary(self):
        """Generate detailed summary report."""
        print("\n" + "="*80)
        print("COMPREHENSIVE TALMUDIC COMMENTARY ANALYSIS SUMMARY")
        print("="*80)

        # Overall Statistics
        print(f"OVERALL STATISTICS")
        print(f"{'='*40}")
        print(f"Total Scholars Analyzed: {self.stats['total_scholars']:,}")
        print(f"Total Tractates Covered: {self.stats['total_tractates']:,}")
        print(f"Total Files Extracted: {self.stats['total_files']:,}")
        print(f"Total Hebrew Words: {self.stats['total_words']:,}")
        print(f"Total Commentary Sections: {self.stats['total_sections']:,}")
        print(f"Total Text Blocks: {self.stats['total_text_blocks']:,}")
        print(f"Success Rate: {self.report['extraction_stats']['success_rate']:.1f}%")

        # Top Scholars by Word Count
        print(f"TOP 20 SCHOLARS BY WORD COUNT")
        print(f"{'='*50}")
        top_scholars = sorted(self.stats['word_distribution'].items(), key=lambda x: x[1], reverse=True)
        for i, (scholar, word_count) in enumerate(top_scholars[:20], 1):
            tractate_count = self.stats['scholar_details'][scholar]['tractates']
            print(f"{i:2d}. {scholar:<30} {word_count:>8,} words ({tractate_count} tractates)")

        # Tractate Coverage Analysis
        print(f"TRACTATE COVERAGE ANALYSIS")
        print(f"{'='*45}")
        tractate_scholars = sorted(self.stats['tractate_coverage'].items(),
                                 key=lambda x: len(x[1]), reverse=True)

        print(f"{'Tractate':<15} {'Scholars':<8} {'Commentary Sources'}")
        print(f"{'-'*15} {'-'*8} {'-'*50}")

        for tractate, scholars in tractate_scholars:
            scholar_count = len(scholars)
            scholar_preview = ", ".join(scholars[:3])
            if len(scholars) > 3:
                scholar_preview += f" (+{len(scholars)-3} more)"
            print(f"{tractate:<15} {scholar_count:<8} {scholar_preview}")

        # Scholar Categories
        print(f"SCHOLAR CATEGORIES")
        print(f"{'='*35}")

        # Categorize scholars
        rishonim = []
        acharonim = []
        modern = []

        for scholar in self.stats['scholar_details'].keys():
            scholar_lower = scholar.lower()
            if any(name in scholar_lower for name in ['rashi', 'tosafot', 'ramban', 'rashba', 'ritva', 'ran', 'rosh', 'meiri', 'nimukei']):
                rishonim.append(scholar)
            elif any(name in scholar_lower for name in ['steinsaltz', 'ben yehoyada', 'gilyon hashas', 'penei yehoshua']):
                if 'steinsaltz' in scholar_lower:
                    modern.append(scholar)
                else:
                    acharonim.append(scholar)
            else:
                acharonim.append(scholar)

        print(f"Rishonim (Medieval): {len(rishonim)} scholars")
        print(f"Acharonim (Post-Medieval): {len(acharonim)} scholars")
        print(f"Modern: {len(modern)} scholars")

        # Content Volume Analysis
        print(f"CONTENT VOLUME ANALYSIS")
        print(f"{'='*40}")

        total_words = self.stats['total_words']
        avg_words_per_scholar = total_words / self.stats['total_scholars']
        avg_words_per_tractate = total_words / self.stats['total_tractates']
        avg_sections_per_scholar = self.stats['total_sections'] / self.stats['total_scholars']

        print(f"Average words per scholar: {avg_words_per_scholar:,.0f}")
        print(f"Average words per tractate: {avg_words_per_tractate:,.0f}")
        print(f"Average sections per scholar: {avg_sections_per_scholar:,.0f}")
        print(f"Average words per section: {total_words / self.stats['total_sections']:,.0f}")

        # Major Commentators Analysis
        print(f"MAJOR COMMENTATORS ANALYSIS")
        print(f"{'='*45}")

        major_commentators = {
            'Steinsaltz': 'Modern comprehensive commentary',
            'Maharsha': 'Combined halakhic and aggadic innovations',
            'Meiri': 'Systematic medieval commentary',
            'Ramban': 'Combined Talmudic works and innovations',
            'Rabbi Akiva Eiger': 'Combined critical notes and glosses',
            'Rashash': 'Textual corrections and brief notes',
            'Penei Yehoshua': 'Analytical commentary'
        }

        for commentator, description in major_commentators.items():
            if commentator in self.stats['scholar_details']:
                stats = self.stats['scholar_details'][commentator]
                print(f"{commentator:<20} {stats['tractates']:>2} tractates, {stats['words']:>7,} words")
                print(f"{'':>20} {description}")
                print()

        # Data Quality Metrics
        print(f"DATA QUALITY METRICS")
        print(f"{'='*35}")

        non_empty_files = sum(1 for scholar_stats in self.stats['scholar_details'].values()
                            if scholar_stats['words'] > 0)
        substantial_scholars = sum(1 for scholar_stats in self.stats['scholar_details'].values()
                                 if scholar_stats['words'] > 1000)

        print(f"Files with content: {non_empty_files}/{self.stats['total_files']} ({non_empty_files/self.stats['total_files']*100:.1f}%)")
        print(f"Scholars with substantial content (>1000 words): {substantial_scholars}")
        print(f"Average text blocks per section: {self.stats['total_text_blocks']/self.stats['total_sections']:.1f}")

        # Comparison with Original Analysis
        print(f"COMPARISON WITH ORIGINAL ANALYSIS")
        print(f"{'='*45}")
        print(f"Original MongoDB Analysis:")
        print(f"  - Scholars found: 11")
        print(f"  - Text sections: 3,188")
        print(f"  - Success rate: ~20%")
        print(f"\nCorrected MongoDB Analysis:")
        print(f"  - Scholars found: {self.stats['total_scholars']}")
        print(f"  - Text sections: {self.stats['total_sections']:,}")
        print(f"  - Success rate: {self.report['extraction_stats']['success_rate']:.1f}%")
        print(f"\nImprovement:")
        print(f"  - {self.stats['total_scholars']/11:.1f}x more scholars")
        print(f"  - {self.stats['total_sections']/3188:.1f}x more text sections")
        print(f"  - {self.report['extraction_stats']['success_rate']/20:.1f}x better success rate")

        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE")
        print("="*80)

    def save_detailed_report(self):
        """Save detailed analysis to JSON file."""
        detailed_report = {
            'summary_stats': self.stats,
            'extraction_report': self.report,
            'analysis_metadata': {
                'total_scholars': self.stats['total_scholars'],
                'total_tractates': self.stats['total_tractates'],
                'total_words': self.stats['total_words'],
                'total_sections': self.stats['total_sections'],
                'analysis_date': '2025-01-17'
            }
        }

        report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "comprehensive_analysis_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, ensure_ascii=False, indent=2)

        print(f"\nDetailed report saved to: {report_path}")

def main():
    """Main execution function."""
    analyzer = ComprehensiveAnalyzer()
    analyzer.analyze_extracted_data()
    analyzer.generate_comprehensive_summary()
    analyzer.save_detailed_report()

if __name__ == "__main__":
    main()
