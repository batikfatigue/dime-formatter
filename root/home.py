import flask
from flask import Flask, request, render_template, send_file
from io import TextIOWrapper
import track

app = Flask(__name__)

@app.route('/submit')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        uploaded_file = request.files.get('fileInput')
        
        if uploaded_file is None:
            return 
        
        text_stream = TextIOWrapper(uploaded_file, encoding="utf-8")
        track.tracker(text_stream)

        return render_template('download.html')
    
    else:
        return render_template('index.html')
    
@app.route('/download')
def download():
    file_path = 'import.csv'
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run()