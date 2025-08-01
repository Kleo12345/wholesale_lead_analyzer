# wholesale_lead_analyzer/main.py

import pandas as pd
import argparse
import logging
from datetime import datetime

# Import all our custom components
from data_processing.cleaner import DataCleaner
from data_processing.scorer import LeadScorer
from output.report_generator import ReportGenerator
from enrichment.social_media import SocialMediaAnalyzer
from utils.proxy_manager import ProxyManager
from utils.classification import classify_lead

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def process_wholesale_leads(input_csv_path: str, output_csv_path: str, delimiter: str = '\t') -> pd.DataFrame:
    """Main function to orchestrate the lead processing workflow."""
    logger.info(f"Starting lead processing from {input_csv_path}")
    
    # --- MODIFICATION START: Instantiate components with dependencies ---
    logger.info("Initializing analysis components...")
    
    # 1. Initialize the ProxyManager first, as other components need it.
    proxy_manager = ProxyManager()
    if not proxy_manager.proxies:
        logger.warning("No working proxies found or configured. Scraping may be unreliable or blocked.")
        
    # 2. Initialize analyzers that depend on the proxy manager.
    social_media_analyzer = SocialMediaAnalyzer(proxy_manager)
    
    # 3. Initialize the main components, injecting the tools they need.
    cleaner = DataCleaner()
    scorer = LeadScorer(proxy_manager, social_media_analyzer)
    reporter = ReportGenerator()
    # --- MODIFICATION END ---

    # Load and clean data
    try:
        raw_data = pd.read_csv(input_csv_path, sep=delimiter)
        logger.info(f"Loaded {len(raw_data)} records.")
    except Exception as e:
        logger.error(f"Failed to read input file {input_csv_path}: {e}")
        raise
        
    cleaned_data = cleaner.clean_contact_data(raw_data)
    if cleaned_data.empty:
        logger.warning("No leads remaining after cleaning and filtering. Exiting.")
        return pd.DataFrame()
    
    # Process each contact
    results = []
    total = len(cleaned_data)
    for index, contact in cleaned_data.iterrows():
        try:
            name = contact.get('name') or contact.get('username', f'Contact {index+1}')
            logger.info(f"Processing {index+1}/{total}: {name}")
            
            # The scorer now has everything it needs to perform deep analysis
            score, reasons, components = scorer.calculate_lead_score(contact)
            classification = classify_lead(score)
            
            result_record = reporter.build_result_record(contact, score, classification, reasons, components)
            results.append(result_record)
            
            # Note: The dynamic_sleep is now handled within the scraper functions,
            # so we no longer need a sleep call here in the main loop.
            
        except Exception as e:
            logger.error(f"Critical error while processing contact {name}: {e}", exc_info=True)
            results.append({
                'original_username': contact.get('username', ''), 'lead_score': 0,
                'lead_classification': 'ERROR', 'scoring_reasons': f'Processing error: {e}',
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
    # Finalize and save results
    results_df = pd.DataFrame(results).sort_values('lead_score', ascending=False)
    results_df.to_csv(output_csv_path, index=False)
    logger.info(f"Results saved to {output_csv_path}")
    
    # Validate and summarize
    validation_report = reporter.validate_results(results_df)
    logger.info(f"Validation report: {validation_report}")
    reporter.print_summary(results_df)
    
    return results_df

def main():
    """Main execution function with command line interface."""
    parser = argparse.ArgumentParser(description='Wholesale Lead Analyzer with Free Data Enrichment')
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('output_file', help='Output CSV file path')
    parser.add_argument('--delimiter', '-d', default='\t', help='CSV delimiter (default: tab)')
    parser.add_argument('--hot-leads-file', help='Export hot leads to a separate file')
    parser.add_argument('--report-file', help='Generate detailed analysis text report')
    args = parser.parse_args()
    
    try:
        results_df = process_wholesale_leads(args.input_file, args.output_file, args.delimiter)
        
        if not results_df.empty:
            reporter = ReportGenerator()
            if args.hot_leads_file:
                reporter.export_hot_leads(results_df, args.hot_leads_file)
            if args.report_file:
                reporter.generate_report(results_df, args.report_file)
            
        print(f"\n✅ Processing complete! Results saved to {args.output_file}")
        
    except FileNotFoundError:
        print(f"❌ Error: Input file '{args.input_file}' not found.")
    except Exception as e:
        logger.error("A critical error occurred in the main execution.", exc_info=True)
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()