from flask import Flask, request, render_template, jsonify
import joblib
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import class_lablel

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx'}

# Load the trained model
model = joblib.load("model/best_model.pkl")

# Enhanced label mapping with colors and icons



def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                with open(filepath, 'r', encoding='utf-8') as f:
                    news = f.read()
                os.remove(filepath)  # Clean up after processing
            else:
                return render_template("index.html", error="Invalid file type")
        else:
            news = request.form["news"]

        prediction = model.predict([news])[0]
        result = class_lablel.label_mapping.get(prediction,
                                   {"name": f"Unknown category ({prediction})", "color": "#6c757d", "icon": "question"})
        return jsonify({
            "topic": result["name"],
            "color": result["color"],
            "icon": result["icon"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)