#!/usr/bin/env python3
"""
Center of Gravity Visualizer
Analyzes the shifting focus of Talmudic commentary between Rishonim and Acharonim periods
by examining the distribution of commentary across the six orders (Sedarim) of the Talmud.
"""

import json
import os
import re
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict

class CenterOfGravityVisualizer:
    def __init__(self):
        # Navigate from visualization/center_of_gravity/ to project root, then to data/
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_dir = os.path.join(project_root, "data")
        self.output_dir = os.path.dirname(os.path.abspath(__file__))  # Output to same directory as script
        
        # Define the six orders and their tractates
        self.sedarim = {
            "Zeraim": ["Berakhot"],
            "Moed": ["Shabbat", "Eruvin", "Pesachim", "Yoma", "Sukkah", "Beitzah", 
                     "Rosh Hashanah", "Taanit", "Megillah", "Moed Katan", "Chagigah"],
            "Nashim": ["Yevamot", "Ketubot", "Nedarim", "Nazir", "Sotah", "Gittin", "Kiddushin"],
            "Nezikin": ["Bava Kamma", "Bava Metzia", "Bava Batra", "Sanhedrin", 
                        "Makkot", "Shevuot", "Avodah Zarah", "Horayot"],
            "Kodashim": ["Zevachim", "Menachot", "Chullin", "Bekhorot", "Arakhin", 
                         "Temurah", "Keritot", "Meilah", "Niddah"],
            "Tohorot": []  # No tractates from Tohorot in the Babylonian Talmud (except Niddah which is in Kodashim)
        }
        
        # Scholar categorization
        self.rishonim_scholars = [
            "Rif", "Rabbeinu_Chananel", "Rabbeinu_Gershom", "Rav_Nissim_Gaon",
            "Rabbeinu_Zerachya_ha_Levi",  # Baal HaMaor
            "Rabbeinu_Yehonatan_of_Lunel", "Rabbeinu_Yonah", "Rabbeinu_Efrayim",
            "Ramban", "Rashba", "Ritva", "Ran", "Meiri", "Rosh", "Nimukei_Yosef",
            "Yad_Ramah", "Tosafot_Rid", "Tosafot_Ri_HaZaken", "Tosafot_HaRosh",
            "Tosafot_Chad_Mikamei", "Tosafot_Yeshanim", "Tosafot_Shantz",
            "Chiddushei_HaRa'ah", "Chiddushei_HaRambam"
        ]
        
        # All others are Acharonim (including Modern)
        self.acharonim_scholars = []  # Will be populated dynamically
        
        # Modern color palette
        self.colors = {
            'rishonim': '#2E86AB',      # Deep blue
            'acharonim': '#A23B72',     # Deep magenta
            'zeraim': '#8E44AD',        # Purple
            'moed': '#27AE60',          # Green
            'nashim': '#E67E22',        # Orange
            'nezikin': '#E74C3C',       # Red
            'kodashim': '#3498DB',      # Light blue
            'tohorot': '#95A5A6'        # Gray (unused)
        }
        
        self.scholar_data = {}
        self.period_seder_distribution = {
            'Rishonim': defaultdict(int),
            'Acharonim': defaultdict(int)
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
    
    def get_seder_for_tractate(self, tractate: str) -> str:
        """Return which Seder a tractate belongs to."""
        for seder, tractates in self.sedarim.items():
            if tractate in tractates:
                return seder
        return None
    
    def load_and_analyze_data(self):
        """Load scholar data and analyze distribution by Seder."""
        print("Loading and analyzing scholar data...")
        
        # Get all scholars in data directory
        all_scholars = [d for d in os.listdir(self.data_dir) 
                       if os.path.isdir(os.path.join(self.data_dir, d))]
        
        # Categorize Acharonim (everyone not in Rishonim list)
        self.acharonim_scholars = [s for s in all_scholars if s not in self.rishonim_scholars]
        
        # Process each scholar
        for scholar_dir in all_scholars:
            scholar_path = os.path.join(self.data_dir, scholar_dir)
            if not os.path.isdir(scholar_path):
                continue
            
            scholar_name = scholar_dir
            period = "Rishonim" if scholar_name in self.rishonim_scholars else "Acharonim"
            
            # Process each tractate file
            for file_name in os.listdir(scholar_path):
                if not file_name.endswith('.json'):
                    continue
                
                tractate_name = file_name.replace('.json', '')
                seder = self.get_seder_for_tractate(tractate_name)
                
                if seder is None:
                    print(f"Warning: Tractate {tractate_name} not found in any Seder")
                    continue
                
                file_path = os.path.join(scholar_path, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Count words in this tractate
                    word_count = 0
                    for section_key, content in data.items():
                        if isinstance(content, list):
                            for text_block in content:
                                word_count += self.count_words_in_text(text_block)
                    
                    # Add to period-seder distribution
                    self.period_seder_distribution[period][seder] += word_count
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        print(f"Analyzed {len(self.rishonim_scholars)} Rishonim scholars")
        print(f"Analyzed {len(self.acharonim_scholars)} Acharonim scholars")
    
    def create_center_of_gravity_visualization(self):
        """Create the grouped bar chart showing distribution by Seder."""
        
        # Calculate percentages for each period
        rishonim_total = sum(self.period_seder_distribution['Rishonim'].values())
        acharonim_total = sum(self.period_seder_distribution['Acharonim'].values())
        
        # Prepare data for visualization
        sedarim_order = ["Zeraim", "Moed", "Nashim", "Nezikin", "Kodashim"]
        
        rishonim_percentages = []
        acharonim_percentages = []
        
        for seder in sedarim_order:
            rishonim_pct = (self.period_seder_distribution['Rishonim'][seder] / rishonim_total * 100) if rishonim_total > 0 else 0
            acharonim_pct = (self.period_seder_distribution['Acharonim'][seder] / acharonim_total * 100) if acharonim_total > 0 else 0
            
            rishonim_percentages.append(rishonim_pct)
            acharonim_percentages.append(acharonim_pct)
        
        # Create the grouped bar chart
        fig = go.Figure()
        
        # Add Rishonim bars
        fig.add_trace(go.Bar(
            name='Rishonim (Medieval)',
            x=sedarim_order,
            y=rishonim_percentages,
            marker_color=self.colors['rishonim'],
            text=[f'{pct:.1f}%' for pct in rishonim_percentages],
            textposition='outside',
            textfont=dict(size=12)
        ))
        
        # Add Acharonim bars
        fig.add_trace(go.Bar(
            name='Acharonim (Post-Medieval/Modern)',
            x=sedarim_order,
            y=acharonim_percentages,
            marker_color=self.colors['acharonim'],
            text=[f'{pct:.1f}%' for pct in acharonim_percentages],
            textposition='outside',
            textfont=dict(size=12)
        ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text='<b>The Shifting "Center of Gravity" in Talmudic Commentary</b><br>' +
                     '<span style="font-size: 14px;">Distribution of Commentary Volume Across the Six Orders</span>',
                x=0.5,
                font=dict(size=24)
            ),
            xaxis=dict(
                title=dict(
                    text='<b>Order (Seder)</b>',
                    font=dict(size=16)
                ),
                tickfont=dict(size=14)
            ),
            yaxis=dict(
                title=dict(
                    text='<b>Percentage of Total Commentary Volume</b>',
                    font=dict(size=16)
                ),
                tickfont=dict(size=12),
                range=[0, max(max(rishonim_percentages), max(acharonim_percentages)) * 1.15]
            ),
            barmode='group',
            width=1200,
            height=700,
            template='plotly_white',
            legend=dict(
                x=0.5,
                y=0.98,
                xanchor='center',
                yanchor='top',
                orientation='h',
                font=dict(size=14)
            ),
            margin=dict(l=80, r=80, t=120, b=80)
        )
        
        # Add annotations for key insights
        max_diff = 0
        max_diff_seder = ""
        for i, seder in enumerate(sedarim_order):
            diff = abs(rishonim_percentages[i] - acharonim_percentages[i])
            if diff > max_diff:
                max_diff = diff
                max_diff_seder = seder
        
        if max_diff > 5:  # Only annotate significant differences
            fig.add_annotation(
                x=max_diff_seder,
                y=max(rishonim_percentages[sedarim_order.index(max_diff_seder)],
                      acharonim_percentages[sedarim_order.index(max_diff_seder)]) + 2,
                text=f"Largest shift:<br>{max_diff:.1f}% difference",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="gray",
                font=dict(size=12),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="gray",
                borderwidth=1
            )
        
        # Save the figure
        output_path_html = os.path.join(self.output_dir, "center_of_gravity.html")
        output_path_png = os.path.join(self.output_dir, "center_of_gravity.png")
        
        fig.write_html(output_path_html)
        fig.write_image(output_path_png, width=1200, height=700, scale=2)
        
        # Also save the raw data
        raw_data = {
            "periods": {
                "Rishonim": {
                    "scholars": self.rishonim_scholars,
                    "total_words": rishonim_total,
                    "distribution": dict(self.period_seder_distribution['Rishonim']),
                    "percentages": {seder: pct for seder, pct in zip(sedarim_order, rishonim_percentages)}
                },
                "Acharonim": {
                    "scholars": self.acharonim_scholars,
                    "total_words": acharonim_total,
                    "distribution": dict(self.period_seder_distribution['Acharonim']),
                    "percentages": {seder: pct for seder, pct in zip(sedarim_order, acharonim_percentages)}
                }
            },
            "analysis": {
                "largest_shift": max_diff_seder,
                "shift_magnitude": max_diff
            }
        }
        
        with open(os.path.join(self.output_dir, "center_of_gravity_data.json"), 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        
        print(f"\nVisualization saved to {self.output_dir}")
        print("Files generated:")
        print("- center_of_gravity.html (interactive)")
        print("- center_of_gravity.png (static)")
        print("- center_of_gravity_data.json (raw data)")
        
        # Print summary statistics
        print("\nSummary Statistics:")
        print(f"Rishonim total words: {rishonim_total:,}")
        print(f"Acharonim total words: {acharonim_total:,}")
        print(f"\nDistribution by Seder:")
        for seder in sedarim_order:
            print(f"{seder:10} - Rishonim: {rishonim_percentages[sedarim_order.index(seder)]:5.1f}%, "
                  f"Acharonim: {acharonim_percentages[sedarim_order.index(seder)]:5.1f}%")

def main():
    """Main execution function."""
    visualizer = CenterOfGravityVisualizer()
    visualizer.load_and_analyze_data()
    visualizer.create_center_of_gravity_visualization()

if __name__ == "__main__":
    main()