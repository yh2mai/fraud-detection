import os
import numpy as np
import onnx
import onnxruntime as ort
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from flask import Blueprint, request, jsonify
import tf2onnx

# Blueprint for fine-tuning
finetune_bp = Blueprint("finetune", __name__)

# Environment variable for model path
ONNX_MODEL_PATH = os.getenv("ONNX_MODEL_PATH", "model.onnx")

# Load ONNX model with ONNX Runtime
def load_onnx_model_with_runtime():
    try:
        session = ort.InferenceSession(ONNX_MODEL_PATH)
        return session
    except Exception as e:
        raise RuntimeError(f"Failed to load ONNX model with ONNX Runtime: {e}")

# Reconstruct TensorFlow model manually
def reconstruct_tf_model(onnx_model_path):
    try:
        # Load ONNX model
        onnx_model = onnx.load(onnx_model_path)

        # Analyze the model graph to rebuild it in TensorFlow
        # For simplicity, assume the model is a sequential-like structure
        layers = []
        for node in onnx_model.graph.node:
            # Example: Translate ONNX nodes to equivalent TensorFlow layers
            if node.op_type == "Relu":
                layers.append(tf.keras.layers.ReLU())
            elif node.op_type == "Dense":
                layers.append(tf.keras.layers.Dense(node.attribute[0].i))  # Extract dimensions

        # Build the TensorFlow model
        tf_model = tf.keras.Sequential(layers)

        return tf_model
    except Exception as e:
        raise RuntimeError(f"Failed to reconstruct TensorFlow model: {e}")

# Fine-tune the TensorFlow model
def fine_tune_model(tf_model, new_data, new_labels, output_path=ONNX_MODEL_PATH):
    try:
        # Determine the number of classes
        num_classes = len(np.unique(new_labels))

        # One-hot encode labels
        from tensorflow.keras.utils import to_categorical
        new_labels_one_hot = to_categorical(new_labels, num_classes=num_classes)

        # Initialize all layers by calling the model with dummy data
        dummy_input = np.random.random((1,) + new_data.shape[1:]).astype(np.float32)
        tf_model(dummy_input)

        # Update the model's output layer if needed
        if tf_model.layers[-1].output_shape[-1] != num_classes:
            from tensorflow.keras.layers import Dense
            from tensorflow.keras.models import Model
            
            x = tf_model.layers[-2].output  # Get the second-to-last layer
            output = Dense(num_classes, activation="softmax")(x)
            tf_model = Model(inputs=tf_model.input, outputs=output)

            # Recompile the model
            tf_model.compile(optimizer=Adam(), loss="categorical_crossentropy", metrics=["accuracy"])

        # Fine-tune the model
        tf_model.fit(new_data, new_labels_one_hot, epochs=5, batch_size=32)

        # Export fine-tuned model back to ONNX
        spec = (tf.TensorSpec((None,) + new_data.shape[1:], tf.float32),)
        tf2onnx.convert.from_keras(tf_model, input_signature=spec, output_path=output_path)

        return output_path
    except Exception as e:
        raise RuntimeError(f"Failed to fine-tune model: {e}")



# API endpoint for fine-tuning
@finetune_bp.route("/fine-tune", methods=["POST"])
def fine_tune():
    try:
        # Parse request data
        data = request.get_json()
        new_data = np.array(data.get("features", []))
        new_labels = np.array(data.get("labels", []))

        if new_data.size == 0 or new_labels.size == 0:
            return jsonify({"error": "Invalid input data"}), 400

        # Load ONNX model using ONNX Runtime
        load_onnx_model_with_runtime()

        # Reconstruct TensorFlow model manually
        tf_model = reconstruct_tf_model(ONNX_MODEL_PATH)

        # Fine-tune the model
        updated_model_path = fine_tune_model(tf_model, new_data, new_labels)

        return jsonify({"message": "Model fine-tuned successfully", "model_path": updated_model_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
