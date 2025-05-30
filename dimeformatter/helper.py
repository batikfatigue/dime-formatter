def formatter_dbs(text_stream, categories):
    import csv, os, sqlite3, re
    # Gets directory for helper.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Generates the path for import.csv
    export_path = os.path.join(script_dir, 'import.csv')

    # Clears the import file and writes in the header
    header = ['Date','Note','Amount','Category','Type']
    with open(export_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        conn = sqlite3.connect('dimeformatter/dbs.db')
        cursor = conn.cursor()
    
    # Reformat CSV
    with text_stream as import_file, open('export_path', mode='a', encoding='utf-8') as export_file:
        data = csv.reader(import_file)
        writer = csv.writer(export_file)
        i = 1
        for row in data:
            if row == []: # skip blank rows
                continue
            # Starts loop logic when first item of the row is a date
            elif row[0][0].isnumeric(): 
                # Index 1: tnCode, Index 2: Expense, Index 3: Income, Index 4,5,6: TnReference
                tn_code = row[1]
                references = row[4,5,6]
                print(references)
                # Check income or expense
                date = row[0]
                note = ''
                if row[3] != ' ': 
                    amount = row[3][1:]
                    tn_nature = 'Income'
                else:
                    amount = row[2][1:]
                    tn_nature = 'Expense'

                # Extract transaction type (FAST/PAYNOW etc.)
                query = "SELECT desc FROM dbs WHERE code = ?"
                cursor.execute(query, (tn_code,))
                tn_type = cursor.fetchone()[0]
                        
                # Categorising based on Pattern Extraction
                if tn_code == 'INT':
                    note = 'Interest Earned'
                    category = 'Interest'
                    newRow = [date, note, amount, category, tn_nature]

                    writer.writerow(newRow)
                    print(f'Row{i} done')
                    i += 1
                    continue
                
                    
                found = False
                if row[1] in ['MST', 'UPI', 'UMC', 'UMC-S']:
                    references = [x for x in references if not re.search(r'\d{4}-\d{4}-\d{4}-\d{4}', x)]
                    if ' SI NG ' in reference: # review this it can also be SI SGP
                        reference = reference[:-12]
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

                newRow = [date, note, amount, category, tn_nature]


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
    #tn_nature, tn_type, tn_ref = tn_data


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


