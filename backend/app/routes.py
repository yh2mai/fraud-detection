from flask import Blueprint, request, jsonify
from kafka import KafkaProducer, KafkaConsumer
import json
import uuid
import threading

api = Blueprint("api", __name__)

# Kafka setup
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
consumer = KafkaConsumer(
    'response_topic',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id="rest-api-group"
)

results_store = {}  # Temporary storage for results

@api.route('/predict', methods=['POST'])
def predict():
    transaction = request.json
    correlation_id = str(uuid.uuid4())

    # Send transaction to Kafka
    result=producer.send('raw_transactions', value={
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
        results_store[correlation_id] = response["result"]


# Start Kafka consumer thread
threading.Thread(target=consume_kafka_responses, daemon=True).start()
