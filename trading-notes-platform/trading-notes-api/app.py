from flask import Flask, request, jsonify
from google.cloud import firestore
import os

app = Flask(__name__)

try:
    db = firestore.Client()
except:
    db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))

@app.route('/health')
def health():
    try:
        db.collection('notes').limit(1).get()
        return jsonify({"status":"healthy"})
    except Exception as e:
        return jsonify({"status":"unhealthy","error":str(e)}),503

@app.route('/notes', methods=['GET'])
def get_notes():
    try:
        notes=[]
        docs=db.collection('notes').limit(10).stream()
        for doc in docs:
            notes.append(doc.to_dict())
        return jsonify({"notes":notes})
    except Exception as e:
        return jsonify({"error":str(e)}),500

@app.route('/notes', methods=['POST'])
def create_note():
    try:
        data=request.get_json()
        if not data.get("message"):
            return jsonify({"error":"message required"}),400

        db.collection('notes').add({
            "message":data["message"],
            "timestamp":firestore.SERVER_TIMESTAMP
        })

        return jsonify({"status":"created"}),201
    except Exception as e:
        return jsonify({"error":str(e)}),500

if __name__ == "__main__":
    port=int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0",port=port)
