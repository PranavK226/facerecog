from crypt import methods
import face_recognition
import cv2
from face_recognition.api import face_encodings
import pyrebase
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/fetchData")
def dataTest():
    return {"members": ["Hello", "This Works", "Do better stuff man"]}

@app.route('/personData', methods=['POST', 'GET'])
def personData():
    f = request.files['file']
    f.save("./Subject.jpg")
    person_json = {"Img":"Subject.jpg", "Path":"./Subject.jpg"}
    return findPerson(person_json)

@app.route('/missingPeople', methods=['POST', 'GET'])
def missingPeople():
    config = {
    "apiKey": "AIzaSyBOkIXeckED7TmUTpaLW23BYuVtWIanQyY",
    "authDomain": "face-recognition-c1e84.firebaseapp.com",
    "databaseURL": "https://face-recognition-c1e84-default-rtdb.firebaseio.com",
    "projectId": "face-recognition-c1e84",
    "storageBucket": "face-recognition-c1e84.appspot.com",
    "messagingSenderId": "225780171266",
    "appId": "1:225780171266:web:b63f0946a7ee9732eedd1b",
    "measurementId": "G-VVWZECG12S"
    }

    fb = pyrebase.initialize_app(config)

    storage = fb.storage()
    db = fb.database()

    requestData = request.get_json()
    print(requestData)
    path = requestData.replace(" ", "") + ".jpg"
    storage.child(path).put("./Subject.jpg")
    db.child("People").child(requestData).update({"Name":requestData, "Img":path})

    return jsonify("All Good")
    

def findPerson(personData_json):
    config = {
    "apiKey": "AIzaSyBOkIXeckED7TmUTpaLW23BYuVtWIanQyY",
    "authDomain": "face-recognition-c1e84.firebaseapp.com",
    "databaseURL": "https://face-recognition-c1e84-default-rtdb.firebaseio.com",
    "projectId": "face-recognition-c1e84",
    "storageBucket": "face-recognition-c1e84.appspot.com",
    "messagingSenderId": "225780171266",
    "appId": "1:225780171266:web:b63f0946a7ee9732eedd1b",
    "measurementId": "G-VVWZECG12S"
    }

    fb = pyrebase.initialize_app(config)

    storage = fb.storage()
    db = fb.database()

    path = personData_json['Path'] #input("Please input path to subject image: ")
    img_name = personData_json['Img'] #input("Please input just the name of the subjects' image: Ex: ElonMusk.jpg ")

    img = cv2.imread(path)
    img = cv2.resize(img, (400, int(400*img.shape[0]/img.shape[1])))
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodedimg = face_recognition.face_encodings(rgb_img)[0]


    people = db.child("People").get()

    for person in people.each():
        person_img = person.val()['Img']
        storage.child(person_img).download("", person_img)

    found = False

    for person in people.each(): #for each person, figure out their name and get their image
        person_val = person.val()
        print(person_val)

        person_img = person_val['Img']
        person_name = person_val['Name']

        new_path = "./" + person_img
        new_img = cv2.imread(new_path)
        new_rgb_img = cv2.cvtColor(new_img, cv2.COLOR_BGR2RGB)
        new_encodedimg = face_recognition.face_encodings(new_rgb_img)[0]

        if face_recognition.compare_faces([new_encodedimg], encodedimg)[0]: #if its a match, then say who the person is and box their face
            print(person_name)
            found = True
            break
    if found:
        return jsonify({"Name":person_name, "Found":True})
    else:
        return jsonify({"Found":False})


    '''if not found_person: #if we do not find the persson, record their name in the database and upload their image
        new_data = {'Name':subject, "Img":img_name}
        db.child("People").child(subject).update(new_data)
        storage.child(img_name).put(path)
        data = {"Name":person_name, "Img":person_img, "Found": True}
        return False, "Please enter data"'''

if __name__ == "__main__":
    app.run(debug=True)