import os
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='template')

ALLOWED_EXTS = {"wav", "mp3"}


def check_file(file):
    return '.' in file and file.rsplit('.', 1)[1].lower() in ALLOWED_EXTS



@app.route("/", methods=["GET", "POST"])
def web():
    error = None
    filename = None
    if request.method == 'POST':
        if 'file' not in request.files:
            error = "file not selected"
            return render_template("index.html", error=error)

        file = request.files['file']
        filename = file.filename

        if ".mp3" in filename:
            filename = filename.split(".")[0]
            filename += ".wav"

        if filename == '':
            error = "File name is empty"
            return render_template("index.html", error=error)
        if not check_file(filename):
            error = "Upload only mp3 or wav files"
            return render_template("index.html", error=error)
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        file.save(os.path.join(ROOT_DIR, filename))
    return render_template("index.html", filename=filename)


if __name__ == "__main__":
    app.run()