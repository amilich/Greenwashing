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
    try: 
        session_str = session['file_name']
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            print("No OCR tool found")
            sys.exit(1)
        tool = tools[0]
        langs = tool.get_available_languages()
        lang = langs[0]
        my_path = session_str.split("\'")[1].split("\'")[0]
        txt = tool.image_to_string(
            Image.open("uploads/" + my_path),
            lang=lang,
            builder=pyocr.builders.TextBuilder()
        )
        session['product_text'] = txt
        reasons = []
        if ('natural') in txt.lower(): 
            reasons.append("The term 'natural' is vague and unregulated. You should do more research.")
        if ('pure') in txt.lower(): 
            reasons.append("The term 'pure' is vague and unregulated. You should do more research.")
        if ('healthful') in txt.lower(): 
            reasons.append("The term 'healthful' is vague and unregulated. You should do more research.")
        if ('simple') in txt.lower(): 
            reasons.append("The term 'simple' is vague and unregulated. You should do more research.")
        if ('cfc') in txt.lower(): 
            reasons.append("CFC free is an irrelevant term. CFCs are illegal.")
        if ('better') in txt.lower(): 
            reasons.append("The word 'better' is extremely vague. Be careful.")
        if ('earth') in txt.lower(): 
            reasons.append("Be wary of excessively green packaging and unclear claims. Does this protect the Earth?")
        if ('plant') in txt.lower() and 'plastic' in txt.lower(): 
            reasons.append("This is still a lot of plastic. It is clearly the lesser of two evils - it may be better to skip this.")
    
        degree = "not"
        if len(reasons) > 3:
            degree = "very" 
        elif len(reasons) > 0: 
            degree = "fairly"
        try: 
            print str(reasons) 
            print str(txt)
        except: 
            print 'printing failed' # ... 
        return render_template('gw.html', greenwash_degree = degree, reasons=reasons, img_src="uploads/" + my_path)
    except: 
        return "Error occurred. Please return home."


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.debug = False
    app.run(host='0.0.0.0', port=port)
