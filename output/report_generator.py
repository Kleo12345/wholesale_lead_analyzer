# wholesale_lead_analyzer/output/report_generator.py

import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Any
from utils.classification import estimate_probability

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Handles all output, including CSVs, reports, and summaries."""

    def build_result_record(self, contact: pd.Series, score: int, classification: str, 
                            reasons: List[str], component_scores: Dict[str, int]) -> Dict:
        """Build the final dictionary for the output DataFrame."""
        financial_indicators, property_indicators = [], []
        for reason in reasons:
            if "Financial stress" in reason: financial_indicators.append(reason.split(": ")[1])
            elif "Property ownership" in reason: property_indicators.append(reason.split(": ")[1])
        
        return {
            'original_username': contact.get('username', ''),
            'cleaned_name': contact.get('name', ''),
            'phone_extracted': contact.get('phone_extracted', ''),
            'email_extracted': contact.get('email_extracted', ''),
            'original_bio': contact.get('bio', ''),
            'original_category': contact.get('category', ''),
            'cleaned_website': contact.get('website', ''),
            'lead_score': score,
            'lead_classification': classification,
            'scoring_reasons': ' | '.join(reasons),
            **component_scores, # Unpack all component scores
            'financial_stress_indicators': ', '.join(financial_indicators),
            'property_ownership_indicators': ', '.join(property_indicators),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'follow_up_priority': 1 if classification == "HOT" else 2 if classification == "WARM" else 3,
            'estimated_probability': estimate_probability(score)
        }

    def validate_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Performs quality checks on the final results."""
        return {
            'missing_scores': df['lead_score'].isna().sum(),
            'invalid_scores': ((df['lead_score'] < 0) | (df['lead_score'] > 100)).sum(),
            'classification_distribution': df['lead_classification'].value_counts().to_dict(),
            'duplicates': df.duplicated(subset=['original_username']).sum(),
            'score_stats': df['lead_score'].describe().to_dict()
        }

    def print_summary(self, df: pd.DataFrame):
        """Prints a summary of the analysis to the console."""
        print("\n" + "="*70 + "\nENHANCED WHOLESALE LEAD SCORING SUMMARY\n" + "="*70)
        total = len(df)
        print(f"Total Leads Processed: {total}")
        
        print("\nLead Classifications:")
        for cls, count in df['lead_classification'].value_counts().items():
            print(f"  {cls}: {count} ({(count / total) * 100:.1f}%)")

        print("\nTop 5 Leads:")
        for _, lead in df.head(5).iterrows():
            print(f"  {lead['cleaned_name'] or lead['original_username']}: {lead['lead_score']} ({lead['lead_classification']})")
        print("="*70)

    def export_hot_leads(self, df: pd.DataFrame, path: str):
        """Exports only HOT leads to a separate CSV."""
        hot_leads = df[df['lead_classification'] == 'HOT'].copy()
        if not hot_leads.empty:
            cols = [
                'cleaned_name', 'phone_extracted', 'email_extracted', 'lead_score', 
                'financial_stress_indicators', 'property_ownership_indicators', 
                'scoring_reasons', 'follow_up_priority', 'estimated_probability'
            ]
            hot_leads[cols].to_csv(path, index=False)
            logger.info(f"Exported {len(hot_leads)} hot leads to {path}")
        else:
            logger.info("No hot leads found to export.")

    def generate_report(self, df: pd.DataFrame, path: str):
        """Generates a simple text file report."""
        try:
            with open(path, 'w') as f:
                f.write(f"WHOLESALE LEAD ANALYSIS REPORT\n{'='*50}\n\n")
                f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Leads Analyzed: {len(df)}\n\n")
                f.write("LEAD CLASSIFICATION SUMMARY:\n" + "-"*30 + "\n")
                for cls, count in df['lead_classification'].value_counts().items():
                    f.write(f"{cls}: {count} leads ({(count / len(df)) * 100:.1f}%)\n")
                
                hot_leads = df[df['lead_classification'] == 'HOT']
                if not hot_leads.empty:
                    f.write(f"\nHOT LEADS (Top Priority):\n" + "-"*30 + "\n")
                    for _, lead in hot_leads.iterrows():
                        f.write(f"• {lead['cleaned_name'] or lead['original_username']} (Score: {lead['lead_score']})\n")
            logger.info(f"Detailed report generated: {path}")
        except Exception as e:
            logger.error(f"Error generating report: {e}")