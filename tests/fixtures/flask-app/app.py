import os

from flask import Flask

app = Flask(__name__)
FOLDER_ID = os.environ["EXAMPLE_FOLDER_ID"]


@app.route("/health")
def health():
    return {"status": "ok"}
