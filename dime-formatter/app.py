from flask import Flask, request, render_template, send_file
from io import TextIOWrapper
from app.helper import reformatter

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        # Assume valid file input
        categories = request.form.getlist('categories')
    
        uploaded_file = request.files.get('fileInput')
        text_stream = TextIOWrapper(uploaded_file, encoding="utf-8")
        reformatter(text_stream, categories)

        return render_template('download.html')
    
    else:
        return render_template('index.html')

    
@app.route('/categoriser', methods=['GET', 'POST'])
def category():
    if request.method == 'POST':
        categories = request.form.getlist('categories') 
        print(categories)

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