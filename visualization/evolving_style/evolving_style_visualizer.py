#!/usr/bin/env python3
"""
Evolving Style of Commentary Visualizer
Analyzes whether later commentators (Acharonim) wrote more or less on average 
per tractate than their predecessors (Rishonim).
"""

import json
import os
import re
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict

class EvolvingStyleVisualizer:
    def __init__(self):
        # Navigate from visualization/evolving_style/ to project root, then to data/
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_dir = os.path.join(project_root, "data")
        self.output_dir = os.path.dirname(os.path.abspath(__file__))  # Output to same directory as script
        
        # Scholar categorization (same as center of gravity)
        self.rishonim_scholars = [
            "Rif", "Rabbeinu_Chananel", "Rabbeinu_Gershom", "Rav_Nissim_Gaon",
            "Rabbeinu_Zerachya_ha_Levi",  # Baal HaMaor
            "Rabbeinu_Yehonatan_of_Lunel", "Rabbeinu_Yonah", "Rabbeinu_Efrayim",
            "Ramban", "Rashba", "Ritva", "Ran", "Meiri", "Rosh", "Nimukei_Yosef",
            "Yad_Ramah", "Tosafot_Rid", "Tosafot_Ri_HaZaken", "Tosafot_HaRosh",
            "Tosafot_Chad_Mikamei", "Tosafot_Yeshanim", "Tosafot_Shantz",
            "Chiddushei_HaRa'ah", "Chiddushei_HaRambam"
        ]
        
        # Modern color palette
        self.colors = {
            'rishonim': '#2E86AB',      # Deep blue
            'acharonim': '#A23B72',     # Deep magenta
            'background': '#FAFAFA',    # Light gray
            'text': '#2C3E50',          # Dark blue-gray
            'accent': '#34495E'         # Darker blue-gray
        }
        
        # Data storage
        self.period_data = {
            'Rishonim': {
                'total_words': 0,
                'total_tractates': 0,
                'scholars': set(),
                'tractate_counts': defaultdict(int),
                'word_counts_per_tractate': []
            },
            'Acharonim': {
                'total_words': 0,
                'total_tractates': 0,
                'scholars': set(),
                'tractate_counts': defaultdict(int),
                'word_counts_per_tractate': []
            }
        }
    
    def count_words_in_text(self, text: str) -> int:
        """Count Hebrew words in text."""
        if not isinstance(text, str):
            return 0
        
        # Remove HTML tags and special characters
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'[^\u0590-\u05FF\s]', ' ', clean_text)
        
        # Split on whitespace and count non-empty words
        words = [word.strip() for word in clean_text.split() if word.strip()]
        return len(words)
    
    def load_and_analyze_data(self):
        """Load scholar data and calculate average words per tractate."""
        print("Loading and analyzing scholar data...")
        
        # Get all scholars in data directory
        all_scholars = [d for d in os.listdir(self.data_dir) 
                       if os.path.isdir(os.path.join(self.data_dir, d))]
        
        # Process each scholar
        for scholar_dir in all_scholars:
            scholar_path = os.path.join(self.data_dir, scholar_dir)
            if not os.path.isdir(scholar_path):
                continue
            
            scholar_name = scholar_dir
            period = "Rishonim" if scholar_name in self.rishonim_scholars else "Acharonim"
            
            self.period_data[period]['scholars'].add(scholar_name)
            
            # Process each tractate file
            for file_name in os.listdir(scholar_path):
                if not file_name.endswith('.json'):
                    continue
                
                tractate_name = file_name.replace('.json', '')
                file_path = os.path.join(scholar_path, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Count words in this tractate
                    tractate_word_count = 0
                    for section_key, content in data.items():
                        if isinstance(content, list):
                            for text_block in content:
                                tractate_word_count += self.count_words_in_text(text_block)
                    
                    # Add to period statistics
                    if tractate_word_count > 0:
                        self.period_data[period]['total_words'] += tractate_word_count
                        self.period_data[period]['total_tractates'] += 1
                        self.period_data[period]['tractate_counts'][tractate_name] += 1
                        self.period_data[period]['word_counts_per_tractate'].append(tractate_word_count)
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        # Calculate averages
        for period in ['Rishonim', 'Acharonim']:
            data = self.period_data[period]
            data['average_words_per_tractate'] = (
                data['total_words'] / data['total_tractates'] 
                if data['total_tractates'] > 0 else 0
            )
            
            # Calculate median and standard deviation
            if data['word_counts_per_tractate']:
                data['median_words_per_tractate'] = np.median(data['word_counts_per_tractate'])
                data['std_words_per_tractate'] = np.std(data['word_counts_per_tractate'])
            else:
                data['median_words_per_tractate'] = 0
                data['std_words_per_tractate'] = 0
        
        print(f"Analyzed {len(self.period_data['Rishonim']['scholars'])} Rishonim scholars")
        print(f"Analyzed {len(self.period_data['Acharonim']['scholars'])} Acharonim scholars")
    
    def create_evolving_style_visualization(self):
        """Create the comparative bar chart."""
        
        # Prepare data
        periods = ['Rishonim\n(Medieval)', 'Acharonim\n(Post-Medieval/Modern)']
        averages = [
            self.period_data['Rishonim']['average_words_per_tractate'],
            self.period_data['Acharonim']['average_words_per_tractate']
        ]
        
        # Calculate percentage change
        pct_change = ((averages[1] - averages[0]) / averages[0] * 100) if averages[0] > 0 else 0
        
        # Create the figure
        fig = go.Figure()
        
        # Add bars
        colors = [self.colors['rishonim'], self.colors['acharonim']]
        
        fig.add_trace(go.Bar(
            x=periods,
            y=averages,
            marker_color=colors,
            text=[f'{avg:,.0f}<br>words' for avg in averages],
            textposition='outside',
            textfont=dict(size=16, weight='bold'),
            width=0.5
        ))
        
        # Add annotations for additional statistics
        for i, period_key in enumerate(['Rishonim', 'Acharonim']):
            data = self.period_data[period_key]
            
            # Add annotation below each bar
            fig.add_annotation(
                x=periods[i],
                y=-5000,  # Below x-axis
                text=f"<b>{len(data['scholars'])} scholars</b><br>" +
                     f"{data['total_tractates']:,} tractate commentaries<br>" +
                     f"Median: {data['median_words_per_tractate']:,.0f} words",
                showarrow=False,
                font=dict(size=11, color=self.colors['text']),
                yanchor='top'
            )
        
        # Add percentage change annotation
        if pct_change != 0:
            fig.add_annotation(
                x=1,  # Position between bars
                y=max(averages) * 0.5,
                text=f"<b>{pct_change:+.1f}%</b><br>change",
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=2,
                arrowcolor=self.colors['accent'],
                ax=-40,
                ay=0,
                font=dict(size=18, color=self.colors['accent']),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor=self.colors['accent'],
                borderwidth=2,
                borderpad=8
            )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text='<b>The Evolving Style of Commentary</b><br>' +
                     '<span style="font-size: 16px;">Average Commentary Volume per Tractate by Period</span>',
                x=0.5,
                font=dict(size=26)
            ),
            xaxis=dict(
                title=dict(
                    text='<b>Historical Period</b>',
                    font=dict(size=18)
                ),
                tickfont=dict(size=16),
                fixedrange=True
            ),
            yaxis=dict(
                title=dict(
                    text='<b>Average Words per Tractate Commentary</b>',
                    font=dict(size=18)
                ),
                tickfont=dict(size=14),
                range=[0, max(averages) * 1.25],
                fixedrange=True
            ),
            width=900,
            height=700,
            template='plotly_white',
            margin=dict(l=100, r=100, t=120, b=150),
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False
        )
        
        # Add a subtle grid
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200,200,200,0.3)'
        )
        
        # Save the figure
        output_path_html = os.path.join(self.output_dir, "evolving_style.html")
        output_path_png = os.path.join(self.output_dir, "evolving_style.png")
        
        fig.write_html(output_path_html)
        fig.write_image(output_path_png, width=900, height=700, scale=2)
        
        # Save detailed statistics
        detailed_stats = {
            "Rishonim": {
                "scholars": list(self.period_data['Rishonim']['scholars']),
                "total_scholars": len(self.period_data['Rishonim']['scholars']),
                "total_words": self.period_data['Rishonim']['total_words'],
                "total_tractates": self.period_data['Rishonim']['total_tractates'],
                "average_words_per_tractate": self.period_data['Rishonim']['average_words_per_tractate'],
                "median_words_per_tractate": self.period_data['Rishonim']['median_words_per_tractate'],
                "std_words_per_tractate": self.period_data['Rishonim']['std_words_per_tractate']
            },
            "Acharonim": {
                "scholars": list(self.period_data['Acharonim']['scholars']),
                "total_scholars": len(self.period_data['Acharonim']['scholars']),
                "total_words": self.period_data['Acharonim']['total_words'],
                "total_tractates": self.period_data['Acharonim']['total_tractates'],
                "average_words_per_tractate": self.period_data['Acharonim']['average_words_per_tractate'],
                "median_words_per_tractate": self.period_data['Acharonim']['median_words_per_tractate'],
                "std_words_per_tractate": self.period_data['Acharonim']['std_words_per_tractate']
            },
            "analysis": {
                "percentage_change": pct_change,
                "insight": "Acharonim wrote more extensively" if pct_change > 0 else "Rishonim wrote more extensively"
            }
        }
        
        with open(os.path.join(self.output_dir, "evolving_style_data.json"), 'w', encoding='utf-8') as f:
            json.dump(detailed_stats, f, ensure_ascii=False, indent=2)
        
        print(f"\nVisualization saved to {self.output_dir}")
        print("Files generated:")
        print("- evolving_style.html (interactive)")
        print("- evolving_style.png (static)")
        print("- evolving_style_data.json (detailed statistics)")
        
        # Print summary
        print("\nSummary:")
        print(f"Rishonim average: {averages[0]:,.0f} words per tractate")
        print(f"Acharonim average: {averages[1]:,.0f} words per tractate")
        print(f"Change: {pct_change:+.1f}%")

def main():
    """Main execution function."""
    visualizer = EvolvingStyleVisualizer()
    visualizer.load_and_analyze_data()
    visualizer.create_evolving_style_visualization()

if __name__ == "__main__":
    main()