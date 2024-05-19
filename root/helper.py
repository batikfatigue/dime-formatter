def reformatter(text_stream, categories):
    import csv
    import os

    # Gets directory for helper.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Generates the path for import.csv
    csv_path = os.path.join(script_dir, 'import.csv')

    # Clears the import file and writes in the header
    header = ['Date','Note','Amount','Category','Type']
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    with text_stream as file:
        data = csv.reader(file)
        i = 1
        for row in data:
            if row == []:
                continue
            elif row[0][0].isnumeric(): # Check if first item of the row is a date
                # Check debit or credit
                # Index 2 is Expense, 3 is income
                
                date = row[0]
                note = ''
                if row[3] != ' ': 
                    amount = row[3][1:]
                    type1 = 'Income'
                else:
                    amount = row[2][1:]
                    type1 = 'Expense'
                
            
                # this is repeated , maybe can use function
                # if row[1] == 'INT':
                #     note = 'Interest Earned'
                #     category = 'Interest'
                #     newRow = [date, note, amount, type1, category]

 
                #     f = open(csv_path, 'a', newline='')
                #     writer = csv.writer(f)
                #     writer.writerow(newRow)
                #     print(f'Row{i} done for {reference}')
                #     i += 1

                #     continue
                    
                    
                
                # Processing references
                # if nets qr then find the TO: 
                if row[1] == 'MST':
                    reference = row[5]
                else: 
                    reference = row[4:7]
                    dup = [k for k in reference]
                    found = False
                    for j, ref in enumerate(dup):
                        print(ref)
                        if 'PayNow Transfer' in ref:
                            reference.remove(dup[j])

                        if 'OTHR' in ref:
                            ref = ref[5:]
                            misc = categoriser(categories, ref)
                            if 'Miscellaneous' in misc:
                                reference.remove(dup[j])
                            else:
                                category = misc
                                found = True
                                break
                        print(
                            'Checking: {}'.format(reference)
                        )

                print(reference)
                if not found:
                    category = categoriser(categories, reference)
                print(category)

                # we will let the user manually type in categories that chatgpt sort as misc, less they want to sort it as misc

                newRow = [date, note, amount, type1, category]


                f = open(csv_path, 'a', newline='')
                writer = csv.writer(f)
                writer.writerow(newRow)
                print(f'Row{i} done')
                i += 1

# *para: categories will take in a list of preset categories in dime
# returns a category
def categoriser(categories, reference): 
    from openai import OpenAI

    client = OpenAI()

    categories = categories + ['Miscellaneous']
    reference = '[' + ', '.join(map(repr, reference)) + ']'


    # Define the prompt or input text
    # reference = 'iCloud Subscription'

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": """You are an bank transactions analyser.
                                        Categories: {}.
                                        You pick a most suitable category from the above, according to the given transaction references.
                                        You don't look at patterns, you focus on the names/brands.
                                        You resort to Miscellaneous whenever there's little context.
                                        You explain why you chose so, in a short sentence.
                                        
                                        """.format(categories)},

        {"role": "user", "content": reference}
    ]
    )

    category = completion.choices[0].message.content

    return category
