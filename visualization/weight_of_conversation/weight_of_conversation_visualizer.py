#!/usr/bin/env python3
"""
Weight of Conversation Visualizer
Analyzes which Talmudic tractates have generated disproportionately large amounts 
of commentary relative to their actual length (measured in dapim/folios).
"""

import json
import os
import re
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict
# from scipy import stats  # Replaced with custom implementation

class WeightOfConversationVisualizer:
    def __init__(self):
        # Navigate from visualization/weight_of_conversation/ to project root, then to data/
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_dir = os.path.join(project_root, "data")
        self.output_dir = os.path.dirname(os.path.abspath(__file__))  # Output to same directory as script
        
        # Tractate lengths in dapim (folios) - standard Babylonian Talmud page counts
        self.tractate_lengths = {
            # Seder Zeraim
            "Berakhot": 64,
            
            # Seder Moed
            "Shabbat": 157,
            "Eruvin": 105,
            "Pesachim": 121,
            "Yoma": 88,
            "Sukkah": 56,
            "Beitzah": 40,
            "Rosh Hashanah": 35,
            "Taanit": 31,
            "Megillah": 32,
            "Moed Katan": 29,
            "Chagigah": 27,
            
            # Seder Nashim
            "Yevamot": 122,
            "Ketubot": 112,
            "Nedarim": 91,
            "Nazir": 66,
            "Sotah": 49,
            "Gittin": 90,
            "Kiddushin": 82,
            
            # Seder Nezikin
            "Bava Kamma": 119,
            "Bava Metzia": 119,
            "Bava Batra": 176,
            "Sanhedrin": 113,
            "Makkot": 24,
            "Shevuot": 49,
            "Avodah Zarah": 76,
            "Horayot": 14,
            
            # Seder Kodashim
            "Zevachim": 120,
            "Menachot": 110,
            "Chullin": 142,
            "Bekhorot": 61,
            "Arakhin": 34,
            "Temurah": 34,
            "Keritot": 28,
            "Meilah": 22,
            "Niddah": 73
        }
        
        # Color scheme by Seder
        self.seder_colors = {
            "Zeraim": '#8E44AD',     # Purple
            "Moed": '#27AE60',       # Green
            "Nashim": '#E67E22',     # Orange
            "Nezikin": '#E74C3C',    # Red
            "Kodashim": '#3498DB'    # Light blue
        }
        
        # Seder assignments
        self.tractate_to_seder = {
            "Berakhot": "Zeraim",
            
            "Shabbat": "Moed", "Eruvin": "Moed", "Pesachim": "Moed", "Yoma": "Moed",
            "Sukkah": "Moed", "Beitzah": "Moed", "Rosh Hashanah": "Moed", "Taanit": "Moed",
            "Megillah": "Moed", "Moed Katan": "Moed", "Chagigah": "Moed",
            
            "Yevamot": "Nashim", "Ketubot": "Nashim", "Nedarim": "Nashim", "Nazir": "Nashim",
            "Sotah": "Nashim", "Gittin": "Nashim", "Kiddushin": "Nashim",
            
            "Bava Kamma": "Nezikin", "Bava Metzia": "Nezikin", "Bava Batra": "Nezikin",
            "Sanhedrin": "Nezikin", "Makkot": "Nezikin", "Shevuot": "Nezikin",
            "Avodah Zarah": "Nezikin", "Horayot": "Nezikin",
            
            "Zevachim": "Kodashim", "Menachot": "Kodashim", "Chullin": "Kodashim",
            "Bekhorot": "Kodashim", "Arakhin": "Kodashim", "Temurah": "Kodashim",
            "Keritot": "Kodashim", "Meilah": "Kodashim", "Niddah": "Kodashim"
        }
        
        self.tractate_data = {}
    
    def linear_regression(self, x, y):
        """Simple linear regression implementation."""
        n = len(x)
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        
        # Calculate slope
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0
        
        # Calculate intercept
        intercept = y_mean - slope * x_mean
        
        # Calculate R-squared
        y_pred = [slope * x[i] + intercept for i in range(n)]
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        r_value = np.sqrt(r_squared) if r_squared >= 0 else 0
        
        # Standard error (simplified)
        std_err = np.sqrt(ss_res / (n - 2)) if n > 2 else 0
        
        return slope, intercept, r_value, 0, std_err  # p_value set to 0 for simplicity
    
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
        """Load scholar data and calculate total commentary volume per tractate."""
        print("Loading and analyzing tractate commentary data...")
        
        # Initialize tractate data
        for tractate in self.tractate_lengths:
            self.tractate_data[tractate] = {
                'length': self.tractate_lengths[tractate],
                'total_commentary': 0,
                'scholar_count': 0,
                'seder': self.tractate_to_seder[tractate]
            }
        
        # Process each scholar
        for scholar_dir in os.listdir(self.data_dir):
            scholar_path = os.path.join(self.data_dir, scholar_dir)
            if not os.path.isdir(scholar_path):
                continue
            
            # Process each tractate file
            for file_name in os.listdir(scholar_path):
                if not file_name.endswith('.json'):
                    continue
                
                tractate_name = file_name.replace('.json', '')
                
                # Skip if not a standard tractate
                if tractate_name not in self.tractate_lengths:
                    continue
                
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
                    
                    if tractate_word_count > 0:
                        self.tractate_data[tractate_name]['total_commentary'] += tractate_word_count
                        self.tractate_data[tractate_name]['scholar_count'] += 1
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        print(f"Analyzed {len(self.tractate_data)} tractates")
    
    def create_weight_of_conversation_visualization(self):
        """Create the scatter plot visualization."""
        
        # Prepare data for plotting
        tractates = []
        lengths = []
        commentary_volumes = []
        seders = []
        scholar_counts = []
        
        for tractate, data in self.tractate_data.items():
            if data['total_commentary'] > 0:  # Only include tractates with commentary
                tractates.append(tractate)
                lengths.append(data['length'])
                commentary_volumes.append(data['total_commentary'])
                seders.append(data['seder'])
                scholar_counts.append(data['scholar_count'])
        
        # Calculate trend line
        slope, intercept, r_value, p_value, std_err = self.linear_regression(lengths, commentary_volumes)
        trend_x = np.array([min(lengths), max(lengths)])
        trend_y = slope * trend_x + intercept
        
        # Calculate residuals to identify outliers
        predicted_commentary = [slope * length + intercept for length in lengths]
        residuals = [actual - predicted for actual, predicted in zip(commentary_volumes, predicted_commentary)]
        residual_std = np.std(residuals)
        
        # Create the figure
        fig = go.Figure()
        
        # Add trend line first (so it's behind the points)
        fig.add_trace(go.Scatter(
            x=trend_x,
            y=trend_y,
            mode='lines',
            name='Expected trend',
            line=dict(color='gray', width=2, dash='dash'),
            showlegend=True
        ))
        
        # Add scatter points by Seder
        for seder in self.seder_colors:
            seder_indices = [i for i, s in enumerate(seders) if s == seder]
            if seder_indices:
                fig.add_trace(go.Scatter(
                    x=[lengths[i] for i in seder_indices],
                    y=[commentary_volumes[i] for i in seder_indices],
                    mode='markers+text',
                    name=f'Seder {seder}',
                    marker=dict(
                        size=[scholar_counts[i] * 0.8 + 10 for i in seder_indices],
                        color=self.seder_colors[seder],
                        opacity=0.8,
                        line=dict(width=2, color='white')
                    ),
                    text=[tractates[i] if abs(residuals[i]) > 1.5 * residual_std else '' 
                          for i in seder_indices],
                    textposition='top center',
                    textfont=dict(size=11, weight='bold'),
                    customdata=[[tractates[i], scholar_counts[i], commentary_volumes[i]] 
                               for i in seder_indices],
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>" +
                        "Length: %{x} dapim<br>" +
                        "Commentary: %{y:,.0f} words<br>" +
                        "Scholars: %{customdata[1]}<br>" +
                        "<extra></extra>"
                    )
                ))
        
        # Identify and annotate major outliers
        outlier_threshold = 2 * residual_std
        major_outliers = []
        
        for i, (tractate, residual) in enumerate(zip(tractates, residuals)):
            if abs(residual) > outlier_threshold:
                major_outliers.append({
                    'tractate': tractate,
                    'length': lengths[i],
                    'commentary': commentary_volumes[i],
                    'residual': residual,
                    'ratio': commentary_volumes[i] / lengths[i]
                })
        
        # Sort outliers by absolute residual
        major_outliers.sort(key=lambda x: abs(x['residual']), reverse=True)
        
        # Annotate top outliers
        for outlier in major_outliers[:3]:
            if outlier['residual'] > 0:
                annotation_text = f"<b>{outlier['tractate']}</b><br>Exceptionally high commentary<br>({outlier['ratio']:,.0f} words/daf)"
            else:
                annotation_text = f"<b>{outlier['tractate']}</b><br>Surprisingly low commentary<br>({outlier['ratio']:,.0f} words/daf)"
            
            fig.add_annotation(
                x=outlier['length'],
                y=outlier['commentary'],
                text=annotation_text,
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='gray',
                ax=50 if outlier['residual'] > 0 else -50,
                ay=-50 if outlier['residual'] > 0 else 50,
                font=dict(size=10),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor='gray',
                borderwidth=1
            )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text='<b>The "Weight of Conversation"</b><br>' +
                     '<span style="font-size: 16px;">Commentary Volume vs. Tractate Length</span>',
                x=0.5,
                font=dict(size=26)
            ),
            xaxis=dict(
                title=dict(
                    text='<b>Tractate Length (dapim)</b>',
                    font=dict(size=18)
                ),
                tickfont=dict(size=14),
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(200,200,200,0.3)'
            ),
            yaxis=dict(
                title=dict(
                    text='<b>Total Commentary Volume (words)</b>',
                    font=dict(size=18)
                ),
                tickfont=dict(size=14),
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(200,200,200,0.3)'
            ),
            width=1200,
            height=800,
            template='plotly_white',
            legend=dict(
                x=0.02,
                y=0.98,
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='gray',
                borderwidth=1,
                font=dict(size=12)
            ),
            margin=dict(l=100, r=100, t=120, b=80)
        )
        
        # Add R² annotation
        fig.add_annotation(
            x=0.98,
            y=0.02,
            xref='paper',
            yref='paper',
            text=f'R² = {r_value**2:.3f}',
            showarrow=False,
            font=dict(size=14, color='gray'),
            xanchor='right',
            yanchor='bottom',
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='gray',
            borderwidth=1,
            borderpad=4
        )
        
        # Save the figure
        output_path_html = os.path.join(self.output_dir, "weight_of_conversation.html")
        output_path_png = os.path.join(self.output_dir, "weight_of_conversation.png")
        
        fig.write_html(output_path_html)
        fig.write_image(output_path_png, width=1200, height=800, scale=2)
        
        # Save analysis data
        analysis_data = {
            "tractate_data": {
                tractate: {
                    "length_dapim": data['length'],
                    "total_commentary_words": data['total_commentary'],
                    "scholar_count": data['scholar_count'],
                    "words_per_daf": data['total_commentary'] / data['length'] if data['length'] > 0 else 0,
                    "seder": data['seder']
                }
                for tractate, data in self.tractate_data.items()
                if data['total_commentary'] > 0
            },
            "regression_analysis": {
                "slope": slope,
                "intercept": intercept,
                "r_squared": r_value**2,
                "p_value": p_value,
                "standard_error": std_err
            },
            "outliers": [
                {
                    "tractate": outlier['tractate'],
                    "deviation_from_trend": outlier['residual'],
                    "words_per_daf": outlier['ratio']
                }
                for outlier in major_outliers
            ]
        }
        
        with open(os.path.join(self.output_dir, "weight_of_conversation_data.json"), 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        print(f"\nVisualization saved to {self.output_dir}")
        print("Files generated:")
        print("- weight_of_conversation.html (interactive)")
        print("- weight_of_conversation.png (static)")
        print("- weight_of_conversation_data.json (analysis data)")
        
        # Print summary
        print(f"\nRegression Analysis:")
        print(f"R² = {r_value**2:.3f} (explains {r_value**2*100:.1f}% of variance)")
        print(f"\nTop outliers (most commentary relative to length):")
        for outlier in major_outliers[:5]:
            if outlier['residual'] > 0:
                print(f"- {outlier['tractate']}: {outlier['ratio']:,.0f} words/daf")

def main():
    """Main execution function."""
    visualizer = WeightOfConversationVisualizer()
    visualizer.load_and_analyze_data()
    visualizer.create_weight_of_conversation_visualization()

if __name__ == "__main__":
    main()