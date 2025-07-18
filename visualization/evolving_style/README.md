# Evolving Style of Commentary Visualization

This directory contains the analysis of how commentary style evolved between the Rishonim and Acharonim periods.

## Files

### Script
- `evolving_style_visualizer.py` - Main visualization script

### Outputs
- `evolving_style.html` - Interactive visualization
- `evolving_style.png` - Static image version
- `evolving_style_data.json` - Statistical analysis data

## What This Analyzes

Investigates whether later commentators (Acharonim) wrote more or less on average per tractate than their predecessors (Rishonim).

### Key Research Question
**Did commentary style become more verbose or more concise over time?**

### Analysis Components
- **Word count comparison** between historical periods
- **Statistical significance testing** of differences
- **Distribution analysis** of commentary lengths
- **Tractate-by-tractate comparison** where both periods have commentary

### Historical Periods Compared
- **Rishonim** (Medieval, ~1000-1500 CE) - Foundational commentators like Rashi, Tosafot, Ramban
- **Acharonim** (Post-Medieval, ~1500-1900 CE) - Later authorities like Maharsha, Penei Yehoshua

## Usage

```bash
cd visualization/evolving_style
python3 evolving_style_visualizer.py
```

The script performs statistical analysis and generates visualization files showing trends in commentary evolution.