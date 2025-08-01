---

# 🧠 Wholesale Lead Analyzer

**Wholesale Lead Analyzer** is a powerful Python tool built for real estate investors and wholesalers. It automates the enrichment, scoring, and prioritization of raw lead data — helping you find the most promising *motivated seller* leads with minimal manual effort.

Simply feed it a CSV or TSV file of contacts (e.g., from Instagram or business directories), and it outputs a prioritized, scored list with enriched details and scoring explanations.

---

## 🚀 Key Features

* **🔢 Lead Scoring Engine**
  Assigns a 0–100 score to each lead using customizable rules.

* **🔍 Automated Data Enrichment**

  * Extracts phone numbers and emails from bios.
  * Analyzes websites for real estate keywords (e.g., *we buy houses*, *sell your home fast*).
  * Scrapes Instagram for business indicators.
  * Locates LinkedIn profiles via Google for real estate experience.
  * Pulls Zillow property info (e.g., *days on market*, *price reductions*) via internal API.

* **🔥 Lead Classification**
  Automatically categorizes leads as `HOT`, `WARM`, `COLD`, or `UNLIKELY`.

* **🛡 Proxy & Rate Limiting Support**
  Avoids IP bans with optional rotating proxies and request throttling.

* **⚙ Fully Configurable**
  Customize keywords, scoring weights, and scraping behavior via `settings.py`.

* **📊 Reporting System**
  Generates:

  * A detailed CSV with all scored data
  * A filtered HOT leads CSV
  * A plain text summary report

* **🇺🇸 U.S.-Focused**
  Filters out non-USA leads to narrow focus.

---

## 🧱 Project Structure

```
wholesale_lead_analyzer/
├── configs/
│   └── settings.py         # Main configuration file
├── data_processing/
│   ├── cleaner.py          # Cleans and filters raw input
│   └── scorer.py           # Scoring logic
├── enrichment/
│   ├── social_media.py     # Instagram & LinkedIn analysis
│   └── web_scraper.py      # Zillow & website analysis
├── output/
│   └── report_generator.py # Generates CSVs & text reports
├── utils/
│   ├── proxy_manager.py    # Proxy rotation logic
│   └── web_utils.py        # Rate limiting utilities
├── main.py                 # Entry point
└── README.md               # This file
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites

* Python 3.8+
* `pip` package manager

### 2. Install Dependencies

```bash
git clone <your-repo-url>
cd wholesale_lead_analyzer
pip install pandas requests beautifulsoup4
```

### 3. Configuration (IMPORTANT)

Open `configs/settings.py` and set the required parameters.

#### Required:

**Zillow ZUID (for property data):**

1. Visit [zillow.com](https://www.zillow.com)
2. Open Developer Tools (F12)
3. Go to `Application > Cookies > https://www.zillow.com`
4. Copy the value of the `zuid` cookie
5. Paste it into `ZILLOW_ZUID` in `settings.py`:

```python
ZILLOW_ZUID = "YOUR_PASTED_ZUID_VALUE_HERE"
```

#### Recommended:

**Proxy List:**

Add paid or reliable free HTTP proxies to avoid getting blocked:

```python
PROXIES = [
    "http://user1:password@proxy1.com:8080",
    "http://user2:password@proxy2.com:8080",
]
```

> If left empty, the script will attempt to use a built-in free proxy finder (less reliable).

---

## 📥 Preparing Input Data

Prepare a `CSV` or `TSV` file with the following columns:

| Column     | Description                                       |
| ---------- | ------------------------------------------------- |
| `username` | Social handle (e.g., Instagram username)          |
| `name`     | Full name of lead                                 |
| `bio`      | Profile biography text                            |
| `category` | Business category (e.g., Real Estate, Contractor) |
| `address`  | Property address (for Zillow lookup)              |
| `website`  | Website URL                                       |
| `location` | e.g., `Los Angeles, CA, USA`                      |

**Example: `leads.csv`**

```csv
username,name,bio,category,address
john_investor,John Smith,"Cash buyer for houses in any condition. We close fast! #webuyhouses",Real Estate,"123 Main St, Anytown, USA"
handy_mike,Mike Johnson,"General contractor and handyman services. Call for a quote.",Construction,
```

---

## 🧪 Running the Analyzer

Run the script via terminal:

```bash
python main.py input/leads.csv output/analyzed.csv
```

### Optional Flags:

| Flag               | Description                              |
| ------------------ | ---------------------------------------- |
| `-d`               | Delimiter for input file (default: `\t`) |
| `--hot-leads-file` | Path for CSV with only HOT leads         |
| `--report-file`    | Path for plain-text summary report       |

### Full Example:

```bash
python main.py data/raw_leads.tsv results/scored.csv -d "\t" \
  --hot-leads-file results/hot_leads.csv \
  --report-file results/summary.txt
```

---

## 📤 Output Files

* **`scored_leads.csv`**: Enriched, scored data with fields like:

  * `lead_score`
  * `lead_classification`
  * `scoring_reasons`
  * `phone_extracted`
  * `email_extracted`

* **`hot_leads.csv`**: Filtered list of top-priority leads (optional).

* **`summary_report.txt`**: A concise breakdown of the results (optional).

---

## 🧩 Final Notes

* For large-scale lead processing, rotate proxies and tune scraping delays.
* Custom rules can be added in `scorer.py` and `settings.py`.
* Designed with U.S. real estate in mind — international leads are excluded by default.

---