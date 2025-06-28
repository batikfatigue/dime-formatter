# DimePrep
This app auto formats your bank CSV statements into an import-ready file for Dime, a money tracking app.
Uses Google Gemini 2.5-flash to auto-categorise your bank transactions with batch processing for efficiency.
Features a modern React TSX landing page built with shadcn/ui components.

## Setup

### Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for React frontend
npm install
```

### Configure API Key
- Create a Gemini API Key at https://aistudio.google.com/app/apikey
- Rename `dimeformatter/.env.example` to `dimeformatter/.env`
- Add your API key: `GEMINI_API_KEY=your_key_here`

### Build Frontend
```bash
# Build React TSX landing page
npm run build
```

### Run Application
```bash
# Start Flask development server
cd dimeformatter
python app.py
```

## Usage
1. Visit the modern DimePrep landing page
2. Click "Start formatting" to select your expense/income categories
3. Upload your POSB bank statement (CSV format only)
4. Download the formatted file
5. Import file to Dime

Currently only works with POSB bank statements.

How to download your CSV bank statetements:
- Log in to POSB internet banking
- Complete the Authentication Process.
- Under My Accounts, select View transaction history.
- Filter desired account and transaction period
- Download statement
