from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from flask_cors import CORS
from imagehash import hex_to_hash
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


EXTENSION_MAP = {
    'documents': ['.pdf', '.docx', '.txt'],
    'images': ['.jpg', '.jpeg', '.png'],
    'videos': ['.mp4', '.mov', '.avi'],
    'audio': ['.mp3', '.wav'],
    'archives': ['.zip', '.tar', '.rar'],
    'others': []
}

class ImagesData(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    device_id = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(512), unique=True, nullable=False)
    data = db.Column(db.String())

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "username": self.username,
            "name": self.name,
            "path": self.path,
            "data": self.data
        }






class FileMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(512), unique=True, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    hash = db.Column(db.String(64), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    last_access = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sync = db.Column(db.Boolean,default=False)
    archive = db.Column(db.Boolean,default=False)

    def to_dict(self):
        return {
            "id":self.id,
            "device_id": self.device_id,
            "username": self.username,
            "name": self.name,
            "path": self.path,
            "size": self.size,
            "hash": self.hash,
            "category": self.category,
            "last_access": self.last_access.isoformat(),
            "sync":self.sync,
            "archive":self.archive
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    device_id = db.Column(db.String(50), nullable=False)
    clean_on_scan = db.Column(db.Boolean, default=False)  # Option for automatic cleaning
    total_cleaned_size = db.Column(db.Integer, default=0)  # Total data cleaned (bytes)
    total_files_scanned = db.Column(db.Integer, default=0)  # Total files scanned


    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "device_id": self.device_id,
            "clean_on_scan": self.clean_on_scan,
            "total_cleaned_size": self.total_cleaned_size,
            "total_files_scanned": self.total_files_scanned
        }

class TaskQueue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # "sync" or "archive"
    path = db.Column(db.String(512), nullable=False)
    status = db.Column(db.String(20), default="pending")  # "pending", "in_progress", "done"


with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="pranav").first():
        user1 = User(username="pranav", device_id="device_001", clean_on_scan=True, total_cleaned_size=0, total_files_scanned=0)
        db.session.add(user1)

    if not User.query.filter_by(username="shiv").first():
        user2 = User(username="shiv", device_id="device_002", clean_on_scan=True, total_cleaned_size=0, total_files_scanned=0)
        db.session.add(user2)
    db.session.commit()





@app.route('/task', methods=['POST'])
def add_task():
    data = request.json
    required_fields = {"device_id", "username", "action", "path"}
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    if data["action"] not in ["sync","unsync","unarchive", "archive"]:
        return jsonify({"error": "Invalid action"}), 400
    
    existing_file = FileMetadata.query.filter_by(path=data["path"]).first()
    if not existing_file:
        return jsonify({"error": "Invalid path"}), 400
    
    if data["action"] =="sync" :
        existing_file.sync = True
    else: 
        existing_file.archive = True

    task = TaskQueue(**data)
    db.session.add(task)
    
    
    db.session.commit()

    return jsonify({"message": "Task added", "task": task.id}), 201

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = TaskQueue.query.filter_by(status="pending").all()
    return jsonify([{"id": t.id, "device_id": t.device_id, "username": t.username, "action": t.action, "path": t.path} for t in tasks])

@app.route('/task/done/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = TaskQueue.query.get(task_id)
    if task:
        task.status = "done"
        db.session.commit()
        return jsonify({"message": "Task marked as done"})
    return jsonify({"error": "Task not found"}), 404

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/stats/<user>', methods=['GET'])
def get_statistics(user):
   
    category_stats = db.session.query(
        FileMetadata.category, 
        db.func.count(FileMetadata.id), 
        db.func.sum(FileMetadata.size)
    ).group_by(FileMetadata.category).filter_by(username=user).all()

    category_summary = {
        cat: {"count": count, "total_size": total_size or 0} 
        for cat, count, total_size in category_stats
    }

    for category in EXTENSION_MAP.keys():
        if category not in category_summary:
            category_summary[category] = {"count": 0, "total_size": 0}

  
    user_stats = User.query.filter_by(username=user).first()
    

    return jsonify({
        "categories": category_summary,
        "user": user_stats.to_dict()
    })






@app.route('/update_cleaning', methods=['POST'])
def update_cleaning_preference():
    data = request.json

    if "username" not in data or "clean_on_scan" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.filter_by(username=data["username"]).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.clean_on_scan = data["clean_on_scan"]
    db.session.commit()

    return jsonify({"message": "Cleaning preference updated", "user": user.to_dict()})


@app.route('/image/upload', methods=['POST'])
def upload_image_file_metadata():
    data = request.json

    required_fields = {"device_id", "username", "name", "path", "response"}
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    new_file = ImagesData(
        device_id=data["device_id"],
        username=data["username"],
        name=data["name"],
        path=data["path"],
        data=data["response"]
    )

    db.session.add(new_file)
    db.session.commit()

    return jsonify({"message": "photo stored successfully", "file": new_file.to_dict()}), 201

@app.route('/image/search/<data>', methods=['GET'])
def search_images_data(data):
    
    results = ImagesData.query.filter(ImagesData.data.like(f"%{data}%")).all()

    if not results:
        return jsonify({"message": "No matching images found"}), 404

    return jsonify([image.to_dict() for image in results]), 200


@app.route('/upload', methods=['POST'])
def upload_file_metadata():
    data = request.json

    required_fields = {"device_id", "username", "name", "path", "size", "hash", "category", "last_access"}
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400


    existing_file = FileMetadata.query.filter_by(hash=data["hash"]).first()
    us = User.query.filter_by(username=data['username']).first()
    if existing_file:
        if us.clean_on_scan:
            us.total_cleaned_size += data["size"]
            db.session.commit()
        return jsonify({"message": "File already exists", "file": existing_file.to_dict(),"clean":us.clean_on_scan}), 409

    us.total_files_scanned += 1
    new_file = FileMetadata(
        device_id=data["device_id"],
        username=data["username"],
        name=data["name"],
        path=data["path"],
        size=data["size"],
        hash=data["hash"],
        category=data["category"],
        last_access=datetime.fromisoformat(data["last_access"]),
        archive=True if data["category"] == False else False
    )

    db.session.add(new_file)
    db.session.commit()

    return jsonify({"message": "File metadata stored successfully", "file": new_file.to_dict()}), 201




@app.route('/delete', methods=['POST'])
def del_file_metadata():
    data = request.json

    required_fields = {"device_id", "username", "name"}
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    existing_file = FileMetadata.query.filter_by(device_id=data["device_id"], username=data["username"], name=data["name"]).first()
    
    if existing_file:
        db.session.delete(existing_file)
        db.session.commit()
        return jsonify({"message": "File deleted successfully", "file": existing_file.to_dict()}), 200

    return jsonify({"error": "File does not exist"}), 409


@app.route('/mov', methods=['POST'])
def mov_file_metadata():
    data = request.json

    required_fields = {"device_id", "username", "name", "old", "new"}
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    existing_file = FileMetadata.query.filter_by(device_id=data["device_id"], username=data["username"], name=data["name"]).first()
    
    if existing_file:
        if existing_file.path != data["old"]:
            return jsonify({"error": "Old path does not match"}), 400  # Optional validation
        existing_file.path = data["new"]
        db.session.commit()
        return jsonify({"message": "File moved successfully", "file": existing_file.to_dict()}), 200

    return jsonify({"error": "File does not exist"}), 409


@app.route('/acc', methods=['POST'])
def acc_file_metadata():
    data = request.json

    required_fields = {"device_id", "username", "name", "date"}
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    existing_file = FileMetadata.query.filter_by(device_id=data["device_id"], username=data["username"], name=data["name"]).first()
    
    if existing_file:
        existing_file.last_access = datetime.fromisoformat(data["date"])
        db.session.commit()
        return jsonify({"message": "File access updated", "file": existing_file.to_dict()}), 200

    return jsonify({"error": "File does not exist"}), 409


@app.route('/files', methods=['GET'])
def get_files():
    files = FileMetadata.query.all()
    return jsonify([file.to_dict() for file in files])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
