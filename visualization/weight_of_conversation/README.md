# Weight of Conversation Visualization

This directory contains the analysis of which Talmudic tractates generated disproportionate amounts of commentary relative to their length.

## Files

### Script
- `weight_of_conversation_visualizer.py` - Main visualization script

### Outputs
- `weight_of_conversation.html` - Interactive visualization
- `weight_of_conversation.png` - Static image version
- `weight_of_conversation_data.json` - Analysis results data

## What This Analyzes

Identifies tractates that attracted unusually large or small amounts of commentary relative to their actual length (measured in dapim/folios).

### Key Metrics
- **Commentary Density**: Total words of commentary per daf (page) of Talmud
- **Relative Weight**: How much commentary each tractate generated compared to its size
- **Outlier Analysis**: Tractates with unexpectedly high or low commentary ratios

### Research Questions
1. Which tractates inspired the most discussion per page?
2. Are certain types of legal content more "conversation-worthy"?
3. Do practical vs. theoretical tractates differ in commentary density?

### Tractate Categories
- **Practical Law** (e.g., Shabbat, Ketubot) - Daily life applications
- **Theoretical Law** (e.g., Kodashim tractates) - Temple-era laws
- **Civil Law** (e.g., Bava Kamma, Bava Metzia) - Business and damages
- **Ritual Law** (e.g., Berakhot, Sukkah) - Religious observances

## Usage

```bash
cd visualization/weight_of_conversation
python3 weight_of_conversation_visualizer.py
```

The script calculates commentary-to-length ratios and generates visualizations showing which tractates were most "conversation-heavy".