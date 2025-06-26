# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dime Formatter is a Flask web application that processes POSB bank CSV statements and formats them for import into the Dime money tracking app. The application uses OpenAI's GPT-4o-mini to automatically categorize bank transactions with user-defined categories.

## Architecture

- **Flask App** (`dimeformatter/app.py`): Main web server with three routes:
  - `/` - File upload and processing with validation
  - `/categoriser` - Category selection interface  
  - `/download` - Formatted CSV download
- **Transaction Processor** (`dimeformatter/helper.py`): Core logic for parsing POSB CSV format, pattern matching transaction types, AI-powered categorization, and file validation
- **Database** (`dimeformatter/dbs.db`): SQLite database storing transaction codes and descriptions
- **Templates** (`dimeformatter/templates/`): HTML templates for the web interface

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp dimeformatter/.env.example dimeformatter/.env
# Add your OpenAI API key to .env
```

### Running the Application
```bash
# Run development server
cd dimeformatter
python app.py
```

### Testing
```bash
# Use sample data files in tests/ directory
# Upload tests/sample_data.csv through the web interface
```

## User Flow

1. **Category Selection**: User visits `/categoriser` to select expense/income categories
2. **File Upload**: User uploads POSB CSV file on file upload page
3. **Validation**: System validates file format and POSB-specific headers
4. **Processing**: Transactions are parsed and categorized using AI
5. **Download**: User downloads formatted CSV ready for Dime import

## Key Implementation Details

### Transaction Processing
- **POSB Format Support**: Handles POSB-specific CSV format with empty header lines and account information
- **Transaction Codes**: Processes specific POSB codes (INT, ITR, ICT, MST, UPI, UMC) with custom logic
- **Pattern Matching**: Complex logic for PayNow transfers, I-BANK transfers, and card transactions
- **Amount Parsing**: Extracts amounts from credit/debit columns with currency symbol removal

### File Validation (`validate_csv()`)
- **Format Check**: Validates .csv extension and file size (10MB limit)
- **POSB Header Detection**: Scans first 25 lines for POSB-specific header format
- **Encoding Support**: UTF-8 with fallback error handling
- **Error Reporting**: Returns specific error messages for different failure types

### AI Categorization (`categoriser()`)
- **OpenAI Integration**: Uses GPT-4o-mini with Singapore-specific financial prompts
- **Category Constraints**: Only allows user-defined categories plus "Miscellaneous"
- **Web Search**: Uses web search tool for unclear transactions
- **Output Format**: Returns "Category - Note" format with 4-word limit on notes

### Error Handling
- **File Validation**: Shows errors on same page without losing category selections
- **Form State Preservation**: Categories passed through form data to maintain user selections
- **Graceful Degradation**: Falls back to "Miscellaneous" for unclear transactions

## Configuration

- **OpenAI API Key**: Set in `dimeformatter/.env` (required for categorization)
- **Model**: GPT-4o-mini (configurable in helper.py:248)
- **Database**: `dimeformatter/dbs.db` (transaction codes)
- **Output**: `dimeformatter/import.csv` (Dime-compatible format)
- **File Limits**: 10MB max upload size
- **Encoding**: UTF-8 (compatible with POSB ASCII format)

## Known Issues & Limitations

- **POSB Only**: Currently only supports POSB bank statement format
- **Manual Categories**: User must select categories beforehand (no auto-discovery)
- **No Session Management**: Categories lost on browser refresh
- **Single File Processing**: No batch processing capability