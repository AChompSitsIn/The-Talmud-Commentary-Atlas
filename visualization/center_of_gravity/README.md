# Center of Gravity Visualization

This directory contains the analysis of how Talmudic commentary focus shifted between historical periods across the six orders (Sedarim) of the Talmud.

## Files

### Script
- `center_of_gravity_visualizer.py` - Main visualization script

### Outputs
- `center_of_gravity.html` - Interactive visualization
- `center_of_gravity.png` - Static image version
- `center_of_gravity_data.json` - Raw analysis data

## What This Analyzes

Examines the distribution of commentary across the six orders of the Talmud:

### The Six Orders (Sedarim)
1. **Zeraim** - Agricultural laws (Berakhot)
2. **Moed** - Festival and Sabbath laws  
3. **Nashim** - Marriage and divorce laws
4. **Nezikin** - Civil and criminal law
5. **Kodashim** - Temple and sacrifice laws
6. **Taharot** - Purity laws

### Analysis Focus
- Compares commentary distribution between **Rishonim** (Medieval) and **Acharonim** (Post-Medieval) periods
- Identifies shifting scholarly priorities over time
- Reveals which areas of Jewish law received more attention in different eras

## Usage

```bash
cd visualization/center_of_gravity
python3 center_of_gravity_visualizer.py
```

The script analyzes commentary patterns and generates visualization files in this directory.