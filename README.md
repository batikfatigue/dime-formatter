# Dime Formatter
This app auto formats your bank csv statements into an import-ready file for Dime, a money tracking app.
Uses OpenAI's API to auto-categorise your bank transactions. 
Default model used: 'GPT 4.1'

To use:
- Create an API Key at https://platform.openai.com/api-keys
- Tutorial: https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key
- Rename .env.example to .env
- Paste your API key in .env
- run app.py (in dime-formatter/)
- upload your POSB bank statement (in csv format only!)
- download the formatted file
- import file to Dime

Dependencies: Run 'pip install -r requirements.txt' in the terminal

Current, only works with POSB bank statements

How to download your CSV bank statetements:
- Log in to POSB internet banking
- Complete the Authentication Process.
- Under My Accounts, select View transaction history.
- Filter desired account and transaction period
- Download statement
