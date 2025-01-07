import tensorflow as tf
import numpy as np
from flask import request, jsonify
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
from flask import Blueprint, request, jsonify

tf.config.run_functions_eagerly(True)

# Blueprint for fine-tuning
finetune_bp = Blueprint("finetune", __name__)

# Path to the saved model
MODEL_PATH = "classification_model.h5"

# Load the TensorFlow model
def load_tf_model():
    try:
        model = load_model(MODEL_PATH)
        return model
    except Exception as e:
        raise RuntimeError(f"Failed to load TensorFlow model: {e}")

# Fine-tune the TensorFlow model
def fine_tune_model(model, features, labels):
    try:
        # Convert features and labels to numpy arrays
        features = np.array(features, dtype=np.float32)
        labels = np.array(labels, dtype=np.float32)

        # Normalize the features
        scaler = StandardScaler()
        features = scaler.fit_transform(features)

        # Ensure labels are 2D
        if labels.ndim == 1:
            labels = np.expand_dims(labels, axis=-1)

        # Recompile the model with a new optimizer
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss=tf.keras.losses.BinaryCrossentropy(),
            metrics=['accuracy']
        )

        # Fine-tune the model
        model.fit(features, labels, epochs=5, batch_size=32, verbose=1)

        # Save the fine-tuned model
        model.save(MODEL_PATH)
        return MODEL_PATH
    except Exception as e:
        raise RuntimeError(f"Failed to fine-tune model: {e}")


# API endpoint for fine-tuning
@finetune_bp.route("/fine-tune", methods=["POST"])
def fine_tune():
    try:
        # Parse request data
        data = request.get_json()
        features = data.get('features', [])
        labels = data.get('labels', [])

        if not features or not labels:
            return jsonify({"error": "Features and labels are required"}), 400

        # Load the model
        model = load_tf_model()

        # Fine-tune the model
        updated_model_path = fine_tune_model(model, features, labels)

        return jsonify({"message": "Model fine-tuned successfully", "model_path": updated_model_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
