from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import tensorflow as tf
from finetune import finetune_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# Load the TensorFlow model
model_path = "classification_model.h5"  # Replace with the actual path to your saved model
try:
    model = tf.keras.models.load_model(model_path)
except Exception as e:
    raise RuntimeError(f"Failed to load TensorFlow model: {e}")

# Register the Blueprint
app.register_blueprint(finetune_bp)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Parse input data
        data = request.json["inputs"]
        inputs = np.array(data).astype(np.float32)

        # Perform inference
        outputs = model.predict(inputs)

        # Return the result
        return jsonify({"outputs": outputs.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
