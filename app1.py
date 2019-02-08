import re
import string
import random
import datetime

from flask_dropzone import Dropzone
from flask import Flask, render_template, request, jsonify , session, url_for, redirect

import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db

app = Flask(__name__)
dropzone = Dropzone(app)
cred = credentials.Certificate("credentials.json")

app.config['SECRET_KEY'] = 'heorohania'
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['DROPZONE_REDIRECT_VIEW'] = 'display'
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_PARALLEL_UPLOADS'] = 2 

firebase_admin.initialize_app(cred, {
    
                'databaseURL': 'https://ionicdb-a7f9e.firebaseio.com',
            })

app1 = firebase_admin.initialize_app(cred, {
    
                'storageBucket': 'ionicdb-a7f9e.appspot.com',
            }, name='storage')


bucket = storage.bucket(app=app1)


def page_acceuil():
    return render_template('index.html')

def test_db():
    ref = db.reference('presentation')
    

    for key, val in (ref.get()).items() :
        if (val['phone']):
            bblp = bucket.blob(""+val['url'])
            bblp.make_public()
            url = bblp.public_url

            users_ref = ref.child(key)

            users_ref.update({
                'url': url,
                'phone':False,
                
            })
        else:

            users_ref = ref.child(key)

            users_ref.update({
                'status':False,
                
            })
          

    return render_template('display2.html',file_urls=ref.get())

def page_upload():


    if "file_urls" not in session:
        session['file_urls'] = []
    # list to hold our uploaded image urls
    file_urls = session['file_urls']

    if request.method == 'POST':
         for key, f in request.files.items():

             if key.startswith('file'):

                 img_name = 'presentation/' +f.filename
                 blob = bucket.blob(img_name)
                 blob.upload_from_file(
                        f,
                        content_type='image/jpg'
                    )
                 blob.make_public()
                 file_urls.append(img_name)
                
         session['file_urls'] = file_urls
         return "Uploading ..."

    return render_template('upload1.html')


def page_display():

    if "file_urls" not in session or session['file_urls'] == []:
        return redirect(url_for('upload'))
        
    # # set the file_urls and remove the session variable
    file_urls = list(map(get_url, session['file_urls'])) 
    session.pop('file_urls', None)
    return render_template('services.html', file_urls=file_urls)


def predict(vec):

    modelCu = pickle.load(open("models/modelCu.pkl", "rb"))
    modelZn = pickle.load(open("models/modelZn.pkl", "rb"))
    modelPb = pickle.load(open("models/modelZn.pkl", "rb"))


    cu = modelCu.predict(vec)
    zn = modelZn.predict(vec)
    pb = modelPb.predict(vec)

    doc = {
        "zn":cu,
        "pb":zn,
        "cu":pb,
        }
    
    return  jsonify(doc)


# routes app
app.add_url_rule('/', 'index', page_acceuil, methods=['GET'])
app.add_url_rule('/responsable', 'test_db', test_db, methods=['GET'])
app.add_url_rule('/upload', 'upload', page_upload, methods=['GET', 'POST'])
app.add_url_rule('/display', 'display', page_display, methods=['GET'])

app.add_url_rule('/api/get/<name>', 'test', test, methods=['GET'])

if __name__ == "__main__":
    app.run(debug=True)
