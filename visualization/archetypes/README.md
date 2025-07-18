# Archetypes of Scholarship Visualization

This directory contains the visualization and analysis of scholarly archetypes among Talmudic commentators.

## Files

### Script
- `archetypes_visualizer.py` - Main visualization script that analyzes scholarly patterns

### Outputs
- `archetypes_of_scholarship.html` - Interactive visualization with click functionality
- `archetypes_of_scholarship.png` - Static image version
- `archetype_summary.html` - Summary statistics visualization
- `archetype_summary.png` - Static summary image
- `archetype_data.json` - Raw data used for visualization

## What This Analyzes

The visualization categorizes scholars into four archetypes based on:
- **Breadth**: Number of tractates commented on
- **Depth**: Average words per tractate

### The Four Archetypes
1. **The Sages** - High breadth, high depth (comprehensive scholars)
2. **The Specialists** - Low breadth, high depth (focused experts)
3. **The Surveyors** - High breadth, low depth (broad coverage)
4. **The Glossators** - Low breadth, low depth (targeted commentary)

## Usage

```bash
cd visualization/archetypes
python3 archetypes_visualizer.py
```

The script will generate all visualization files in this directory.