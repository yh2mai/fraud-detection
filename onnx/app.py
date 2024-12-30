from flask import Flask, request, jsonify
from flask_cors import CORS
import onnxruntime as ort
import numpy as np
from finetune import finetune_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# Load the ONNX model
model_path = "model.onnx"
session = ort.InferenceSession(model_path)

# Register the Blueprint
app.register_blueprint(finetune_bp)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Parse input data
        data = request.json["inputs"]
        inputs = np.array(data).astype(np.float32)

        # Perform inference
        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: inputs})

        # Return the result
        return jsonify({"outputs": outputs[0].tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
