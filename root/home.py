from flask import Flask, request, render_template, send_file
from io import TextIOWrapper
from writer import base, categoriser

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        uploaded_file = request.files.get('fileInput')
        
        if uploaded_file is None:
            return 
        

        text_stream = TextIOWrapper(uploaded_file, encoding="utf-8")
        base(text_stream)

        return render_template('download.html')
    
    else:
        return render_template('index.html')
    
@app.route('/categoriser', methods=['GET', 'POST'])
def category():
    if request.method == 'POST':
        categories = request.form.getlist('categories')
        categories = [category for category in categories if category != ""]

        print(categories)

        # categoriser(categories, reference)
        # this function will return the category from a prompt

        return render_template('file.html')
    else:
        return render_template('category.html')

@app.route('/download')
def download():
    file_path = 'import.csv'
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run()