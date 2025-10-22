#!/usr/bin/env python3
"""
Image Keyword Extractor using OCR and Image Analysis

This script processes a directory of images, extracts text using Tesseract OCR,
and generates relevant keywords using pre-trained models. Results are exported
to JSON and CSV formats.

Usage:
    python image_analyzer.py --input images/ --output results.json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import warnings

try:
    import pandas as pd
    from PIL import Image
    import pytesseract
    from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
    import torch
except ImportError as e:
    print(f"Error: Missing required dependency: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)

# Suppress warnings
warnings.filterwarnings('ignore')


class ImageAnalyzer:
    """Image analysis class for extracting keywords from images."""
    
    def __init__(self, use_gpu: bool = False):
        """
        Initialize the image analyzer.
        
        Args:
            use_gpu: Use GPU acceleration if available (default: False)
        """
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Initialize models lazily
        self._caption_model = None
        self._caption_processor = None
        self._image_processor = None
        
    def _init_caption_model(self):
        """Initialize the image captioning model (BLIP)."""
        if self._caption_model is None:
            print("Loading BLIP image captioning model...")
            try:
                self._caption_processor = BlipProcessor.from_pretrained(
                    "Salesforce/blip-image-captioning-base"
                )
                self._caption_model = BlipForConditionalGeneration.from_pretrained(
                    "Salesforce/blip-image-captioning-base"
                ).to(self.device)
                print("BLIP model loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load BLIP model: {e}")
                self._caption_model = "error"
                self._caption_processor = "error"
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using Tesseract OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text
        """
        try:
            image = Image.open(image_path)
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            return text.strip()
            
        except Exception as e:
            print(f"Error extracting text from {image_path}: {e}")
            return ""
    
    def generate_image_caption(self, image_path: str) -> str:
        """
        Generate caption for image using BLIP model.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Generated caption
        """
        self._init_caption_model()
        
        if self._caption_model == "error":
            return ""
        
        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Process image and generate caption
            inputs = self._caption_processor(image, return_tensors="pt").to(self.device)
            outputs = self._caption_model.generate(**inputs, max_length=50)
            caption = self._caption_processor.decode(outputs[0], skip_special_tokens=True)
            
            return caption
            
        except Exception as e:
            print(f"Error generating caption for {image_path}: {e}")
            return ""
    
    def extract_keywords_from_text(self, text: str) -> Set[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Input text
            
        Returns:
            Set of keywords
        """
        if not text:
            return set()
        
        # Simple keyword extraction: lowercase, remove punctuation, split
        words = text.lower().replace(',', ' ').replace('.', ' ').replace('\n', ' ').split()
        
        # Filter out common stop words and short words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
            'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'as', 'by', 'from'
        }
        
        keywords = {
            word for word in words
            if len(word) > 2 and word not in stop_words and word.isalpha()
        }
        
        return keywords
    
    def analyze_image(self, image_path: str) -> Dict[str, any]:
        """
        Analyze a single image and extract keywords.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with analysis results
        """
        print(f"Analyzing: {os.path.basename(image_path)}")
        
        result = {
            'filename': os.path.basename(image_path),
            'path': str(image_path),
            'extracted_text': '',
            'caption': '',
            'keywords': []
        }
        
        try:
            # Extract text using OCR
            extracted_text = self.extract_text_from_image(image_path)
            result['extracted_text'] = extracted_text
            
            # Generate caption
            caption = self.generate_image_caption(image_path)
            result['caption'] = caption
            
            # Extract keywords from both text and caption
            keywords = set()
            keywords.update(self.extract_keywords_from_text(extracted_text))
            keywords.update(self.extract_keywords_from_text(caption))
            
            result['keywords'] = sorted(list(keywords))
            
            print(f"  Found {len(result['keywords'])} keywords")
            
        except Exception as e:
            print(f"Error analyzing {image_path}: {e}")
        
        return result
    
    def analyze_directory(
        self,
        input_dir: str,
        extensions: Tuple[str, ...] = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
    ) -> List[Dict[str, any]]:
        """
        Analyze all images in a directory.
        
        Args:
            input_dir: Directory containing images
            extensions: Tuple of valid image extensions
            
        Returns:
            List of analysis results
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")
        
        # Find all image files
        image_files = []
        for ext in extensions:
            image_files.extend(input_path.glob(f"*{ext}"))
        
        print(f"Found {len(image_files)} images in {input_dir}")
        
        if not image_files:
            print("No images found!")
            return []
        
        # Analyze each image
        results = []
        for idx, image_path in enumerate(image_files, 1):
            print(f"\n[{idx}/{len(image_files)}]")
            result = self.analyze_image(str(image_path))
            results.append(result)
        
        return results
    
    def export_to_json(self, results: List[Dict[str, any]], output_path: str):
        """
        Export results to JSON file.
        
        Args:
            results: Analysis results
            output_path: Path to output JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults exported to JSON: {output_path}")
    
    def export_to_csv(self, results: List[Dict[str, any]], output_path: str):
        """
        Export results to CSV file.
        
        Args:
            results: Analysis results
            output_path: Path to output CSV file
        """
        # Flatten the data for CSV
        flattened = []
        for result in results:
            flattened.append({
                'filename': result['filename'],
                'path': result['path'],
                'extracted_text': result['extracted_text'],
                'caption': result['caption'],
                'keywords': ', '.join(result['keywords']),
                'keyword_count': len(result['keywords'])
            })
        
        df = pd.DataFrame(flattened)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Results exported to CSV: {output_path}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Image Keyword Extractor using OCR and Image Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python image_analyzer.py --input images/ --output results.json
  python image_analyzer.py --input pinterest_images/ --output analysis.json --format both
  python image_analyzer.py --input images/ --output results.csv --format csv --gpu
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input directory containing images'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output file path (JSON or CSV)'
    )
    parser.add_argument(
        '--format',
        type=str,
        default='json',
        choices=['json', 'csv', 'both'],
        help='Output format (default: json)'
    )
    parser.add_argument(
        '--gpu',
        action='store_true',
        help='Use GPU acceleration if available'
    )
    
    args = parser.parse_args()
    
    # Check if Tesseract is installed
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        print("Error: Tesseract OCR is not installed or not in PATH")
        print("Please install Tesseract:")
        print("  - Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  - macOS: brew install tesseract")
        print("  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        sys.exit(1)
    
    # Create analyzer
    analyzer = ImageAnalyzer(use_gpu=args.gpu)
    
    # Analyze images
    results = analyzer.analyze_directory(args.input)
    
    if not results:
        print("No results to export")
        return
    
    # Export results
    output_path = Path(args.output)
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.format == 'json' or args.format == 'both':
        json_path = output_path.with_suffix('.json')
        analyzer.export_to_json(results, str(json_path))
    
    if args.format == 'csv' or args.format == 'both':
        csv_path = output_path.with_suffix('.csv')
        analyzer.export_to_csv(results, str(csv_path))
    
    # Print summary
    total_keywords = sum(len(r['keywords']) for r in results)
    unique_keywords = set()
    for r in results:
        unique_keywords.update(r['keywords'])
    
    print(f"\n{'=' * 60}")
    print(f"Analysis Summary")
    print(f"{'=' * 60}")
    print(f"Total images analyzed: {len(results)}")
    print(f"Total keywords extracted: {total_keywords}")
    print(f"Unique keywords: {len(unique_keywords)}")
    print(f"Average keywords per image: {total_keywords / len(results):.1f}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
