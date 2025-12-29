from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from src.huffman import compress, decompress
import json
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route("/")
def home():
    return "Huffman Compressor Ready"

@app.route("/compress", methods=["POST"])
def compress_file():
    file = request.files["file"]
    filename = secure_filename(file.filename)
    raw = file.read()

    compressed_bytes, freq = compress(raw)

    out_bin = os.path.join(app.config["UPLOAD_FOLDER"], filename + ".huf")
    out_meta = os.path.join(app.config["UPLOAD_FOLDER"], filename + ".json")

    with open(out_bin, "wb") as f:
        f.write(compressed_bytes)

    with open(out_meta, "w") as f:
        json.dump(freq, f)

    ratio = round((1 - (len(compressed_bytes) / len(raw))) * 100, 2)

    return jsonify({"message": "Compressed", "ratio": f"{ratio}%", 
                    "bin_file": out_bin, "meta_file": out_meta})

@app.route("/decompress", methods=["POST"])
def decompress_file():
    binfile = request.files["bin"]
    metafile = request.files["meta"]

    raw = binfile.read()
    freq = json.load(metafile)

    original = decompress(raw, freq)

    out = os.path.join(app.config["UPLOAD_FOLDER"], binfile.filename.replace(".huf", "_restored"))
    with open(out, "wb") as f:
        f.write(original)

    return jsonify({"message": "Decompressed", "output": out})

if __name__ == "__main__":
    app.run(debug=True)
