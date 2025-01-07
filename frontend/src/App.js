import React, { useState } from 'react';
import FeedNewData from './components/FeedNewData';
import { v4 as uuidv4 } from 'uuid'; // For generating random IDs

const BACKEND_REST_URL=process.env.REACT_APP_BACKEND_URL;

const App = () => {
    const [inputs, setInputs] = useState(Array(30).fill(0.0)); // 30 input features
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);

    // Handle input change
    const handleInputChange = (index, value) => {
        const newInputs = [...inputs];
        newInputs[index] = value;
        setInputs(newInputs);
    };

    // Submit inputs for prediction
    const handlePredict = () => {
        setLoading(true);
        const transactionId = uuidv4(); // Generate a random ID

        fetch(`${BACKEND_REST_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({"transaction":[inputs], "id":transactionId}),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Correlation ID:', data.correlation_id);

                // Poll for result
                const interval = setInterval(() => {
                    fetch(`${BACKEND_REST_URL}/result/${data.correlation_id}`)
                        .then(response => response.json())
                        .then(result => {
                            if (result.status !== 'processing') {
                                clearInterval(interval);
                                setPrediction(result); // Set the prediction result
                                setLoading(false); // Stop loading
                                console.log('Prediction Result:', result);
                            }
                        })
                        .catch(err => {
                            clearInterval(interval);
                            setLoading(false);
                            console.error('Error fetching prediction result:', err);
                        });
                }, 1000); // Poll every second
            })
            .catch(err => {
                setLoading(false);
                console.error('Error submitting prediction:', err);
            });
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>Fraud Detection Prediction</h1>
            <form
                onSubmit={e => {
                    e.preventDefault();
                    handlePredict();
                }}
                style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px' }}
            >
                {inputs.map((input, index) => (
                    <div key={index} style={{ marginBottom: '10px' }}>
                        <label>Feature {index + 1}</label>
                        <input
                            type="number"
                            value={input}
                            onChange={e => handleInputChange(index, e.target.value)}
                            style={{ width: '100%' }}
                        />
                    </div>
                ))}
                <button
                    type="submit"
                    style={{
                        gridColumn: 'span 5',
                        padding: '10px',
                        fontSize: '16px',
                        cursor: 'pointer',
                        backgroundColor: '#007bff',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '5px',
                    }}
                    disabled={loading}
                >
                    {loading ? 'Processing...' : 'Predict'}
                </button>
            </form>
            {prediction && (
                <div style={{ marginTop: '20px', padding: '10px', border: '1px solid #ccc', borderRadius: '5px' }}>
                    <h3>Prediction Result</h3>
                    <pre>{JSON.stringify(prediction, null, 2)}</pre>
                </div>
            )}

        <FeedNewData />
        </div>
    );
};

export default App;
