#!/usr/bin/env python3
"""
Script to combine OCR JSON results from multiple pages into a single file.
Each page's data will be preserved with its page identifier.
"""

import json
import os
import glob
from pathlib import Path

def combine_ocr_json_files(input_dir="output_all", output_file="combined_ocr_results.json"):
    """
    Combine all OCR JSON files from the input directory into a single JSON file.
    
    Args:
        input_dir (str): Directory containing the JSON files
        output_file (str): Output filename for the combined JSON
    """
    
    # Find all JSON files with the pattern *_res.json
    json_pattern = os.path.join(input_dir, "*_res.json")
    json_files = glob.glob(json_pattern)
    
    if not json_files:
        print(f"No JSON files found in {input_dir} with pattern *_res.json")
        return
    
    # Sort files by page number (extract number from filename)
    def extract_page_number(filename):
        try:
            # Extract number from filename like "clean_data_combine_0_res.json"
            basename = os.path.basename(filename)
            parts = basename.split('_')
            for part in parts:
                if part.isdigit():
                    return int(part)
            return 0
        except:
            return 0
    
    json_files.sort(key=extract_page_number)
    
    combined_data = {
        "document_info": {
            "total_pages": len(json_files),
            "source_directory": input_dir,
            "combined_timestamp": None
        },
        "pages": []
    }
    
    print(f"Found {len(json_files)} JSON files to combine...")
    
    for i, json_file in enumerate(json_files):
        try:
            print(f"Processing {os.path.basename(json_file)}...")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
            
            # Add metadata to identify the source file and page
            page_info = {
                "source_file": os.path.basename(json_file),
                "page_number": extract_page_number(json_file),
                "page_index": page_data.get("page_index", i),
                "input_path": page_data.get("input_path", ""),
                "ocr_data": page_data
            }
            
            combined_data["pages"].append(page_info)
            
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
            continue
    
    # Add timestamp
    from datetime import datetime
    combined_data["document_info"]["combined_timestamp"] = datetime.now().isoformat()
    
    # Write combined data to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully combined {len(combined_data['pages'])} pages")
        print(f"Output saved to: {output_file}")
        print(f"File size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
        
    except Exception as e:
        print(f"Error writing output file: {str(e)}")

def create_summary_report(combined_file="combined_ocr_results.json", summary_file="ocr_summary.txt"):
    """
    Create a summary report of the combined OCR data.
    """
    try:
        with open(combined_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("OCR COMBINATION SUMMARY REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Total Pages: {data['document_info']['total_pages']}\n")
            f.write(f"Combined on: {data['document_info']['combined_timestamp']}\n")
            f.write(f"Source Directory: {data['document_info']['source_directory']}\n\n")
            
            f.write("PAGE DETAILS:\n")
            f.write("-" * 30 + "\n")
            
            for page in data['pages']:
                f.write(f"Page {page['page_number']:2d}: {page['source_file']}\n")
                
                # Count parsing results
                parsing_count = len(page['ocr_data'].get('parsing_res_list', []))
                f.write(f"         Parsing blocks: {parsing_count}\n")
                
                # Count layout detection results
                layout_count = len(page['ocr_data'].get('layout_det_res', {}).get('boxes', []))
                f.write(f"         Layout boxes: {layout_count}\n")
                
                # Count OCR text results
                ocr_count = len(page['ocr_data'].get('overall_ocr_res', {}).get('dt_polys', []))
                f.write(f"         OCR polygons: {ocr_count}\n\n")
        
        print(f"Summary report saved to: {summary_file}")
        
    except Exception as e:
        print(f"Error creating summary report: {str(e)}")

if __name__ == "__main__":
    # Combine the JSON files
    combine_ocr_json_files()
    
    # Create summary report
    create_summary_report()
    
    print("\nDone! Check the following files:")
    print("- combined_ocr_results.json (main combined file)")
    print("- ocr_summary.txt (summary report)")