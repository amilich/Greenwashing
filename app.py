import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug import secure_filename
from PIL import Image
import sys
import pyocr
import pyocr.builders

app = Flask(__name__)
app.secret_key = 'xbf\xcb7\x0bv\xcf\xc0N\xe1\x86\x98g9\xfei\xdc\xab\xc6\x05\xff%\xd3\xdf'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
current_file = "no_name"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename.replace(" ",""))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        session['file_name'] = str(file).replace(" ","")
        print session['file_name']
        return render_template("success.html")
    return render_template("fail.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route('/wash')
def wash_file():
    session_str = session['file_name']
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)
    tool = tools[0]
    print("Will use tool '%s'" % (tool.get_name()))
    langs = tool.get_available_languages()
    lang = langs[0]
    my_path = session_str.split("\'")[1].split("\'")[0]
    print my_path
    txt = tool.image_to_string(
        Image.open("uploads/" + my_path),
        lang=lang,
        builder=pyocr.builders.TextBuilder()
    )
    session['product_text'] = txt

    return txt


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
