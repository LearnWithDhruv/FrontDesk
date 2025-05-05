from flask import Flask, render_template, request, redirect, url_for
from db import get_pending_requests, update_help_request, get_learned_answers
from firebase_init import db
import os
from dotenv import load_dotenv
import logging
import flask_socketio
from flask_socketio import SocketIO
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
socketio = SocketIO(app, cors_allowed_origins="*")

# Real-time updates
def firebase_listener():
    def callback(col_snapshot, changes, read_time):
        for change in changes:
            if change.type.name == 'ADDED':
                socketio.emit('new_request', change.document.to_dict())
            elif change.type.name == 'MODIFIED':
                socketio.emit('update_request', change.document.to_dict())

    db.collection("help_requests").on_snapshot(callback)

@app.route("/")
def index():
    return redirect(url_for("pending_requests"))

@app.route("/requests")
def pending_requests():
    requests = get_pending_requests()
    return render_template("requests.html", requests=requests)

@app.route("/respond/<request_id>", methods=["POST"])
def respond(request_id):
    answer = request.form.get("answer")
    if not answer:
        return "Answer is required", 400
    
    update_help_request(request_id, answer)
    socketio.emit('refresh')
    return redirect(url_for("pending_requests"))

@app.route("/history")
def request_history():
    requests = db.collection("help_requests")\
        .order_by("created_at", direction="DESCENDING")\
        .stream()
    return render_template("history.html", 
                         requests=[{"id": doc.id, **doc.to_dict()} for doc in requests])

@app.route("/learned")
def learned_answers():
    return render_template("learned.html", answers=get_learned_answers())

@socketio.on('connect')
def handle_connect():
    logging.info('Client connected')

if __name__ == "__main__":
    firebase_listener()  # Start real-time listener
    socketio.run(app, debug=True)