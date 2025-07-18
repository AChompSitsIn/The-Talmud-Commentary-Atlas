# Usage Guide

## Prerequisites

### System Requirements
- Python 3.7 or higher
- MongoDB instance running locally (port 27017)
- Sefaria database loaded in MongoDB
- Minimum 2GB available disk space for extracted data

### Python Dependencies
```bash
pip install pymongo
```

### MongoDB Setup
Ensure your MongoDB instance is running and contains the Sefaria database:
```bash
# Start MongoDB service
sudo systemctl start mongod  # Linux
brew services start mongodb  # macOS

# Verify database exists
mongo
> show dbs
> use sefaria
> db.texts.count()  # Should return significant number
```

## Basic Usage

### 1. Extract Commentary Data
Run the main extraction script to process all Talmudic commentary:

```bash
cd corrected_mongodb_analysis
python3 talmudic_extractor.py
```

**Expected Output:**
```
=== EXTRACTING ALL TALMUDIC COMMENTARIES ===
=== FINDING TALMUDIC COMMENTARIES ===
Found 1167 Talmudic commentary documents
✓ Ben Yehoyada on Arakhin: 14 sections, 54 text blocks
✓ Ben Yehoyada on Avodah Zarah: 38 sections, 158 text blocks
...
```

**Generated Files:**
- `data/` directory with scholar subdirectories
- `extraction_report.json` with detailed statistics
- Individual JSON files for each scholar-tractate combination

**Note:** The extraction will initially create 63 entries, but after consolidation (removing non-commentary entries and merging works by the same author), you'll have 47 legitimate scholars. See the consolidation report for details.

### 2. Generate Comprehensive Analysis
Run the analysis script to get detailed statistics:

```bash
python3 comprehensive_summary.py
```

**Expected Output:**
```
COMPREHENSIVE TALMUDIC COMMENTARY ANALYSIS SUMMARY
================================================================================
OVERALL STATISTICS
Total Scholars Analyzed: 47 (consolidated from 63 initial entries)
Total Tractates Covered: 36
Total Hebrew Words: 30,215,148
...
```

**Generated Files:**
- `comprehensive_analysis_report.json` with complete analysis
- Console output with formatted statistics

## Advanced Usage

### 1. Custom MongoDB Connection
If your MongoDB instance uses different settings, modify the connection in `talmudic_extractor.py`:

```python
# Default connection
self.client = pymongo.MongoClient("mongodb://localhost:27017/")

# Custom connection
self.client = pymongo.MongoClient("mongodb://username:password@host:port/")
```

### 2. Selective Extraction
To extract specific scholars or tractates, modify the tractate list:

```python
# Extract only major tractates
self.talmudic_tractates = [
    "Berakhot", "Shabbat", "Sanhedrin", "Bava Metzia"
]
```

### 3. Custom Output Directory
Change the output directory in `talmudic_extractor.py`:

```python
# Default output
output_dir = "/path/to/corrected_mongodb_analysis/data"

# Custom output
output_dir = "/your/custom/path/data"
```

## Data Access Patterns

### 1. Reading Extracted Data
```python
import json

# Load specific scholar's commentary on a tractate
with open('data/Steinsaltz/Sanhedrin.json', 'r', encoding='utf-8') as f:
    steinsaltz_sanhedrin = json.load(f)

# Access specific sections
for section_key, content in steinsaltz_sanhedrin.items():
    print(f"Section: {section_key}")
    for text_block in content:
        print(f"  {text_block}")
```

### 2. Analyzing Scholar Coverage
```python
import os

# Get all scholars
scholars = os.listdir('data/')
print(f"Total scholars: {len(scholars)}")

# Get tractates for specific scholar
scholar_tractates = os.listdir('data/Steinsaltz/')
tractates = [f.replace('.json', '') for f in scholar_tractates if f.endswith('.json')]
print(f"Steinsaltz covers {len(tractates)} tractates")
```

### 3. Word Count Analysis
```python
import json
import re

def count_hebrew_words(text):
    """Count Hebrew words in text."""
    clean_text = re.sub(r'<[^>]+>', '', text)
    clean_text = re.sub(r'[^\u0590-\u05FF\s]', ' ', clean_text)
    words = [word.strip() for word in clean_text.split() if word.strip()]
    return len(words)

# Count words in a file
with open('data/Steinsaltz/Sanhedrin.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total_words = 0
for section_key, content in data.items():
    for text_block in content:
        total_words += count_hebrew_words(text_block)

print(f"Total words in Steinsaltz Sanhedrin: {total_words}")
```

## File Structure Reference

### Data Directory Organization
```
data/
├── Steinsaltz/
│   ├── Sanhedrin.json
│   ├── Berakhot.json
│   └── ...
├── Chidushei_Halachot/
│   ├── Sanhedrin.json
│   ├── Berakhot.json
│   └── ...
└── ...
```

### JSON File Format
Each tractate file contains:
```json
{
  "Scholar_on_Tractate.section_1": [
    "Hebrew text line 1",
    "Hebrew text line 2"
  ],
  "Scholar_on_Tractate.section_2": [
    "Hebrew text line 1"
  ]
}
```

### Report Files
- **extraction_report.json**: Extraction statistics and metadata
- **comprehensive_analysis_report.json**: Complete analysis with word counts

## Common Use Cases

### 1. Research Analysis
```python
# Find all scholars who commented on specific tractate
import os
import json

def find_scholars_for_tractate(tractate_name):
    scholars = []
    for scholar_dir in os.listdir('data/'):
        scholar_path = os.path.join('data/', scholar_dir)
        if os.path.isdir(scholar_path):
            tractate_file = os.path.join(scholar_path, f"{tractate_name}.json")
            if os.path.exists(tractate_file):
                scholars.append(scholar_dir.replace('_', ' '))
    return scholars

sanhedrin_scholars = find_scholars_for_tractate('Sanhedrin')
print(f"Scholars who commented on Sanhedrin: {len(sanhedrin_scholars)}")
```

### 2. Comparative Analysis
```python
# Compare word counts between scholars
def compare_scholars(tractate_name, scholar1, scholar2):
    # Load data for both scholars
    with open(f'data/{scholar1}/{tractate_name}.json', 'r', encoding='utf-8') as f:
        data1 = json.load(f)
    
    with open(f'data/{scholar2}/{tractate_name}.json', 'r', encoding='utf-8') as f:
        data2 = json.load(f)
    
    # Count words for each
    words1 = sum(count_hebrew_words(text) for section in data1.values() for text in section)
    words2 = sum(count_hebrew_words(text) for section in data2.values() for text in section)
    
    print(f"{scholar1}: {words1} words")
    print(f"{scholar2}: {words2} words")
    print(f"Ratio: {words1/words2:.2f}")

compare_scholars('Sanhedrin', 'Steinsaltz', 'Maharsha')
```

### 3. Content Search
```python
# Search for specific Hebrew terms
def search_content(search_term, scholar=None, tractate=None):
    results = []
    
    data_dir = 'data/'
    scholars = [scholar] if scholar else os.listdir(data_dir)
    
    for scholar_name in scholars:
        scholar_path = os.path.join(data_dir, scholar_name)
        if not os.path.isdir(scholar_path):
            continue
            
        files = [f"{tractate}.json"] if tractate else os.listdir(scholar_path)
        
        for file_name in files:
            if not file_name.endswith('.json'):
                continue
                
            file_path = os.path.join(scholar_path, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for section_key, content in data.items():
                    for text_block in content:
                        if search_term in text_block:
                            results.append({
                                'scholar': scholar_name,
                                'tractate': file_name.replace('.json', ''),
                                'section': section_key,
                                'text': text_block
                            })
            except:
                continue
    
    return results

# Search for specific term
results = search_content('סנהדרין')
print(f"Found {len(results)} occurrences")
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   ```
   pymongo.errors.ServerSelectionTimeoutError
   ```
   **Solution**: Ensure MongoDB is running and accessible
   ```bash
   sudo systemctl start mongod
   ```

2. **Permission Errors**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   **Solution**: Check directory permissions or run with appropriate privileges

3. **Memory Issues**
   ```
   MemoryError
   ```
   **Solution**: Process in smaller batches or increase system memory

4. **Unicode Encoding Issues**
   ```
   UnicodeDecodeError
   ```
   **Solution**: Ensure Python environment supports UTF-8 encoding

### Debugging

Enable verbose output by modifying the extraction script:
```python
# Add debug prints
print(f"Processing document: {doc['title']}")
print(f"Chapter type: {type(doc.get('chapter', {}))}")
```

## Getting Help

For technical issues:
1. Check MongoDB connection and database content
2. Verify Python dependencies are installed
3. Ensure sufficient disk space and memory
4. Review log output for specific error messages

For questions about the data or methodology:
1. Refer to METHODOLOGY.md for technical details
2. Check README.md for project overview
3. Review extraction reports for statistics
