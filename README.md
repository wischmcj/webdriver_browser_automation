# WebDriver Browser Automation

A collection of scripts using browser automation/emulation libaries (i.e. Selenium WebDrive) for various web scraping and automation tasks. This repository serves as a centralized location for storing and organizing code I create for smaller automation tasks.

## Overview

The scripts here are designed to handle rather specific web automation tasks, often only authenticating then pulling one specific type of data from a webpage. Scripts may therefore not be generally applicable.

## Prerequisites

- Python 3.x
- Selenium WebDriver
- Chrome browser (for Chrome WebDriver)
- Redis server (for some scripts)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd webdriver_browser_automation
```

2. Install required dependencies:
```bash
pip install selenium numpy redis
```

3. Download ChromeDriver and ensure it's in your PATH, or use webdriver-manager:
```bash
pip install webdriver-manager
```

## Scripts

### LinkedIn Scraper (`selenium/linked_in_scraper.py`)

**Functionality**: Automates LinkedIn profile interactions to extract followed companies and perform automated following actions.

**Key Features**:
- Automated LinkedIn login with email/password authentication
- CAPTCHA detection and handling (supports reCAPTCHA)
- Profile navigation and data extraction
- Company following automation
- Redis integration for storing company links
- Scroll-based content loading for dynamic pages
- Error handling and logging

**Main Functions**:
- `linkedin_login()`: Handles LinkedIn authentication
- `complete_captcha_if_needed()`: Detects and attempts to solve reCAPTCHAs
- `get_profile_section()`: Returns specific profile sections and their tabs by name 
- `scroll_and_act()`: Implements scroll until bottom functionality, ausing java script to populate page data and processing that data in batches 
- `follow_company()`: Automates pulling of followed companies from li profile
- `linkedin_login_and_get_followed_companies()`: Main orchestration function

**Usage**:
Set environment variables for LinkedIn credentials:
```bash
export LINKEDIN_USERNAME="your_email@example.com"
export LINKEDIN_PASSWORD="your_password"
```

Run the script:
```bash
python selenium/linked_in_scraper.py
```

## License

This project is for educational and personal use only. Please ensure compliance with the terms of service of any websites referenced.
