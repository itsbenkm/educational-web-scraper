# Educational Scraper

A sophisticated, production-ready web scraping project built with Python and Scrapy. This repository is designed for educational purposes to demonstrate advanced scraping techniques, defensive programming, and robust architecture.

## 🚀 Overview

This project scrapes the `fashionbroda.x.yupoo.com` catalog, extracting category metadata, album information, and image assets. It is structured to handle the complexities of web scraping at scale while maintaining clean, readable code and detailed documentation within the source.

### Key Features

- **Defensive Programming:** Implements rigorous checks at system boundaries to handle inconsistent HTML structures and network failures.
- **Session & Identity Management:** Custom middlewares for rotating User-Agents and Proxy management to simulate natural browsing behavior.
- **Multi-Spider Architecture:**
  - `fashion_broda`: Scrapes top-level categories and seller information.
  - `albums`: Deep-dives into specific categories to list all product albums.
  - `images`: Collects high-quality image paths and metadata for all catalog items.
- **Structured Data Export:** Automated JSON feeds for all scraped entities with precise field ordering.
- **Resilient Crawling:** Configured with job persistence (JobDir) to allow pausing and resuming of long-running crawls.

## 🛠️ Tech Stack

- **Framework:** Scrapy (Python)
- **Concurrency:** Twisted Reactor (Asyncio)
- **Data Handling:** Pathlib for cross-platform path resolution
- **Compliance:** ROBOTSTXT_OBEY = False (customized for specific study needs)

## 📁 Project Structure

```text
fashionbroda/
├── fashionbroda/           # Scrapy project root
│   ├── resources/          # Custom User-Agents and Proxy lists
│   ├── scraped_data/       # Output directory for JSON/Image data
│   ├── spiders/            # Spider implementations
│   └── settings.py         # Advanced Scrapy configurations
└── scrapy.cfg              # Deployment configuration
```

## 🚥 Getting Started

### Prerequisites

- Python 3.10+
- Virtual Environment (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fashionbroda-scraper.git
   cd fashionbroda-scraper
   ```
2. Set up the environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

### Running Spiders

To run the main spider and export data:

```bash
cd fashionbroda
scrapy crawl fashion_broda
```

## 🎓 Educational Value

This repo is a great reference for:

1. **Middleware Design:** Look at `middlewares.py` to see how requests are intercepted and modified.
2. **Defensive Logic:** Check `spiders/fashion_broda.py` for comments on handling "unstable" web elements.
3. **Resource Management:** See how `settings.py` manages external resource files like `proxies.txt`.

## ⚠️ Disclaimer

This tool is for educational purposes only. Always respect the Terms of Service of the websites you interact with and ensure your scraping activities are ethical and legal.

---

_Created by [b3n]_
