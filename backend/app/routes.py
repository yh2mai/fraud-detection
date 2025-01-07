from flask import Blueprint, request, jsonify
from kafka import KafkaProducer, KafkaConsumer
import os
from dotenv import load_dotenv
import json
import uuid
import threading
from flask_cors import CORS

api = Blueprint("api", __name__)

CORS(api) 

# Load environment variables
load_dotenv(dotenv_path=f".env.{os.getenv('ENV', 'dev')}")
kafka_service=os.environ.get("KAFKA_SERVICE", "localhost:9092")

# Kafka setup
producer = KafkaProducer(
    bootstrap_servers=kafka_service,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
consumer = KafkaConsumer(
    'response_topic',
    bootstrap_servers=kafka_service,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

results_store = {}  # Temporary storage for results

@api.route('/predict', methods=['POST'])
def predict():
    transaction = request.json
    correlation_id = str(uuid.uuid4())
    
    # Send transaction to Kafka
    producer.send('raw_transactions', value={
        "transaction": transaction,
        "correlation_id": correlation_id,
        "response_topic": "response_topic"
    })
    
    # Respond immediately with the correlation ID
    return jsonify({"correlation_id": correlation_id}), 202

@api.route('/result/<correlation_id>', methods=['GET'])
def get_result(correlation_id):
    # Check if the result is available
    result = results_store.get(correlation_id)
    if result:
        return jsonify(result)
    else:
        return jsonify({"status": "processing"}), 202
    

# Background thread to consume Kafka responses
def consume_kafka_responses():
    for message in consumer:
        response = message.value
        correlation_id = response["correlation_id"]
        print ('response_topic consumer ')
        results_store[correlation_id] = response["result"]


# Start Kafka consumer thread
threading.Thread(target=consume_kafka_responses, daemon=True).start()
