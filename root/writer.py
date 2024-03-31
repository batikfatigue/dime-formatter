def base(text_stream):
    import csv

    # Clears the import file and writes in the header
    header = ['Date','Note','Amount','Category','Type']
    with open('import.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    with text_stream as file:
        data = csv.reader(file)
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

                category = ''

                if row[1] == 'INT':
                    note = 'Interest Earned'

                newRow = [date, note, amount, type1, category]

                f = open('import.csv', 'a', newline='')
                writer = csv.writer(f)
                writer.writerow(newRow)

# *para: categories will take in a list of preset categories in dime
def categoriser(categories, reference): 
    from openai import OpenAI

    client = OpenAI()

    list_of_categories = categories + ['Miscellaneous']
    categories = '[' + ', '.join(map(repr, list_of_categories)) + ']'

    # Print the result
    print(categories)


    # Define the prompt or input text
    # reference = 'iCloud Subscription'

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": """You are an analyser, being able to choose a category from a prompt for money tracking. Just a single word.
                                        Here are the categories you choose from: {}.""".format(categories)},
        {"role": "user", "content": reference}
    ]
    )

    category = completion.choices[0].message.content

    return category
    
            