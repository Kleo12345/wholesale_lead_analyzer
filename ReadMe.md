Wholesale Lead Analyzer

The Wholesale Lead Analyzer is a powerful Python application designed for real estate investors and wholesalers. It automates the process of enriching, scoring, and prioritizing raw lead data from various sources. By leveraging automated web scraping and data analysis, this tool identifies the most promising "motivated seller" leads, saving you hours of manual research.

The script takes a simple CSV/TSV file of contacts (e.g., from Instagram, business directories) and outputs a detailed, scored, and prioritized list, complete with extracted contact information and the reasons behind each lead's score.
Key Features

    Comprehensive Lead Scoring: Assigns a score (0-100) to each lead based on a configurable set of rules.

    Data Enrichment: Automatically enhances lead data by:

        Extracting phone numbers and emails from text bios.

        Analyzing website content for real estate keywords (we buy houses, sell your home fast, etc.).

        Scraping Instagram profiles for business indicators and relevant bio keywords.

        Searching Google for LinkedIn profiles to identify professional experience in real estate.

        Querying Zillow's internal API for property data like "days on market" and price reductions.

    Intelligent Classification: Categorizes leads into HOT, WARM, COLD, and UNLIKELY to guide your outreach strategy.

    Proxy & Rate Limiting: Built-in support for proxy rotation and rate limiting to ensure reliable scraping without getting blocked.

    Configurable & Extensible: Easily customize keywords, scoring weights, and scraping behavior through a central settings file.

    Detailed Reporting: Generates a main CSV with all scored data, a separate file for HOT leads, and a summary text report.

    USA-Centric Filtering: Automatically filters out non-USA leads to focus your efforts.

Project Structure
Generated code

      
wholesale_lead_analyzer/
├── configs/
│   └── settings.py         # Main configuration file
├── data_processing/
│   ├── cleaner.py          # Data cleaning and filtering
│   └── scorer.py           # Core lead scoring logic
├── enrichment/
│   ├── social_media.py     # Instagram & LinkedIn analysis
│   └── web_scraper.py      # Zillow & generic website analysis
├── output/
│   └── report_generator.py # Generates CSVs and text reports
├── utils/
│   ├── proxy_manager.py    # Manages proxy rotation
│   └── web_utils.py        # Manages rate limiting
├── main.py                 # Main application entry point
└── README.md               # This file

    

IGNORE_WHEN_COPYING_START
Use code with caution.
IGNORE_WHEN_COPYING_END
How to Use
1. Prerequisites

    Python 3.8 or higher

    pip for installing packages

2. Installation

    Clone the repository (or set up your project files):
    Generated bash

      
git clone <your-repo-url>
cd wholesale_lead_analyzer

    

IGNORE_WHEN_COPYING_START
Use code with caution. Bash
IGNORE_WHEN_COPYING_END

Install the required Python packages:
Generated bash

      
pip install pandas requests beautifulsoup4

    

IGNORE_WHEN_COPYING_START

    Use code with caution. Bash
    IGNORE_WHEN_COPYING_END

3. Configuration (Important!)

Before running the analyzer, you must configure it. Open configs/settings.py and fill in the required information.
Required Configuration:

    Zillow ZUID (ZILLOW_ZUID)
    This is essential for the Zillow scraper to function.

        Go to https://www.zillow.com in your browser (Chrome/Firefox).

        Open Developer Tools (F12 or Ctrl+Shift+I).

        Go to the Application (Chrome) or Storage (Firefox) tab.

        Under Cookies -> https://www.zillow.com, find the cookie named zuid.

        Copy its value and paste it into the ZILLOW_ZUID variable in settings.py.
    Generated python

      
# configs/settings.py
ZILLOW_ZUID = "YOUR_PASTED_ZUID_VALUE_HERE"

    

IGNORE_WHEN_COPYING_START

    Use code with caution. Python
    IGNORE_WHEN_COPYING_END

Recommended Configuration:

    Proxies (PROXIES)
    For any serious use, proxies are highly recommended to avoid your IP address from being blocked by Google, Instagram, or Zillow.

        Obtain a list of HTTP proxies from a reliable provider.

        Add them to the PROXIES list in settings.py.
    Generated python

      
# configs/settings.py
PROXIES = [
    "http://user1:password@proxy1.com:8080",
    "http://user2:password@proxy2.com:8080",
    # ... and so on
]

    

IGNORE_WHEN_COPYING_START

    Use code with caution. Python
    IGNORE_WHEN_COPYING_END

    If you leave this list empty, the script will attempt to use a built-in free proxy finder, which is less reliable.

4. Prepare Your Input Data

Create an input CSV or TSV file (tab-separated is the default) with your raw leads. The script works best with the following columns, but will function with fewer:

    username: The lead's social media handle (e.g., Instagram username).

    name: The lead's full name.

    bio: The profile biography text.

    category: Business category (e.g., "Real Estate", "Contractor").

    website: The lead's website URL.

    address: A physical property address for Zillow lookup.

    location: A location string (e.g., "Los Angeles, CA, USA") for country filtering.

Example leads.csv:
Generated code

      
username	name	bio	category	address
john_investor	John Smith	Cash buyer for houses in any condition. We close fast! #webuyhouses	Real Estate	123 Main St, Anytown, USA
handy_mike	Mike Johnson	General contractor and handyman services. Call for a quote.	Construction

    

IGNORE_WHEN_COPYING_START
Use code with caution.
IGNORE_WHEN_COPYING_END
5. Run the Analyzer

Execute the script from your terminal, providing the input and output file paths.

Basic Usage:
Generated bash

      
python main.py input/my_leads.csv output/analyzed_leads.csv

    

IGNORE_WHEN_COPYING_START
Use code with caution. Bash
IGNORE_WHEN_COPYING_END

Command-Line Arguments:

    input_file: (Required) Path to your input CSV/TSV file.

    output_file: (Required) Path where the scored output CSV will be saved.

    --delimiter or -d: The character used to separate columns in your input file. Default is a tab (\t). For a comma, use ,.

    --hot-leads-file: (Optional) Path to save a separate, smaller CSV containing only the HOT leads for quick follow-up.

    --report-file: (Optional) Path to save a plain text summary report of the analysis.

Full Example:
Generated bash

      
python main.py data/raw_leads.tsv results/scored_leads.csv -d "	" --hot-leads-file results/hot_leads.csv --report-file results/summary_report.txt

    

IGNORE_WHEN_COPYING_START
Use code with caution. Bash
IGNORE_WHEN_COPYING_END
6. Review the Output

After the script finishes, you will find your generated files in the specified output directory.

    scored_leads.csv: The main output file containing all original data plus new columns like lead_score, lead_classification, scoring_reasons, phone_extracted, and email_extracted.

    hot_leads.csv (if specified): A clean, action-oriented list of your highest-priority leads.

    summary_report.txt (if specified): A high-level overview of the processing results.
