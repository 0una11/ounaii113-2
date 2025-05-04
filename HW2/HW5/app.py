from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import pandas as pd
import os
import threading
from werkzeug.utils import secure_filename
from language_analysis import generate_language_report

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
socketio = SocketIO(app, async_mode='threading')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        socketio.emit('update', {'message': '🟢 問卷上傳成功，開始分析中...'})
        threading.Thread(target=background_task, args=(file_path,)).start()
        return 'File uploaded and processing started.', 200

def background_task(file_path):
    try:
        df = pd.read_csv(file_path)
        result = generate_language_report(df)

        socketio.emit('plot_generated', {'plot_url': '/' + result['plot_path']})

        group_summary = f"📊 團體平均動機分數：{result['motivation_avg']:.2f}，焦慮分數：{result['anxiety_avg']:.2f}"
        socketio.emit('update', {'message': group_summary})

        for student in result['individual_feedback']:
            text = f"👤 {student['name']}（{student['subject']}）\n動機分數：{student['motivation']}；焦慮分數：{student['anxiety']}\n建議：{student['suggestions']}"
            socketio.emit('student_advice', {'message': text})

    except Exception as e:
        socketio.emit('update', {'message': f"❌ 分析錯誤：{str(e)}"})

if __name__ == '__main__':
    socketio.run(app, debug=True)
