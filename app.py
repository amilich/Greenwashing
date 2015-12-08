import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug import secure_filename
from PIL import Image
import sys
import pyocr
import pyocr.builders

"""
    Earthsys 41N Final Project

    Andrew M. 
"""

app = Flask(__name__)
app.secret_key = 'xbf\xcb7\x0bv\xcf\xc0N\xe1\x86\x98g9\xfei\xdc\xab\xc6\x05\xff%\xd3\xdf'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
current_file = "no_name"

# Uploading credit: see http://flask.pocoo.org/docs/0.10/patterns/fileuploads/ for file uploading. 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

"""
    Show homepage 
"""
@app.route('/')
def index():
    return render_template('index.html')

"""
    Upload file, set path to current file used. 
"""
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

"""
    Display the file. 
"""
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

"""
    Determine whether image is greenwashed. 
"""
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
        txt = txt.encode('utf-8').strip()
        session['product_text'] = txt
        reasons = []
        fiji = False 
        huggies = False 
        theInfo = ""
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
            theInfo = "It looks like you're buying a product from <b>Fiji</b>. Did you know: <br><br><li>The plastic used in this bottle was first shipped from Asia and transported again to stores across the world?</li><br><li>Fiji has been sued in the past for making false environmental claims. Be wary of greenwashing.</li><br><li>Fiji has also lied about being a carbon-negative company. In 2007, they emitted over 85,000 tons of CO2.</li><br>"
            # fiji = True 
        if ('plant') in txt.lower() and 'plastic' in txt.lower(): 
            reasons.append("'Plant bottle' still means plastic. This is the lesser of two evils - it may be better to skip a plastic water bottle.")
        if ('gg|e') in txt.lower(): 
            print 'ggie'
            huggies = True 
            theInfo = "It appears you are buying Huggies diapers. Remember, 'pure', and 'natural' are unregulated. Diapers will still end up in landfills. "

        degree = "This appears to not be greenwashed, or we could not read the packaging well enough."
        if len(reasons) > 3:
            degree = "This appears to be very greenwashed." 
        elif len(reasons) > 0: 
            degree = "This appears to be greenwashed."
        print txt

        if ('purity you can taste') in txt.lower(): 
            degree = "This appears to be greenwashed."
            theInfo = "It appears you are buying SmartWater. Remember, this is the lesser of two evils. It is still made in a 70% petroleum plastic bottle and shipped across the world. <br> Also, Coca Cola, the maker of Smart Water, has created the 'Plant Bottle' greenwashing campaign. In reality, all bottles are still approximately 70% petroleum products."
        if ('urelyinspired') in txt.lower(): 
            degree = "This appears to be greenwashed."
            theInfo = "What does purely inspired mean? It is vague and unregulated. Furthermore, be wary of the term \"100% plant based.\""

        try: 
            print str(reasons) 
        except: 
            print 'printing failed' # ... 
        printStuff = False 
        if len(theInfo) > 0: 
            print 'printing info'
            printStuff = True
        return render_template('gw.html', greenwash_degree = degree, reasons=reasons, img_src="uploads/" + my_path, theInfo=theInfo, printStuff=printStuff)
    except Exception, e: 
        return "Error occurred. Please return home. " + str(e)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
