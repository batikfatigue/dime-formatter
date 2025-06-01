def formatter_dbs(text_stream, categories):
    import csv, os, sqlite3, re
    # Gets directory for helper.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Generates the path for import.csv
    export_path = os.path.join(script_dir, 'import.csv')

    # Clears the import file and writes in the header
    header = ['Date','Note','tn_amt','Category','Type']
    with open(export_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        conn = sqlite3.connect('dimeformatter/dbs.db')
        cursor = conn.cursor()
    
    def if_ibank(references):
        has_ibank = False
        has_transfer = False
        bank_name = None
        
        for item in references:
            if "I-BANK" in item:
                has_ibank = True
                if ":" in item:
                    bank_part = item.split(":")[0].strip()
                    if bank_part:
                        bank_name = "Transfer to: " + bank_part + " Bank"
            elif "Transfer" in item:
                has_transfer = True
        
        if has_ibank and has_transfer and bank_name:
            return [bank_name]

    # Reformat CSV
    with text_stream as import_file, open(export_path, mode='a', encoding='utf-8') as export_file:
        data = csv.reader(import_file)
        writer = csv.writer(export_file)
        i = 1
        for row in data:
            if row == []: # skip blank rows
                continue
            # Starts loop logic when first item of the row is a date
            elif row[0][0].isnumeric(): 
                # Index 1: txCode, Index 2: Expense, Index 3: Income, Index 4/5/6: txReference
                tx_code = row[1]
                references = row[4:7]
                full_text = " ".join(references)
                print(references)
                # Check income or expense
                date = row[0]
                note = ''
                if row[3] != ' ': 
                    tn_amt = row[3][1:]
                    tn_nature = 'Income'
                else:
                    tn_amt = row[2][1:]
                    tn_nature = 'Expense'

                # Extract transaction type (FAST/PAYNOW etc.)
                query = "SELECT desc FROM dbs WHERE code = ?"
                cursor.execute(query, (tx_code,))
                tx_type = cursor.fetchone()[0]
                        
                # Categorising based on Pattern Extraction
                if tx_code == 'INT':
                    note = 'Interest Earned'
                    category = 'Interest'
                    newRow = [date, note, tn_amt, category, tn_nature]

                    writer.writerow(newRow)
                    print(f'Row{i} done')
                    i += 1
                    continue

                if tx_code == 'ITR':
                    indices = [1,2,3]
                    for i, item in enumerate(references):
                        if "I-BANK" in item:
                            indices.remove(i)
                            bank_info = item.split(":")
                            # Case 1: Personal Transfers (Account-No. : I-BANK)
                            if len(bank_info) == 2:
                                # Sub Case 1: Transfer to consumer accounts
                                if bank_info[1] == " I-BANK":
                                    recipient = bank_info.strip()
                                    notes = ''.join([references[x.strip()] for x in indices])
                                    if notes:
                                        return ['Transfer to account: ' + recipient, notes]
                                    else:
                                        return ['Transfer to account: ' + recipient] 

                                # Sub Case 2: Transfer to corporate accounts
                                if bank_info[1] == "I-BANK":
                                    bank_name = bank_info[0]
                                    random_note = references[indices[0]].strip()
                                    if not random_note.startswith('OTHR') and random_note.isnumeric():
                                        recipient = random_note
                                        return ["Transfer to: " + bank_name + " " + recipient]
                                    else:
                                        recipient = references[indices[1]].strip()
                                        return ["Transfer to: " + bank_name + " " + recipient]
                            
                            # Case 2: Handle personal PayLah transfers
                            elif 'SEND BACK FROM PAYLAH!' in full_text:
                                return ['SEND BACK FROM PAYLAH ACCOUNT']
                            elif 'TOP-UP TO PAYLAH!' in full_text:
                                return ['TOP-UP TO PAYLAH ACCOUNT']
                            
                            # Handle potential pattern spotted for ICT transactions   
                            elif len(bank_info) == 3:
                                bank_name = bank_info[0]
                                recipient = bank_info[1]
                                return ["Transfer to: " + bank_name + " " + recipient]

                
                if tx_code == 'ICT':
                    result = []
                    
                    # Case 1: Outgoing PayNow Transfer
                    if "PayNow Transfer" in full_text and any("To:" in item for item in references):
                        # Extract recipient
                        for item in references:
                            if "To:" in item:
                                recipient = item.replace("To:", "").strip()
                                if recipient:
                                    result.append(f"To: {recipient}")
                                break
                        
                        # Extract message after OTHR
                        for item in references:
                            if item.startswith("OTHR ") and len(item) > 5:
                                message = item[5:].strip()
                                if message:
                                    result.append(message)
                                break
                        
                        return result
                    
                    # Case 2: Incoming PayNow Transfer
                    elif "PayNow" in full_text and any("From:" in item for item in references):
                        # Extract sender
                        for item in references:
                            if "From:" in item:
                                sender = item.replace("From:", "").strip()
                                if sender:
                                    result.append(f"From: {sender}")
                                break
                        
                        # Extract message after OTHR
                        for item in references:
                            if item.startswith("OTHR ") and len(item) > 5:
                                message = item[5:].strip()
                                if message:
                                    result.append(message)
                                break
                        
                        return result
                    
                    # Case 5: Outgoing External Internet Banking Transfer
                    else:
                        bank_name = None
                        is_ibank = False
                        
                        references_copy = references.copy()
                        for i, item in enumerate(references):
                            if "I-BANK" in item:
                                is_ibank = True
                                references_copy.pop(i)
                                bank_part = item.split(":")
                                if ":" in item:
                                    bank_name = bank_part[0].strip()
                                    if bank_name:
                                        result.append("Transfer to: " + bank_part + " Bank")
                            elif len(item) == 19 and not item.startswith('OTHR'):
                                references_copy.pop(i)
                                result.append('Transaction Category: ' + item[0:4])
                        if is_ibank:
                            return result
                        
                        # Case 3 & 4: Incoming External Internet Banking Transfer (Meaningless alphanumerical values)
                        # PS. OKX can be meaningful data, but you need intelligence
                        for item in references:
                            if not item.startswith("OTHR") and item.strip() != "OTHR":
                                result.append(item.strip())
                                if len(result) >= 3:
                                    break
                        
                        return result

                found = False
                if row[1] in ['MST', 'UPI', 'UMC', 'UMC-S']:
                    references = [x for x in references if not re.search(r'\d{4}-\d{4}-\d{4}-\d{4}', x)]
                else: 
                    reference = row[4:7]
                    dup = [k for k in reference]
                    
                    for j, ref in enumerate(dup):
                        if ref.startswith('PayNow Transfer'):
                            reference.remove(dup[j])
                        if ref.startswith('OTHR'):
                            ref = ref[5:]
                            misc, note = categoriser(categories, ref)
                            if 'Miscellaneous' in misc:
                                reference.remove(dup[j])
                            else:
                                category = misc
                                found = True
                                break

                print(reference)
                if not found:
                    category, note = categoriser(categories, reference)
                print(note)
                print(category)

                # we will let the user manually type in categories that chatgpt sort as misc, less they want to sort it as misc

                newRow = [date, note, tn_amt, category, tn_nature]


                f = open(export_path, 'a', newline='', encoding='utf-8', errors='ignore')
                writer.writerow(newRow)
                print(f'Row{i} done')
                i += 1
                 
        conn.close()
        

# *para: categories will take in a list of preset categories in dime
# returns a category
def categoriser(categories, tn_data): 
    from openai import OpenAI
    import os, dotenv

    dotenv.load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    categories = categories + ['Miscellaneous']
    #tn_nature, tx_type, tn_ref = tn_data


    # Define the prompt or input text
    # reference = 'iCloud Subscription'

    response = client.responses.create(
        model="gpt-4o-mini",
        tools=[{"type": "web_search_preview"}],
        # tool_choice="auto",
        input=[
            {"role": "system",
             "content": """You ara a financial analyst with a knowledge base on much of the bank transactions that happen in Singapore. Your job is to:
                            Categorize a bank transaction based on the provided information, including transaction nature (debit/credit), up to three transaction notes, and transaction type. Focus on extracting relevant information from the transaction notes, ignoring noise. The output category should be followed by a brief note of less than 4 word, and is not just a repeat of the category.
                            Only pick a Category from {}.
                            # Steps

                            1. **Parse Transaction Details**: Identify and extract relevant information from the transaction nature, transaction notes, and transaction type.
                            2. **Filter Noise**: From the transaction notes, separate and remove noise. Emphasize identifying key terms in notes.
                            3. **Identify Transaction Type and Nature**: Analyze the transaction type and nature for context and relevance.
                            4. **Determine Category and Note**: Based on the extracted relevant information, classify the transaction into a category and provide a note of less than four words after the category.
                            5. If unsure of the category, use the web search tool. If still unclear, default to 'Miscellaneous.

                            # Output Format

                            - The output should be in the format: "Category - Note." For example, "Transport - BUS/MRT" or "Bills - GOMO Phone Bills."

                            # Examples

                            ### Example 1
                            **Input**:
                            - Transaction Nature: Expense
                            - Transaction Ref: 'BUS/MRT 635809888 SI SGP 13MAY'
                            - Transaction Type: 'Point-of-Sale Transaction'

                            **Process**:
                            - Extract 'BUS/MRT' as important information.
                            - Note the transaction nature as 'Debit' and type as 'Point-of-Sale Transaction'.

                            **Output**:
                            - "Transport - BUS/MRT"

                            ### Example 2
                            **Input**:
                            - Transaction Nature: Expense
                            - Transaction Ref: 'GOMO MOBILE PLAN       SI SGP 03MAY', '4628-4500-5030-3180'
                            - Transaction Type: 'Debit Card Transaction'

                            **Process**:
                            - Extract 'GOMO MOBILE PLAN' as important information. Disregard the second transaction note due to a lack of meaningful context.
                            - Note the transaction nature as 'Expense' and type as 'Debit transaction'.

                            **Output**:
                            - "Bills - GOMO Phone Bills"

                            # Notes

                            - Ignore numbers and date-like strings in the transaction notes as they are generally noise.
                            - Consider typical transaction categorizations like "Transport", "Income", "Groceries", etc.
                            - Ensure extracted transaction information aligns with typical financial categories.
                            - Use web search judiciously and default to "Miscellaneous" if the category remains unclear.
                            - All analyses should be performed and categorized under the context of Singapore.""".format(categories)
            },

            {"role": "user",
              "content": tn_data
            }
        ]
    )

    print("\n")
    print(
        f'Tool Choice: {response.tool_choice} | Tools: {response.tools} | Total Tokens: {response.usage.total_tokens} | Output: "{response.output_text}"'
    )
    print("\n")
    category, note = response.output_text.split(' - ')
    return category, note


