def formatter_dbs(text_stream, categories):
    import csv, os, sqlite3, re, json
    # Gets directory for helper.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Generates the path for import.csv
    export_path = os.path.join(script_dir, 'import.csv')

    # Clears the import file and writes in the header
    header = ['Date','Note','Amount','Category','Type']
    with open(export_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    conn = sqlite3.connect('dimeformatter/dbs_code.db')
    cursor = conn.cursor()
    
    # Reformat CSV
    with text_stream as import_file, open(export_path, mode='a', encoding='utf-8') as export_file:
        data = csv.reader(import_file)
        writer = csv.writer(export_file)
        # Payload -> Filtered data for API call, Reference -> Noise from statement
        payload_data = []
        reference_data = []
        for row in data:
            if row == []: # skip blank rows
                continue
            # Commence categorisation when first item of the row is a date
            elif row[0][0].isnumeric(): 
                # Index 0: Date, Index 1: Code, Index 2: Expense, Index 3: Income, Index 4/5/6: References
                tx_code = row[1]
                tx_date = row[0]
                tx_note = ''
                references = row[4:]
                references.pop()
                all_references = " ".join(references)
                # Check income or expense
                if row[3] != ' ': 
                    tx_amt = row[3][1:]
                    tx_nature = 'Income'
                    nature = 'Incoming'
                else:
                    tx_amt = row[2][1:]
                    tx_nature = 'Expense'
                    nature = 'Outgoing'

                # Extract transaction type (FAST/PAYNOW, etc.)
                query = "SELECT desc FROM dbs WHERE code = ?"
                cursor.execute(query, (tx_code,))
                tx_type = cursor.fetchone()[0] 
                        
                # Remove noise from references (Based on Transaction Code)
                filtered = False
                if len(references) == 3:
                    filtered_references = []
                    if tx_code == 'INT':
                        filtered_references = ['Interest Earned']
                        filtered = True

                    elif tx_code == 'ITR' and not filtered:
                        indices = list(range(len(references)))
                        for i, item in enumerate(references):
                            if "I-BANK" in item:
                                indices.pop(i)
                                bank_info = item.split(":")
                                # Case 1: Personal Transfers (Account-No. : I-BANK)
                                if len(bank_info) == 2:
                                    #   Sub Case 1: Transfer to consumer accounts
                                    if bank_info[1] == " I-BANK":
                                        recipient = bank_info[0].strip()
                                        other_notes = ''.join([references[x].strip() for x in indices])
                                        if other_notes: 
                                            filtered_references = ['Transfer to account: ' + recipient, 'Notes: ' + other_notes]
                                            filtered = True
                                        else:
                                            filtered_references = ['Transfer to account: ' + recipient] 
                                            filtered = True

                                    # Sub Case 2: Transfer to corporate accounts
                                    if bank_info[1] == "I-BANK" and not filtered:
                                        bank_name = bank_info[0]
                                        random_note = references[indices[0]].strip()
                                        if not random_note.startswith('OTHR') and random_note.isnumeric():
                                            recipient = random_note
                                            filtered_references = ["Transfer to: " + bank_name + " " + recipient]
                                            filtered = True
                                        else:
                                            recipient = references[indices[1]].strip()
                                            filtered_references = ["Transfer to: " + bank_name + " " + recipient]
                                            filtered = True
                                
                            # Case 2: Handle personal PayLah transfers
                            elif 'SEND BACK FROM PAYLAH!' in all_references and not filtered:
                                filtered_references = ['SEND BACK FROM PAYLAH ACCOUNT']
                                filtered = True

                            elif 'TOP-UP TO PAYLAH!' in all_references and not filtered:
                                filtered_references = ['TOP-UP TO PAYLAH ACCOUNT']
                                filtered = True
                                

                    
                    elif tx_code == 'ICT' and not filtered:
                        # Case 1: Outgoing PayNow Transfer
                        if "PayNow Transfer" in all_references and any("To:" in item for item in references):
                            # Extract recipient
                            for item in references:
                                if "To:" in item:
                                    recipient = item.replace("To:", "").strip()
                                    if recipient:
                                        filtered_references.append(f"To: {recipient}")
                                    break
                            
                            # Extract message after OTHR
                            for item in references:
                                if item.startswith("OTHR ") and len(item) > 5:
                                    message = item[5:].strip()
                                    if message:
                                        filtered_references.append('Note: ' + message)
                                        filtered = True
                                    break
                        
                        # Case 2: Incoming PayNow Transfer
                        elif "PayNow" in all_references and any("From:" in item for item in references) and not filtered:
                            # Extract sender
                            for item in references:
                                if "From:" in item:
                                    sender = item.replace("From:", "").strip()
                                    if sender:
                                        filtered_references.append("From: " + sender)
                                    break
                            
                            # Extract message after OTHR
                            for item in references:
                                if item.startswith("OTHR ") and len(item) > 5:
                                    message = item[5:].strip()
                                    if message:
                                        filtered_references.append("Note: " + message)
                                        filtered = True
                                    break
                        
                        # Case 5: Outgoing External Internet Banking Transfer 

                        elif not filtered:
                            bank_name = None
                            if "I-BANK" in all_references:
                                for i in range(len(references) - 1, -1, -1):
                                    item = references[i]
                                    if "I-BANK" in item:
                                        references.remove(item)
                                        if ":" in item:
                                            bank_part = item.split(":")
                                            bank_name = bank_part[0].strip()
                                            if bank_name:
                                                filtered_references.append("Transfer to: " + bank_name + " Bank")
                                    # Sub Case: ('PHON MBXXXXX,Trus:XXXXX:I-BANK,Simba Bills)
                                    elif re.match(r'^[A-Z]{4} ', item) and not item.startswith('OTHR'):
                                        references.remove(item)
                                        filtered_references.append('Category: ' + item[0:4])
                                        filtered = True

                                if references:
                                    filtered_references.append('Note: ' + references[0])

                            # Case 3 & 4: Incoming External Internet Banking Transfer (Meaningless alphanumerical values)
                            # PS. OKX can be meaningful data, but you need intelligence
                            if tx_nature == 'Income' and not filtered:
                                for item in references:
                                    if not item.startswith("OTHR") and item.strip() == "OTHR":
                                        filtered_references.append(item[5:].strip())
                                        filtered = False
                                        break

                            
                    if tx_code in ['MST', 'UPI', 'UMC', 'UMC-S'] and not filtered:
                        filtered_references = [x for x in references if not re.search(r'\d{4}-\d{4}-\d{4}-\d{4}', x) and x]
                        filtered = True

                    if tx_code == 'POS' and not filtered:
                        if 'NETS QR PAYMENT' in all_references:
                            if "TO: " in all_references:
                                filtered_references.append('To: ' + all_references.split('TO: ')[1].split(',')[0])
                                filtered = True
                
                payload_data.append({
                    'nature': nature,
                    'amount': tx_amt,
                    'references': filtered_references if filtered else references,
                    'type': tx_type
                })
                reference_data.append([tx_date, tx_amt, tx_nature])
                categories = categories + ['Miscellaneous']

        statement = json.loads(gemini_sorter(categories, payload_data))
        print(statement)

        f = open(export_path, 'a', newline='', encoding='utf-8', errors='ignore')
        for i, j in zip(statement, reference_data):
            newRow = [j[0], i['Reasoning'], j[1], i['category'], j[2]]
            writer.writerow(newRow)
        conn.close()
        
def gemini_sorter(categories, tx_data):
    from google import genai
    from google.genai import types
    import os, dotenv, json
    dotenv.load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
            "category": {
                "type": "string",
                "enum": categories
            },
            "Reasoning": {
                "type": "string"
            },
            "alt_category": {
                "type": "string"
            }
            },
            "required": ["category","Reasoning"]
        }
        }
    
    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You ara a Singaporean financial analyst.  Your task is to: "
                "Categorize a list of bank transactions based on the provided information in each transaction, including: "
                "1. transaction nature (incoming/outgoing), "
                "2. transaction amount, "
                "3. up to three transaction references, "
                "4. and transaction type. "
                "For each transaction, provide the `category` from the allowed list and "
                "a brief `Reasoning` (5 to 20 words)"
                "If category is miscellaneous, provide an `alt_category` (1 word). "
                "Ignore any irrelevant noise in the transaction notes."
                ),
                response_mime_type="application/json",
                response_schema = response_schema,
                tools = [grounding_tool]
        ),
        contents=json.dumps(tx_data),
        
    ) 
    return response.text



# *para: categories will take in a list of preset categories in dime
# returns a category
def openai_categoriser(categories, tn_data): 
    from openai import OpenAI
    import os, dotenv

    dotenv.load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    categories = categories + ['Miscellaneous']
    reference = '[' + ', '.join(map(repr, reference)) + ']'


    # Define the prompt or input text
    # reference = 'iCloud Subscription'

    completion = client.chat.completions.create(
    model="gpt-4.1-nano-2025-04-14",
    messages=[
        {"role": "system", "content": """You are an bank transactions analyser.
                                        Categories: {}.
                                        You pick the most suitable category, based off transaction references.
                                        Don't deduce, use miscellaneous when there's little context.
                                        Reply with one word for the category, followed by a dash, then a note of <4 words.
                                        The note should be extracted from the references.
                                        Format: "Category - Note".""".format(categories)},

        {"role": "user", "content": reference}
    ]
    )

    response = completion.choices[0].message.content
    category, note = response.split(' - ')

    return category, note


def validate_csv(file):
    if not file:
        return False, "No file uploaded"
    
    if not file.filename:
        return False, "No file selected"
    
    if not file.filename.lower().endswith('.csv'):
        return False, "Only CSV files are allowed"
    
    # Check file size
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)

    if size > 10 * 1024 * 1024:
        return False, "File too large (max 10MB)"
    
    # Check content if CSV - First line should have comma
    try:
        for i in range(25):
          line = file.readline().decode("utf-8")
          # Check for POSB-specific header
          if "Transaction Date,Reference,Debit Amount,Credit Amount" in line:
              file.seek(0)
              return True, "Valid"
          
        file.seek(0)
        return False, "Not a valid POSB CSV format"
    
    except UnicodeDecodeError:
        return False, "File encoding not supported"
    

