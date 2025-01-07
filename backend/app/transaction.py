# transaction.py

from kafka import KafkaConsumer, KafkaProducer
import os
from dotenv import load_dotenv
import json
import requests
from threading import Thread

# Load environment variables
load_dotenv(dotenv_path=f".env.{os.getenv('ENV', 'dev')}")
kafka_service=os.environ.get("KAFKA_SERVICE", "localhost:9092")

# Kafka consumer setup
consumer = KafkaConsumer(
'raw_transactions',
bootstrap_servers=kafka_service,
value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Kafka producer for response
producer = KafkaProducer(
bootstrap_servers=kafka_service,
value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


onnx_api_service_url = os.environ.get("ML_API_SERVICE", "http://localhost:5000")

def process_transactions():
    for message in consumer:
        data = message.value
        transaction = data["transaction"]
        correlation_id = data["correlation_id"]
        response_topic = data["response_topic"]

        print ('raw_transactions: correlation_id ' + correlation_id)

        # Construct the full URL for the /predict endpoint
        predict_url = f"{onnx_api_service_url}/predict"

        # Call ONNX Runtime REST API for prediction
        response = requests.post(
            predict_url,
            json={"inputs": transaction['transaction']}
        )
        prediction = response.json()["outputs"]

        print (prediction[0][0])
        # Prepare and send the response message
        response_message = {
            "correlation_id": correlation_id,
            "transaction_id": transaction["id"],
            "result": prediction[0]
        }
        producer.send(response_topic, value=response_message)

# Start a background thread for Kafka consumer
def start_transaction_processor():
    thread = Thread(target=process_transactions)
    thread.daemon = True  # Ensures it stops when the main program exits
    thread.start()
