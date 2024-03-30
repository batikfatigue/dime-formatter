def tracker(text_stream):
    import csv

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
                if row[3] != ' ': 
                    newRow = [row[0]] + [row[4]] + [row[3][1:]] + [''] + ['Income']
                elif row[2] != ' ':
                    newRow = [row[0]] + [row[4]] + [row[2][1:]] + [''] + ['Expense']

                f = open('import.csv', 'a', newline='')
                writer = csv.writer(f)
                writer.writerow(newRow)
    
            