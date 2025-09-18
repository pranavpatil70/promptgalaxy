from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
import gridfs

app = Flask(__name__)

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://mailpranavpatil_db_user:QjWkuHU7m0fPjHNq@cluster0.ezvgiqa.mongodb.net/")
db = client["Promptgallery"]
fs = gridfs.GridFS(db)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    print("Hey this function is just working fine")
    name = request.form.get('name')
    email = request.form.get('email')
    title = request.form.get('title')
    description = request.form.get('description')
    instagram = request.form.get('instagram')
    twitter = request.form.get('twitter')

    # handle image
    image_file = request.files['image']
    image_id = None
    if image_file and image_file.filename != "":
        image_id = fs.put(image_file, filename=image_file.filename)

    # insert into MongoDB
    db.prompts.insert_one({
        "name": name,
        "email": email,
        "title": title,
        "description": description,
        "instagram": instagram,
        "twitter": twitter,
        "image_id": image_id
    })

    return redirect('/success')

@app.route('/success')
def success():
    return "Prompt submitted successfully!"

if __name__ == "__main__":
    app.run(debug=True)
