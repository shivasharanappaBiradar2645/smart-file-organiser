from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from flask_cors import CORS

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
            "last_access": self.last_access.isoformat()
        }


with app.app_context():
    db.create_all()


@app.route('/upload', methods=['POST'])
def upload_file_metadata():
    data = request.json

    required_fields = {"device_id", "username", "name", "path", "size", "hash", "category", "last_access"}
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    
    existing_file = FileMetadata.query.filter_by(hash=data["hash"]).first()
    if existing_file:
        return jsonify({"message": "File already exists", "file": existing_file.to_dict()}), 409

    
    new_file = FileMetadata(
        device_id=data["device_id"],
        username=data["username"],
        name=data["name"],
        path=data["path"],
        size=data["size"],
        hash=data["hash"],
        category=data["category"],
        last_access=datetime.fromisoformat(data["last_access"])
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
