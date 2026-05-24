# 🎬 IMDb Selenium Automation Suite

![IMDb Automation Hero](file:///C:/Users/Administrator/.gemini/antigravity/brain/ab65c825-94dd-4783-8f85-ec341bcd8d1d/imdb_automation_hero_1779642422196.png)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0%2B-green?logo=selenium&logoColor=white)](https://www.selenium.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade, robust automated testing framework designed to validate the core functionalities of [IMDb](https://www.imdb.com). This suite employs **Selenium WebDriver** and **Python** to execute a series of comprehensive tests across multiple user flows, ensuring data integrity, UI responsiveness, and search accuracy.

---

## 🌟 Key Features

- **🔍 Multi-Flow Validation**: Covers everything from basic search to complex advanced filtering.
- **🛡️ Robust Error Handling**: Each test case is isolated in its own `try/except` block to prevent cascading failures.
- **⏱️ Smart Waits**: Uses a combination of Implicit and Explicit waits (WebDriverWait) for stability.
- **📊 Automated Reporting**: Generates a detailed, human-readable `.txt` report after every execution.
- **🚀 Dynamic Navigation**: Real-time cross-navigation between films, actors, and search results.

---

## 🛤️ Test Flow Breakdown

The suite is organized into **5 core flows**, comprising a total of **15 test cases**:

### 1. Search Validation
- URL encoding verification.
- Keyword matching in results.
- Boundary testing with special characters.

### 2. Movie Detail Deep-Dive
- Runtime validation (numeric range checks).
- Rating integrity (0-10 scale).
- Cast section completeness.
- "More Like This" recommendation linkage.

### 3. Top Rated List Integrity
- Verification of entry counts (>= 25).
- Descending order validation based on ratings.
- URL uniqueness check for all movie cards.

### 4. Actor Profile & Navigation
- Name accuracy on profile pages.
- Filmography ("Known For") link validation.
- Cross-navigation from actor to movie pages.

### 5. Advanced Search Filtering
- Genre + Year + Sort parameter validation.
- Result count and date range accuracy.

---

## 🛠️ Technology Stack

- **Language**: Python 3.x
- **Framework**: Selenium WebDriver
- **Browser**: Google Chrome (ChromeOptions configured for stealth and stability)
- **Reporting**: Custom Python logging & file-based reporting

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Google Chrome installed
- ChromeDriver (matching your Chrome version)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/imdb-selenium-automation.git
   cd imdb-selenium-automation
   ```

2. **Install dependencies:**
   ```bash
   pip install selenium
   ```

---

## 📈 Usage

To execute the full test suite, run:

```bash
python imdb_test_cases/main.py
```

### Reviewing Results
Once completion, a report named `imdb_test_report.txt` will be generated in the project root. It includes:
- Start/End timestamps and duration.
- Success rate percentage.
- Detailed pass/fail notes for every single test case.
- Web element coverage summary.

---

## 📝 Sample Report Snippet

```text
================================================================
         IMDB SELENIUM AUTOMATED TEST REPORT
================================================================

  RUN METADATA
  ------------------------------------------
  Pass Rate    : 100.0%
  Total TCs    : 15 / 15
  
  > Flow 1 - Search Validation
    Result : 3/3 passed
      [OK] TC1    PASS  Search URL encodes query & results page confirms search term
      ...
```

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions for new test cases or improvements to the wait strategies, feel free to open an issue or submit a pull request.

---
*Created with ❤️ for quality assurance.*
