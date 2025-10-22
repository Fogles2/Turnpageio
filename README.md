# Pinterest Image Scraper and Analyzer

A comprehensive toolkit for scraping images from Pinterest and extracting keywords using OCR and image analysis.

## Overview

This project consists of two main scripts:

1. **pinterest_scraper.py** - A Playwright-based Pinterest image scraper that captures screenshots to avoid 403 errors
2. **image_analyzer.py** - An image analysis tool using OCR and pre-trained models to extract keywords

## Requirements

- Python 3.8 or higher
- Tesseract OCR (system dependency)

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
playwright install chromium
```

### 3. Install Tesseract OCR

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS:
```bash
brew install tesseract
```

#### Windows:
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

## Usage

### Pinterest Scraper

The Pinterest scraper uses Playwright to automate browser interaction and capture screenshots of Pinterest images.

#### Basic Usage

```bash
python pinterest_scraper.py --keywords "nature photography" --count 10
```

#### Advanced Options

```bash
python pinterest_scraper.py \
  --keywords "design inspiration" \
  --count 20 \
  --output custom_output_dir/ \
  --rate-limit 3.0 \
  --headless false \
  --scroll-count 5
```

#### Arguments

- `--keywords` (required): Search keywords (comma or space separated)
- `--count`: Maximum number of images to capture (default: 10)
- `--output`: Output directory for images (default: pinterest_images)
- `--rate-limit`: Delay between requests in seconds (default: 2.0)
- `--headless`: Run browser in headless mode - true/false (default: true)
- `--scroll-count`: Number of times to scroll for loading more images (default: 3)

#### Examples

**Search for multiple keywords:**
```bash
python pinterest_scraper.py --keywords "mountains,sunset,landscape" --count 15
```

**Run with visible browser window:**
```bash
python pinterest_scraper.py --keywords "food photography" --count 10 --headless false
```

**Custom output directory and rate limiting:**
```bash
python pinterest_scraper.py --keywords "architecture" --count 20 --output images/architecture/ --rate-limit 3.0
```

### Image Analyzer

The image analyzer processes images using OCR (Tesseract) and image captioning (BLIP model) to extract meaningful keywords.

#### Basic Usage

```bash
python image_analyzer.py --input pinterest_images/ --output results.json
```

#### Advanced Options

```bash
python image_analyzer.py \
  --input pinterest_images/ \
  --output analysis_results.json \
  --format both \
  --gpu
```

#### Arguments

- `--input` (required): Input directory containing images
- `--output` (required): Output file path (JSON or CSV)
- `--format`: Output format - json/csv/both (default: json)
- `--gpu`: Use GPU acceleration if available

#### Examples

**Analyze images and export to JSON:**
```bash
python image_analyzer.py --input pinterest_images/ --output results.json
```

**Export to both JSON and CSV:**
```bash
python image_analyzer.py --input images/ --output results.json --format both
```

**Use GPU acceleration:**
```bash
python image_analyzer.py --input images/ --output results.json --gpu
```

## Complete Workflow Example

Here's a complete workflow from scraping to analysis:

```bash
# Step 1: Scrape Pinterest images
python pinterest_scraper.py \
  --keywords "digital art" \
  --count 20 \
  --output scraped_images/

# Step 2: Analyze the scraped images
python image_analyzer.py \
  --input scraped_images/ \
  --output analysis_results.json \
  --format both
```

## Output Formats

### Pinterest Scraper Output

Images are saved with the following naming convention:
```
{keyword_slug}_{timestamp}_{index}.png
```

Example: `digital_art_20250122_143022_1.png`

### Image Analyzer Output

#### JSON Format

```json
[
  {
    "filename": "image1.png",
    "path": "/path/to/image1.png",
    "extracted_text": "Text extracted via OCR",
    "caption": "AI-generated image description",
    "keywords": ["keyword1", "keyword2", "keyword3"]
  }
]
```

#### CSV Format

| filename | path | extracted_text | caption | keywords | keyword_count |
|----------|------|----------------|---------|----------|---------------|
| image1.png | /path/to/image1.png | Text from OCR | AI caption | keyword1, keyword2 | 2 |

## Features

### Pinterest Scraper

- **Screenshot-based capture**: Avoids 403 errors by taking screenshots instead of downloading directly
- **Rate limiting**: Configurable delays to avoid being blocked
- **Meaningful filenames**: Images saved with timestamps and keywords
- **Headless/visible mode**: Option to run browser in visible mode for debugging
- **Automatic scrolling**: Loads more images by scrolling
- **Error handling**: Robust error handling and logging

### Image Analyzer

- **OCR text extraction**: Uses Tesseract to extract text from images
- **AI-powered captioning**: Uses BLIP model to generate descriptive captions
- **Keyword extraction**: Intelligent keyword extraction from text and captions
- **Multiple output formats**: Export to JSON and/or CSV
- **GPU acceleration**: Optional GPU support for faster processing
- **Batch processing**: Process entire directories of images
- **Summary statistics**: Provides analysis summary with keyword counts

## Troubleshooting

### Tesseract not found

If you get an error about Tesseract not being found:

1. Make sure Tesseract is installed (see Installation section)
2. On Windows, add Tesseract to your PATH or set the path explicitly:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

### Playwright browser not installed

If you get an error about the browser not being installed:

```bash
playwright install chromium
```

### Out of memory errors

If you encounter memory issues with large image batches:

1. Process images in smaller batches
2. Use `--gpu` flag if you have a GPU available
3. Reduce image resolution before processing

### Rate limiting / Blocked by Pinterest

If Pinterest blocks your requests:

1. Increase the `--rate-limit` value (e.g., 5.0 or higher)
2. Reduce the number of images per session
3. Use `--headless false` to make the scraping look more human-like

## Dependencies

Core libraries:

- `playwright` - Browser automation
- `pytesseract` - OCR text extraction
- `Pillow` - Image processing
- `transformers` - Pre-trained ML models
- `torch` - Deep learning framework
- `pandas` - Data manipulation and export

See `requirements.txt` for complete list with version numbers.

## License

This project is provided as-is for educational and research purposes. Please respect Pinterest's Terms of Service and robots.txt when using the scraper.

## Notes

- **Ethical Usage**: Always respect website terms of service and rate limits
- **Pinterest TOS**: Be aware of Pinterest's Terms of Service regarding automated access
- **Performance**: First run of image analyzer will download AI models (~1GB), subsequent runs will be faster
- **Storage**: AI models require approximately 1GB of disk space
- **Processing Time**: Image analysis can be slow on CPU; GPU acceleration is recommended for large batches

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Support

For issues or questions:

1. Check the Troubleshooting section
2. Review the examples in this README
3. Check that all dependencies are properly installed
4. Ensure Tesseract OCR is in your system PATH
