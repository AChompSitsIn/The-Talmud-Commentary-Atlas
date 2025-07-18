#!/usr/bin/env python3
"""
Archetypes of Scholarship Visualizer
Modern, interactive visualization of scholarly archetypes using Plotly.
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

class ArchetypesVisualizer:
    def __init__(self):
        # Navigate from visualization/archetypes/ to project root, then to data/
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_dir = os.path.join(project_root, "data")
        self.output_dir = os.path.dirname(os.path.abspath(__file__))  # Output to same directory as script
        self.scholars_data = {}
        
        # Modern color palette
        self.colors = {
            'sages': '#2E86AB',        # Deep blue
            'specialists': '#A23B72',  # Deep magenta
            'surveyors': '#F18F01',    # Orange
            'glossators': '#C73E1D',   # Deep red
            'background': '#FAFAFA',   # Light gray
            'grid': '#E8E8E8',         # Light gray
            'text': '#2C3E50',         # Dark blue-gray
            'accent': '#34495E'        # Darker blue-gray
        }
        
        # Historical period colors - completely distinct from archetype colors
        self.period_colors = {
            'Rishonim': '#8E44AD',     # Purple
            'Acharonim': '#27AE60',    # Green
            'Modern': '#E67E22'        # Dark orange
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
    
    def categorize_period(self, scholar_name: str) -> str:
        """Categorize scholar by historical period."""
        scholar_lower = scholar_name.lower()
        
        # Rishonim (Medieval)
        if any(name in scholar_lower for name in [
            'rashi', 'tosafot', 'ramban', 'rashba', 'ritva', 'ran', 'rosh', 
            'meiri', 'nimukei', 'rabbeinu', 'yad ramah'
        ]):
            return 'Rishonim'
        
        # Modern
        if 'steinsaltz' in scholar_lower:
            return 'Modern'
        
        # Acharonim (Post-Medieval) - default
        return 'Acharonim'
    
    def load_scholar_data(self) -> Dict:
        """Load and analyze scholar data from extracted files."""
        print("Loading scholar data...")
        
        for scholar_dir in os.listdir(self.data_dir):
            scholar_path = os.path.join(self.data_dir, scholar_dir)
            if not os.path.isdir(scholar_path):
                continue
            
            scholar_name = scholar_dir.replace('_', ' ')
            
            scholar_stats = {
                'name': scholar_name,
                'tractates': 0,
                'total_words': 0,
                'avg_words_per_tractate': 0,
                'period': self.categorize_period(scholar_name),
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
                    
                    tractate_word_count = 0
                    for section_key, content in data.items():
                        if isinstance(content, list):
                            for text_block in content:
                                tractate_word_count += self.count_words_in_text(text_block)
                    
                    if tractate_word_count > 0:
                        scholar_stats['tractates'] += 1
                        scholar_stats['total_words'] += tractate_word_count
                        scholar_stats['tractate_list'].append({
                            'name': tractate_name,
                            'words': tractate_word_count
                        })
                
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
            
            if scholar_stats['tractates'] > 0:
                scholar_stats['avg_words_per_tractate'] = scholar_stats['total_words'] / scholar_stats['tractates']
                self.scholars_data[scholar_name] = scholar_stats
        
        print(f"Loaded data for {len(self.scholars_data)} scholars")
        return self.scholars_data
    
    def determine_archetype(self, tractates: int, avg_words: float) -> str:
        """Determine archetype based on breadth and depth."""
        # Calculate thresholds based on data distribution
        tractate_median = np.median([s['tractates'] for s in self.scholars_data.values()])
        words_median = np.median([s['avg_words_per_tractate'] for s in self.scholars_data.values()])
        
        if tractates >= tractate_median and avg_words >= words_median:
            return 'The Sages'
        elif tractates < tractate_median and avg_words >= words_median:
            return 'The Specialists'
        elif tractates >= tractate_median and avg_words < words_median:
            return 'The Surveyors'
        else:
            return 'The Glossators'
    
    def create_archetype_visualization(self) -> go.Figure:
        """Create the main archetype scatter plot."""
        
        # Prepare data
        scholars = []
        tractates = []
        avg_words = []
        total_words = []
        periods = []
        archetypes = []
        
        for scholar_name, data in self.scholars_data.items():
            scholars.append(scholar_name)
            tractates.append(data['tractates'])
            avg_words.append(data['avg_words_per_tractate'])
            total_words.append(data['total_words'])
            periods.append(data['period'])
            archetypes.append(self.determine_archetype(data['tractates'], data['avg_words_per_tractate']))
        
        # Create DataFrame
        df = pd.DataFrame({
            'Scholar': scholars,
            'Tractates': tractates,
            'Avg_Words_Per_Tractate': avg_words,
            'Total_Words': total_words,
            'Period': periods,
            'Archetype': archetypes
        })
        
        # Calculate medians for quadrant lines
        tractate_median = df['Tractates'].median()
        words_median = df['Avg_Words_Per_Tractate'].median()
        
        # Create figure
        fig = go.Figure()
        
        # Add quadrant background rectangles
        fig.add_shape(
            type="rect",
            x0=0, y0=words_median, x1=tractate_median, y1=df['Avg_Words_Per_Tractate'].max() * 1.1,
            fillcolor=self.colors['specialists'], opacity=0.1,
            line=dict(width=0)
        )
        
        fig.add_shape(
            type="rect",
            x0=tractate_median, y0=words_median, x1=df['Tractates'].max() * 1.1, y1=df['Avg_Words_Per_Tractate'].max() * 1.1,
            fillcolor=self.colors['sages'], opacity=0.1,
            line=dict(width=0)
        )
        
        fig.add_shape(
            type="rect",
            x0=tractate_median, y0=0, x1=df['Tractates'].max() * 1.1, y1=words_median,
            fillcolor=self.colors['surveyors'], opacity=0.1,
            line=dict(width=0)
        )
        
        fig.add_shape(
            type="rect",
            x0=0, y0=0, x1=tractate_median, y1=words_median,
            fillcolor=self.colors['glossators'], opacity=0.1,
            line=dict(width=0)
        )
        
        # Calculate positions for labels well outside the data area
        y_max = df['Avg_Words_Per_Tractate'].max()
        y_min = df['Avg_Words_Per_Tractate'].min()
        x_max = df['Tractates'].max()
        x_min = df['Tractates'].min()
        
        # Expand the plotting area to accommodate labels
        y_range = y_max - y_min
        x_range = x_max - x_min
        
        # Position labels in corners, well outside data bounds
        fig.add_annotation(
            x=x_min - x_range * 0.05, y=y_max + y_range * 0.15,
            text="<b>The Specialists</b><br>Low breadth, high depth",
            showarrow=False, font=dict(size=14, color=self.colors['text']),
            bgcolor="rgba(255,255,255,0.9)", bordercolor=self.colors['specialists'],
            borderwidth=2, xanchor="left", yanchor="bottom"
        )
        
        fig.add_annotation(
            x=x_max + x_range * 0.05, y=y_max + y_range * 0.15,
            text="<b>The Sages</b><br>High breadth, high depth",
            showarrow=False, font=dict(size=14, color=self.colors['text']),
            bgcolor="rgba(255,255,255,0.9)", bordercolor=self.colors['sages'],
            borderwidth=2, xanchor="right", yanchor="bottom"
        )
        
        fig.add_annotation(
            x=x_max + x_range * 0.05, y=y_min - y_range * 0.15,
            text="<b>The Surveyors</b><br>High breadth, low depth",
            showarrow=False, font=dict(size=14, color=self.colors['text']),
            bgcolor="rgba(255,255,255,0.9)", bordercolor=self.colors['surveyors'],
            borderwidth=2, xanchor="right", yanchor="top"
        )
        
        fig.add_annotation(
            x=x_min - x_range * 0.05, y=y_min - y_range * 0.15,
            text="<b>The Glossators</b><br>Low breadth, low depth",
            showarrow=False, font=dict(size=14, color=self.colors['text']),
            bgcolor="rgba(255,255,255,0.9)", bordercolor=self.colors['glossators'],
            borderwidth=2, xanchor="left", yanchor="top"
        )
        
        # Add median lines
        fig.add_vline(x=tractate_median, line_dash="dash", line_color=self.colors['accent'], line_width=2)
        fig.add_hline(y=words_median, line_dash="dash", line_color=self.colors['accent'], line_width=2)
        
        # Add scatter points by period
        for period in df['Period'].unique():
            period_data = df[df['Period'] == period]
            
            fig.add_trace(go.Scatter(
                x=period_data['Tractates'],
                y=period_data['Avg_Words_Per_Tractate'],
                mode='markers',
                name=period,
                marker=dict(
                    size=np.sqrt(period_data['Total_Words']) / 50 + 8,  # Larger base size with minimum
                    sizemin=8,  # Minimum size for visibility
                    color=self.period_colors[period],
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                text=period_data['Scholar'],
                customdata=period_data['Total_Words'],
                hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "Tractates: %{x}<br>" +
                    "Avg Words/Tractate: %{y:,.0f}<br>" +
                    "Total Words: %{customdata:,.0f}<br>" +
                    "Period: " + period +
                    "<extra></extra>"
                ),
                legendgroup=period,
                showlegend=True
            ))
        

        # Update layout
        fig.update_layout(
            title=dict(
                text="<b>Archetypes of Talmudic Scholarship</b><br><sub>Commentary patterns across 63 scholars and 36 tractates</sub>",
                x=0.5,
                font=dict(size=24, color=self.colors['text'])
            ),
            xaxis=dict(
                title=dict(
                    text="<b>Breadth</b><br>Number of Tractates Commented On",
                    font=dict(size=16, color=self.colors['text'])
                ),
                tickfont=dict(size=12, color=self.colors['text']),
                gridcolor=self.colors['grid'],
                gridwidth=1,
                range=[-x_range * 0.15, x_max + x_range * 0.15]
            ),
            yaxis=dict(
                title=dict(
                    text="<b>Depth</b><br>Average Words per Tractate",
                    font=dict(size=16, color=self.colors['text'])
                ),
                tickfont=dict(size=12, color=self.colors['text']),
                gridcolor=self.colors['grid'],
                gridwidth=1,
                range=[y_min - y_range * 0.25, y_max + y_range * 0.25]
            ),
            plot_bgcolor=self.colors['background'],
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", color=self.colors['text']),
            legend=dict(
                title="<b>Historical Period</b>",
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor=self.colors['accent'],
                borderwidth=1,
                itemsizing="constant",
                tracegroupgap=10
            ),
            width=1200,
            height=800,
            margin=dict(l=120, r=200, t=150, b=120),
            clickmode='event+select',
            hovermode='closest',
            dragmode='zoom'
        )
        
        # Add custom JavaScript for persistent hover on click
        fig.add_annotation(
            x=0, y=0,
            xref="paper", yref="paper",
            text="",
            showarrow=False,
            visible=False
        )
        
        
        return fig
    
    def create_summary_stats(self) -> go.Figure:
        """Create summary statistics visualization."""
        
        # Calculate archetype distribution
        archetype_counts = {}
        for scholar_data in self.scholars_data.values():
            archetype = self.determine_archetype(
                scholar_data['tractates'], 
                scholar_data['avg_words_per_tractate']
            )
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
        
        # Create subplot
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Archetype Distribution", "Period Distribution"),
            specs=[[{"type": "pie"}, {"type": "pie"}]]
        )
        
        # Archetype pie chart
        archetype_labels = list(archetype_counts.keys())
        archetype_colors = []
        for label in archetype_labels:
            if 'Specialists' in label:
                archetype_colors.append(self.colors['specialists'])
            elif 'Sages' in label:
                archetype_colors.append(self.colors['sages'])
            elif 'Surveyors' in label:
                archetype_colors.append(self.colors['surveyors'])
            elif 'Glossators' in label:
                archetype_colors.append(self.colors['glossators'])
        
        fig.add_trace(
            go.Pie(
                labels=archetype_labels,
                values=list(archetype_counts.values()),
                marker_colors=archetype_colors,
                hole=0.4,
                domain=dict(x=[0, 0.48]),
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Period distribution
        period_counts = {}
        for scholar_data in self.scholars_data.values():
            period = scholar_data['period']
            period_counts[period] = period_counts.get(period, 0) + 1
        
        fig.add_trace(
            go.Pie(
                labels=list(period_counts.keys()),
                values=list(period_counts.values()),
                marker_colors=[self.period_colors[period] for period in period_counts.keys()],
                hole=0.4,
                domain=dict(x=[0.52, 1]),
                showlegend=False
            ),
            row=1, col=2
        )
        
        # Add manual legends as annotations with proper alignment
        # Archetype legend (left side - moved farther left and up)
        archetype_legend_lines = []
        archetype_legend_lines.append("<b>Archetypes</b>")
        for i, (label, color) in enumerate(zip(archetype_labels, archetype_colors)):
            # Use monospace font and consistent spacing for alignment
            archetype_legend_lines.append(f'<span style="color:{color}; font-size: 20px; font-family: monospace;">●</span> {label}')
        
        fig.add_annotation(
            x=-0.15, y=0.98,  # Moved farther left and up
            xref="paper", yref="paper",
            text="<br>".join(archetype_legend_lines),
            showarrow=False,
            font=dict(size=12, color=self.colors['text'], family="Arial, sans-serif"),
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor=self.colors['accent'],
            borderwidth=1,
            borderpad=10,
            align="left"  # Left align text
        )
        
        # Period legend (right side - moved farther right and up)
        period_legend_lines = []
        period_legend_lines.append("<b>Historical Periods</b>")
        for period, color in self.period_colors.items():
            if period in period_counts:
                # Use monospace font and consistent spacing for alignment
                period_legend_lines.append(f'<span style="color:{color}; font-size: 20px; font-family: monospace;">●</span> {period}')
        
        fig.add_annotation(
            x=1.15, y=0.98,  # Moved farther right and up
            xref="paper", yref="paper",
            text="<br>".join(period_legend_lines),
            showarrow=False,
            font=dict(size=12, color=self.colors['text'], family="Arial, sans-serif"),
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor=self.colors['accent'],
            borderwidth=1,
            borderpad=10,
            align="left"  # Left align text within the box
        )
        
        fig.update_layout(
            title=dict(
                text="<b>Scholarly Distribution Analysis</b>",
                x=0.5,
                font=dict(size=20, color=self.colors['text'])
            ),
            font=dict(family="Arial, sans-serif", color=self.colors['text']),
            paper_bgcolor='white',
            width=1200,  # Increased width for better spacing
            height=600,
            showlegend=False,
            margin=dict(l=180, r=180, t=80, b=50)  # Increased margins for legends
        )
        
        return fig
    
    def generate_visualizations(self):
        """Generate all visualizations and save them."""
        print("Generating visualizations...")
        
        # Load data
        self.load_scholar_data()
        
        # Create main archetype visualization
        main_fig = self.create_archetype_visualization()
        
        # Configure for interactive behavior in HTML output
        config = {
            'displayModeBar': False,
            'displaylogo': False,
            'scrollZoom': False,
            'doubleClick': 'reset',
            'showTips': False,
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'archetypes_of_scholarship',
                'height': 800,
                'width': 1200,
                'scale': 1
            }
        }
        
        # Create custom HTML with click interaction
        html_content = main_fig.to_html(include_plotlyjs='cdn', config=config)
        
        # Add custom JavaScript for click interaction
        click_script = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            var gd = document.getElementsByClassName('plotly-graph-div')[0];
            var focusedDot = null;
            var infoPanel = null;
            
            // Create info panel on page load
            createInfoPanel();
            
            // Add double-click to reset zoom
            gd.on('plotly_doubleclick', function() {
                Plotly.relayout(gd, {
                    'xaxis.autorange': true,
                    'yaxis.autorange': true
                });
            });
            
            gd.on('plotly_click', function(data) {
                if (data.points && data.points.length > 0) {
                    var clicked = {
                        trace: data.points[0].curveNumber,
                        point: data.points[0].pointNumber
                    };
                    
                    // If clicking currently focused dot, unfocus it
                    if (focusedDot && focusedDot.trace === clicked.trace && focusedDot.point === clicked.point) {
                        unfocus();
                    } else {
                        // Focus the clicked dot
                        focus(clicked, data.points[0]);
                    }
                } else {
                    // Clicked empty area - unfocus if something is focused
                    if (focusedDot) {
                        unfocus();
                    }
                }
            });
            
            function createInfoPanel() {
                // Create info panel element
                infoPanel = document.createElement('div');
                infoPanel.style.position = 'fixed';
                infoPanel.style.top = '400px';
                infoPanel.style.right = '20px';
                infoPanel.style.width = '250px';
                infoPanel.style.background = 'rgba(255, 255, 255, 0.95)';
                infoPanel.style.border = '2px solid #34495E';
                infoPanel.style.borderRadius = '8px';
                infoPanel.style.padding = '16px';
                infoPanel.style.fontSize = '14px';
                infoPanel.style.fontFamily = 'Arial, sans-serif';
                infoPanel.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                infoPanel.style.zIndex = '1000';
                infoPanel.style.display = 'none';
                
                // Initial content
                infoPanel.innerHTML = 
                    '<div style="font-weight: bold; color: #2C3E50; margin-bottom: 8px; font-size: 16px;">Scholar Details</div>' +
                    '<div style="color: #7F8C8D;">Click a dot to view details</div>';
                
                // Add to document
                document.body.appendChild(infoPanel);
            }
            
            function focus(dot, pointData) {
                focusedDot = dot;
                
                // Fade all dots except the focused one
                for (var i = 0; i < gd.data.length; i++) {
                    var opacities = [];
                    for (var j = 0; j < gd.data[i].x.length; j++) {
                        if (i === dot.trace && j === dot.point) {
                            opacities.push(1.0); // Keep focused dot bright
                        } else {
                            opacities.push(0.4); // Fade all others
                        }
                    }
                    Plotly.restyle(gd, {'marker.opacity': opacities}, i);
                }
                
                // Update info panel
                updateInfoPanel(pointData);
            }
            
            function unfocus() {
                focusedDot = null;
                
                // Reset all dots to normal opacity
                for (var i = 0; i < gd.data.length; i++) {
                    Plotly.restyle(gd, {'marker.opacity': 0.8}, i);
                }
                
                // Hide info panel
                infoPanel.style.display = 'none';
            }
            
            function updateInfoPanel(pointData) {
                var scholar = pointData.text;
                var tractates = pointData.x;
                var avgWords = Math.round(pointData.y);
                var totalWords = pointData.customdata;
                var period = pointData.data.name;
                
                infoPanel.innerHTML = 
                    '<div style="font-weight: bold; color: #2C3E50; margin-bottom: 12px; font-size: 16px;">Scholar Details</div>' +
                    '<div style="margin-bottom: 8px;"><strong style="color: #2C3E50;">' + scholar + '</strong></div>' +
                    '<div style="margin-bottom: 4px; color: #34495E;"><strong>Period:</strong> ' + period + '</div>' +
                    '<div style="margin-bottom: 4px; color: #34495E;"><strong>Tractates:</strong> ' + tractates + '</div>' +
                    '<div style="margin-bottom: 4px; color: #34495E;"><strong>Avg Words/Tractate:</strong> ' + avgWords.toLocaleString() + '</div>' +
                    '<div style="color: #34495E;"><strong>Total Words:</strong> ' + totalWords.toLocaleString() + '</div>';
                
                infoPanel.style.display = 'block';
            }
        });
        </script>
        """
        
        # Insert the script before the closing body tag
        html_content = html_content.replace('</body>', click_script + '</body>')
        
        # Write custom HTML
        with open(f"{self.output_dir}/archetypes_of_scholarship.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        main_fig.write_image(f"{self.output_dir}/archetypes_of_scholarship.png", width=1200, height=800)
        
        # Create summary statistics
        summary_fig = self.create_summary_stats()
        summary_fig.write_html(f"{self.output_dir}/archetype_summary.html")
        summary_fig.write_image(f"{self.output_dir}/archetype_summary.png", width=1000, height=500)
        
        # Save data for external use
        archetype_data = []
        for scholar_name, data in self.scholars_data.items():
            archetype_data.append({
                'scholar': scholar_name,
                'tractates': data['tractates'],
                'avg_words_per_tractate': data['avg_words_per_tractate'],
                'total_words': data['total_words'],
                'period': data['period'],
                'archetype': self.determine_archetype(data['tractates'], data['avg_words_per_tractate'])
            })
        
        with open(f"{self.output_dir}/archetype_data.json", 'w', encoding='utf-8') as f:
            json.dump(archetype_data, f, ensure_ascii=False, indent=2)
        
        print(f"Visualizations saved to {self.output_dir}")
        print("Files generated:")
        print("- archetypes_of_scholarship.html (interactive)")
        print("- archetypes_of_scholarship.png (static)")
        print("- archetype_summary.html (interactive)")
        print("- archetype_summary.png (static)")
        print("- archetype_data.json (raw data)")

def main():
    """Main execution function."""
    visualizer = ArchetypesVisualizer()
    visualizer.generate_visualizations()

if __name__ == "__main__":
    main()