# Dime Formatter
This app auto formats your bank csv statements into an import-ready file for Dime, a money tracking app.
Uses OpenAI's API to auto-categorise your bank transactions.
For increased accuracy in auto-categorising, upgrade your model to gpt-4, and replace model in line 111 of helper.py to 'gpt-4o'/'gpt-4'.

To use:
- Create an API Key at https://platform.openai.com/api-keys
- Tutorial: https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key
- Paste your API key in .env
- run home.py (in root/)
- upload your POSB bank statement (in csv format only!)
- download the formatted file
- import file to Dime

P.S. Only works with POSB bank statements

How to download your CSV bank statetements:
- Log in to POSB internet banking
- Complete the Authentication Process.
- Under My Accounts, select View transaction history.
- Filter desired account and transaction period
- Download statement
