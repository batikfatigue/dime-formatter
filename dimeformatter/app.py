from flask import Flask, request, render_template, send_file, session
from io import TextIOWrapper
from helper import formatter_dbs, validate_csv
import sqlite3

app = Flask(__name__)
# app.secret_key = 'your-secret-key'

# To display all transaction codes
def tn_codes():
    conn = sqlite3.connect('dimeformatter/dbs.db')  # Create SQLite database file
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dbs')
    # Get column names
    columns = [description[0] for description in cursor.description]

    # Fetch all rows
    rows = cursor.fetchall()

    # Print column headers
    print('\t'.join(columns))

    # Print each row
    for row in rows:
        print('\t'.join(str(cell) for cell in row))

    # Close connection
    conn.close()
 
#tn_codes()

@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        # Assume valid file input
        categories = request.form.getlist('categories')
        uploaded_file = request.files.get('fileInput')
        
        is_valid, message = validate_csv(uploaded_file)
        if not is_valid:
            return render_template('file.html', error=message, categories=categories)
        
        
        text_stream = TextIOWrapper(uploaded_file, encoding="utf-8")
        formatter_dbs(text_stream, categories)

        return render_template('download.html')
    else:
        return render_template('index.html')

    
@app.route('/categoriser', methods=['GET', 'POST'])
def category():
    if request.method == 'POST':
        categories = request.form.getlist('categories') 

        # categoriser(categories, reference)
        # this function will return the category from a prompt

        return render_template('file.html', categories=categories)
    else:
        return render_template('category.html')

@app.route('/download')
def download():
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # print(script_dir)
    file_path = 'import.csv'
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run()