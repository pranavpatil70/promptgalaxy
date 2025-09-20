from io import BytesIO
from bson import ObjectId
from flask import Flask, render_template, request, redirect, send_file, session, url_for, jsonify
from pymongo import MongoClient
import gridfs

app = Flask(__name__)
app.secret_key = "pvp@9999"

# Admin credentials
ADMIN_USERNAME = "pranav"
ADMIN_PASSWORD = "pvp@9999"

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://mailpranavpatil_db_user:QjWkuHU7m0fPjHNq@cluster0.ezvgiqa.mongodb.net/")
db = client["Promptgallery"]
fs = gridfs.GridFS(db)
submissions = db["prompts"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
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

    # Example avatar: initials from name
    avatar = ''.join([x[0] for x in name.split()][:2]).upper()

    return jsonify({
        "success": True,
        "image_url": url_for('static', filename='images/your_saved_image.jpg'),  # or your GridFS route
        "title": title,
        "description": description,
        "name": name,
        "avatar": avatar,
        "instagram": instagram,
        "twitter": twitter
    })

@app.route('/success')
def success():
    return "Prompt submitted successfully!"

# Admin Login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return "❌ Invalid Credentials"

    return render_template("admin_login.html")

# Admin Dashboard (Protected)
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    all_submissions = list(submissions.find())
    return render_template("admin_dashboard.html", submissions=all_submissions)

# Image Downloader
@app.route("/admin/download/<file_id>")
def admin_download(file_id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    file = fs.get(ObjectId(file_id))
    return send_file(file, as_attachment=True, download_name=f"{file_id}.png")

# Delete Submission
@app.route("/admin/delete/<prompt_id>", methods=["POST"])
def admin_delete(prompt_id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    prompt = submissions.find_one({"_id": ObjectId(prompt_id)})
    if prompt and prompt.get("image_id"):
        try:
            fs.delete(prompt["image_id"])
        except Exception:
            pass  # Ignore if already deleted or not found
    submissions.delete_one({"_id": ObjectId(prompt_id)})
    return redirect(url_for("admin_dashboard"))

# Logout
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(debug=True)
