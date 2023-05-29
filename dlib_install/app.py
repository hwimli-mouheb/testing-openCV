from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from werkzeug.utils import secure_filename
import os
import base64
import cv2
from simple_facerec import SimpleFacerec
import cv2
import face_recognition
import shutil
# Initialize Flask app
app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'path/to/upload/folder'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Firebase Admin SDK
cred = credentials.Certificate('smart-door-430d3-firebase-adminsdk-4i0xs-91b268016f.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-firebase-database-url.firebaseio.com'
})
db = firestore.client()
# Helper function to check file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_document_by_id(collection_name, document_id):
    doc_ref = db.collection(collection_name).document(document_id)
    doc = doc_ref.get()

    if doc.exists:
        # Document found, return its data
        return doc.to_dict()
    else:
        # Document not found
        return None
# Define API endpoints
@app.route('/upload', methods=['POST'])
def add_data():
    # Check if file is present in the request
    if 'file' not in request.files:
        return 'No file provided'

    file = request.files['file']
    filename = request.form.get('filename')

    if not filename:
        return 'No filename provided'
    # Save the file to a temporary location
    file_path = './temp_file.png'
    file.save(file_path)

    # Load the image using OpenCV
    image = cv2.imread(file_path)
    #os.remove(file_path)  # Remove the temporary file

    # Check if any face is present in the image
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) == 0:
        return 'No face detected in the provided photo'
    
    # Create the "photos" directory if it doesn't exist
    photos_dir = os.path.join(os.path.dirname(__file__), 'photos')
    os.makedirs(photos_dir, exist_ok=True)
    
    # Generate a unique ID for the Firestore document
    doc_ref = db.collection('users').document()
    doc_ref.set({
        'name': filename
    })
    doc_id = doc_ref.id
    
    try:
        # Copy the file to the destination directory
        shutil.copy2('./temp_file.png', './photos/'+doc_id+'.png')
        return 'File uploaded successfully'
    except Exception as e:
        return f'Error duplicating file: {str(e)}'
    
    

@app.route('/recognize', methods=['POST'])
def recognize_face():
    # Check if file is present in the request
    if 'file' not in request.files:
        return 'No file provided'

    file = request.files['file']
    # Save the file to a temporary location
    file_path = './temp_file.jpg'
    file.save(file_path)

    # Load the image using OpenCV
    image = cv2.imread(file_path)
    #os.remove(file_path)  # Remove the temporary file

    # Check if any face is present in the image
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) == 0:
        return 'No face detected in the provided photo'

    # Encode the face from the provided photo
    face_encodings = face_recognition.face_encodings(image, face_locations)

    # Load the known face encodings and names from the photo directory
    known_face_encodings = []
    known_face_names = []
    photo_dir = os.path.join(os.path.dirname(__file__), 'photos')

    for filename in os.listdir(photo_dir):
        if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
            name = os.path.splitext(filename)[0]
            known_image = face_recognition.load_image_file(os.path.join(photo_dir, filename))
            known_face_encoding = face_recognition.face_encodings(known_image)[0]
            known_face_encodings.append(known_face_encoding)
            known_face_names.append(name)

    # Compare the face encodings from the provided photo with the known face encodings
    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        face_names.append(name)
    result = []
    for face_name in face_names :
        if face_name != "Unknown" :
            document_data = get_document_by_id('users',face_name)
            result.append(document_data)
    # Return the name(s) of the matched person(s)
    return result

if __name__ == '__main__':
    app.run(debug=True)