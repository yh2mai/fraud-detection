import React, { useState } from 'react';
import axios from 'axios';

const FeedNewData = () => {
    const [inputs, setInputs] = useState(Array(30).fill(0.0)); // 30 input features
    const [result, setResult] = useState(0.0); // Float result label
    const [responseMessage, setResponseMessage] = useState('');
    const [loading, setLoading] = useState(false);

    // Handle input change for features
    const handleInputChange = (index, value) => {
        const newInputs = [...inputs];
        newInputs[index] = value;
        setInputs(newInputs);
    };

    // Handle result label change
    const handleResultChange = value => {
        setResult(parseFloat(value));
    };

    // Submit new data to the model
    const handleFeedData = () => {
        setLoading(true);
        axios.post('http://localhost:5000/fine-tune', { features: [inputs], labels:[result] })
            .then(response => {
                setResponseMessage(response.data.message);
                setLoading(false);
            })
            .catch(err => {
                console.error('Error feeding new data:', err);
                setResponseMessage('An error occurred while feeding new data.');
                setLoading(false);
            });
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>Feed New Data to the Model</h1>
            <form
                onSubmit={e => {
                    e.preventDefault();
                    handleFeedData();
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
                <div style={{ gridColumn: 'span 5', marginBottom: '10px' }}>
                    <label>Result Label</label>
                    <input
                        type="number"
                        value={result}
                        onChange={e => handleResultChange(e.target.value)}
                        style={{ width: '100%' }}
                    />
                </div>
                <button
                    type="submit"
                    style={{
                        gridColumn: 'span 5',
                        padding: '10px',
                        fontSize: '16px',
                        cursor: 'pointer',
                        backgroundColor: '#28a745',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '5px',
                    }}
                    disabled={loading}
                >
                    {loading ? 'Submitting...' : 'Feed Data'}
                </button>
            </form>
            {responseMessage && (
                <div style={{ marginTop: '20px', padding: '10px', border: '1px solid #ccc', borderRadius: '5px' }}>
                    <h3>Response</h3>
                    <p>{responseMessage}</p>
                </div>
            )}
        </div>
    );
};

export default FeedNewData;
