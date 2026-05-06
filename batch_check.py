"""
Batch spell checking for multiple files
Process entire folders and export results
"""

import os
import sys
import argparse
import json
import csv
from pathlib import Path
from datetime import datetime
from spell_checker_ml import MLEnhancedSpellChecker


class BatchSpellChecker:
    """Batch processing for spell checking multiple files"""
    
    def __init__(self, corpus_path='oromo_corpus.txt'):
        print("Initializing spell checker...")
        self.checker = MLEnhancedSpellChecker(corpus_path=corpus_path, use_ml=False)
        print(f"✓ Loaded vocabulary: {len(self.checker.words_db)} words\n")
    
    def process_file(self, file_path):
        """Process a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = self.checker.get_detailed_corrections(content)
            
            return {
                'file': str(file_path),
                'status': 'success',
                'original_length': len(content),
                'corrected_length': len(result['corrected']),
                'total_changes': result['total_changes'],
                'corrections': result['corrections'],
                'original': content,
                'corrected': result['corrected']
            }
        except Exception as e:
            return {
                'file': str(file_path),
                'status': 'error',
                'error': str(e)
            }
    
    def process_directory(self, directory, recursive=False, extensions=None):
        """Process all files in a directory"""
        if extensions is None:
            extensions = ['.txt', '.md']
        
        directory = Path(directory)
        results = []
        
        if recursive:
            files = [f for f in directory.rglob('*') if f.suffix in extensions]
        else:
            files = [f for f in directory.glob('*') if f.suffix in extensions]
        
        print(f"Found {len(files)} files to process\n")
        
        for i, file_path in enumerate(files, 1):
            print(f"[{i}/{len(files)}] Processing: {file_path.name}...", end=' ')
            result = self.process_file(file_path)
            results.append(result)
            
            if result['status'] == 'success':
                print(f"✓ ({result['total_changes']} changes)")
            else:
                print(f"✗ Error: {result['error']}")
        
        return results
    
    def export_to_json(self, results, output_file):
        """Export results to JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Results exported to: {output_file}")
    
    def export_to_csv(self, results, output_file):
        """Export results summary to CSV"""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['File', 'Status', 'Total Changes', 'Original Length', 'Corrected Length'])
            
            for result in results:
                if result['status'] == 'success':
                    writer.writerow([
                        result['file'],
                        result['status'],
                        result['total_changes'],
                        result['original_length'],
                        result['corrected_length']
                    ])
                else:
                    writer.writerow([
                        result['file'],
                        result['status'],
                        result.get('error', 'Unknown error'),
                        '-',
                        '-'
                    ])
        print(f"✓ Summary exported to: {output_file}")
    
    def export_corrected_files(self, results, output_dir):
        """Export corrected versions of files"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for result in results:
            if result['status'] == 'success':
                original_path = Path(result['file'])
                output_path = output_dir / f"{original_path.stem}_corrected{original_path.suffix}"
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['corrected'])
        
        print(f"✓ Corrected files saved to: {output_dir}")
    
    def print_summary(self, results):
        """Print summary statistics"""
        total = len(results)
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = total - successful
        total_changes = sum(r.get('total_changes', 0) for r in results if r['status'] == 'success')
        
        print("\n" + "="*60)
        print("BATCH PROCESSING SUMMARY")
        print("="*60)
        print(f"Total files processed: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total corrections made: {total_changes}")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Batch spell checking for Afaan Oromo text files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file
  python batch_check.py --input document.txt --output results.json

  # Process directory
  python batch_check.py --input texts/ --output results.json

  # Process directory recursively with CSV output
  python batch_check.py --input texts/ --recursive --output results.csv

  # Export corrected files
  python batch_check.py --input texts/ --output results.json --export-corrected corrected/
        """
    )
    
    parser.add_argument('--input', '-i', required=True,
                       help='Input file or directory')
    parser.add_argument('--output', '-o', required=True,
                       help='Output file (JSON or CSV)')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Process directories recursively')
    parser.add_argument('--extensions', '-e', nargs='+', default=['.txt', '.md'],
                       help='File extensions to process (default: .txt .md)')
    parser.add_argument('--export-corrected', '-c', metavar='DIR',
                       help='Export corrected files to directory')
    parser.add_argument('--corpus', default='oromo_corpus.txt',
                       help='Path to corpus file')
    
    args = parser.parse_args()
    
    # Initialize batch checker
    batch_checker = BatchSpellChecker(corpus_path=args.corpus)
    
    # Process input
    input_path = Path(args.input)
    
    if input_path.is_file():
        print(f"Processing single file: {input_path}\n")
        results = [batch_checker.process_file(input_path)]
    elif input_path.is_dir():
        print(f"Processing directory: {input_path}")
        print(f"Recursive: {args.recursive}")
        print(f"Extensions: {args.extensions}\n")
        results = batch_checker.process_directory(
            input_path,
            recursive=args.recursive,
            extensions=args.extensions
        )
    else:
        print(f"Error: Input path does not exist: {input_path}")
        sys.exit(1)
    
    # Export results
    output_ext = Path(args.output).suffix.lower()
    
    if output_ext == '.json':
        batch_checker.export_to_json(results, args.output)
    elif output_ext == '.csv':
        batch_checker.export_to_csv(results, args.output)
    else:
        print(f"Warning: Unknown output format '{output_ext}', defaulting to JSON")
        batch_checker.export_to_json(results, args.output)
    
    # Export corrected files if requested
    if args.export_corrected:
        batch_checker.export_corrected_files(results, args.export_corrected)
    
    # Print summary
    batch_checker.print_summary(results)


if __name__ == '__main__':
    main()
