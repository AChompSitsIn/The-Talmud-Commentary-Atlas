# RInfluence Visualization Suite

This directory contains four distinct visualization analyses of Talmudic commentary patterns, each focusing on different aspects of scholarly behavior and textual analysis.

## Directory Structure

```
visualization/
├── archetypes/              # Scholarly archetype classification
│   ├── archetypes_visualizer.py
│   ├── *.html, *.png, *.json
│   └── README.md
├── center_of_gravity/       # Historical shifts across Talmudic orders
│   ├── center_of_gravity_visualizer.py
│   ├── *.html, *.png, *.json
│   └── README.md
├── evolving_style/          # Commentary verbosity over time
│   ├── evolving_style_visualizer.py
│   ├── *.html, *.png, *.json
│   └── README.md
├── weight_of_conversation/  # Commentary density by tractate
│   ├── weight_of_conversation_visualizer.py
│   ├── *.html, *.png, *.json
│   └── README.md
└── README.md               # This file
```

## The Four Analyses

### 1. Archetypes of Scholarship (`archetypes/`)
**Question**: How do scholars differ in their commentary approach?

Categorizes 47 scholars into four archetypes based on breadth (tractates covered) vs. depth (words per tractate):
- **The Sages**: Comprehensive scholars (high breadth + depth)
- **The Specialists**: Focused experts (low breadth + high depth) 
- **The Surveyors**: Broad coverage (high breadth + low depth)
- **The Glossators**: Targeted commentary (low breadth + depth)

### 2. Center of Gravity (`center_of_gravity/`)
**Question**: How did scholarly focus shift between historical periods?

Analyzes commentary distribution across the six orders (Sedarim) of the Talmud, comparing Rishonim (Medieval) vs. Acharonim (Post-Medieval) periods to identify changing priorities in Jewish legal scholarship.

### 3. Evolving Style (`evolving_style/`)
**Question**: Did commentary become more verbose or concise over time?

Compares average commentary length between Rishonim and Acharonim to determine if scholarly style evolved toward greater elaboration or more concise explanation.

### 4. Weight of Conversation (`weight_of_conversation/`)
**Question**: Which tractates generated disproportionate commentary?

Identifies tractates that attracted unusually high or low amounts of discussion relative to their actual length (in dapim/folios), revealing which topics were most "conversation-worthy."

## Technical Implementation

### Common Features
- **Interactive HTML visualizations** with hover details and zoom
- **Static PNG exports** for presentations and papers
- **JSON data exports** for further analysis
- **Dynamic path resolution** for cross-platform compatibility
- **Comprehensive documentation** in each subdirectory

### Data Sources
All visualizations analyze the same extracted dataset:
- **47 legitimate scholars** (after consolidation)
- **36 tractates** (complete Babylonian Talmud)
- **30.2 million Hebrew words**
- **63,976 commentary sections**

### Dependencies
- `plotly` - Interactive visualizations
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- Standard library: `json`, `os`, `re`, `collections`

## Usage

Each visualization can be run independently:

```bash
# Run individual analyses
cd archetypes && python3 archetypes_visualizer.py
cd ../center_of_gravity && python3 center_of_gravity_visualizer.py
cd ../evolving_style && python3 evolving_style_visualizer.py
cd ../weight_of_conversation && python3 weight_of_conversation_visualizer.py
```

Or from the project root:
```bash
python3 visualization/archetypes/archetypes_visualizer.py
python3 visualization/center_of_gravity/center_of_gravity_visualizer.py
python3 visualization/evolving_style/evolving_style_visualizer.py
python3 visualization/weight_of_conversation/weight_of_conversation_visualizer.py
```

## Research Applications

These visualizations support research in:
- **Digital Humanities**: Computational analysis of religious texts
- **Jewish Studies**: Scholarly tradition evolution
- **Historical Linguistics**: Commentary style development
- **Bibliometrics**: Academic influence patterns
- **Cultural Analytics**: Intellectual history visualization

## Output Files

Each subdirectory generates:
- `*.html` - Interactive visualizations (main research outputs)
- `*.png` - Static images (for papers and presentations) 
- `*_data.json` - Raw analysis data (for reproducibility)

All outputs are self-contained and can be shared independently.