# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DimePrep is a Flask web application that processes POSB bank CSV statements and formats them for import into the Dime money tracking app. The application uses Google Gemini 2.5-flash to automatically categorize bank transactions in batches with user-defined categories. Features a modern React TSX landing page built with shadcn/ui components and Tailwind CSS.

## Architecture

- **Flask App** (`dimeformatter/app.py`): Main web server with three routes:
  - `/` - Modern React TSX landing page with file upload and processing
  - `/categoriser` - Category selection interface  
  - `/download` - Formatted CSV download
- **React Frontend**: Modern TSX landing page built with Vite, React 18, TypeScript, and shadcn/ui components
- **Transaction Processor** (`dimeformatter/helper.py`): Core logic for parsing POSB CSV format, pattern matching transaction types, batch AI-powered categorization, and file validation
- **Database** (`dimeformatter/dbs_codes.db`): SQLite database storing transaction codes and descriptions
- **Templates** (`dimeformatter/templates/`): HTML templates for category selection and file upload interfaces
- **Build System**: Vite for compiling TSX to production-ready static assets served by Flask

## Development Commands

### Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for React frontend
npm install

# Setup environment
cp dimeformatter/.env.example dimeformatter/.env
# Add your GEMINI_API_KEY to .env
```

### Building the Frontend
```bash
# Build React TSX landing page for production
npm run build

# For development with auto-rebuild
npm run dev
```

### Running the Application
```bash
# Run Flask development server
cd dimeformatter
python app.py
```

### Testing
```bash
# Use sample data files in tests/ directory
# Upload tests/sample_data.csv through the web interface
```

## User Flow

1. **Landing Page**: User visits modern React TSX landing page at `/` with DimePrep branding
2. **Category Selection**: User clicks "Start formatting" and visits `/categoriser` to select expense/income categories
3. **File Upload**: User uploads POSB CSV file on file upload page
4. **Validation**: System validates file format and POSB-specific headers
5. **Processing**: Transactions are parsed, filtered, and batch-categorized using AI
6. **Download**: User downloads formatted CSV ready for Dime import

## Key Implementation Details

### Transaction Processing
- **POSB Format Support**: Handles POSB-specific CSV format with empty header lines and account information
- **Transaction Codes**: Processes specific POSB codes (INT, ITR, ICT, MST, UPI, UMC, POS) with custom filtering logic
- **Pattern Matching**: Complex logic for PayNow transfers, I-BANK transfers, NETS QR payments, and card transactions
- **Reference Filtering**: Pre-processes transaction references to remove noise and extract meaningful data
- **Batch Processing**: Collects all transactions before sending to AI for efficient categorization

### File Validation (`validate_csv()`)
- **Format Check**: Validates .csv extension and file size (10MB limit)
- **POSB Header Detection**: Scans first 25 lines for POSB-specific header format
- **Encoding Support**: UTF-8 with fallback error handling
- **Error Reporting**: Returns specific error messages for different failure types

### AI Categorization (`gemini_sorter()`)
- **Gemini Integration**: Uses Google Gemini 2.5-flash with Singapore-specific financial prompts
- **Batch Processing**: Processes all transactions in a single API call for token efficiency
- **Structured Output**: Uses JSON schema for consistent categorization results
- **Category Constraints**: Only allows user-defined categories plus "Miscellaneous"
- **Google Search**: Integrated grounding tool for unclear transactions
- **Output Format**: Returns structured JSON with category and reasoning for each transaction

### Error Handling
- **File Validation**: Shows errors on same page without losing category selections
- **Form State Preservation**: Categories passed through form data to maintain user selections
- **Graceful Degradation**: Falls back to "Miscellaneous" for unclear transactions

## Configuration

- **Gemini API Key**: Set in `dimeformatter/.env` as `GEMINI_API_KEY` (required for categorization)
- **Model**: Google Gemini 2.5-flash (configurable in helper.py)
- **Database**: `dimeformatter/dbs_codes.db` (transaction codes and descriptions)
- **Output**: `dimeformatter/import.csv` (Dime-compatible format)
- **File Limits**: 10MB max upload size
- **Encoding**: UTF-8 (compatible with POSB ASCII format)
- **Batch Size**: All transactions processed in single API call for efficiency

## Known Issues & Limitations

- **POSB Only**: Currently only supports POSB bank statement format
- **Manual Categories**: User must select categories beforehand (no auto-discovery)
- **No Session Management**: Categories lost on browser refresh
- **API Dependency**: Requires Gemini API for transaction categorization
- **JSON Parsing**: AI response must be valid JSON format for successful processing