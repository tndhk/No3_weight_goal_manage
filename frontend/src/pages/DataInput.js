import React, { useState } from 'react';
import { addData } from '../services/api';

const DataInput = () => {
  const [formData, setFormData] = useState({
    name: '',
    value: '',
    category: ''
  });
  const [status, setStatus] = useState({ type: '', message: '' });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setStatus({ type: 'loading', message: 'Submitting data...' });
      await addData(formData);
      setStatus({ type: 'success', message: 'Data added successfully!' });
      // Clear form after successful submission
      setFormData({
        name: '',
        value: '',
        category: ''
      });
    } catch (err) {
      setStatus({ type: 'error', message: 'Failed to add data. Please try again.' });
      console.error('Error adding data:', err);
    }
  };

  return (
    <div>
      <h1>Data Input</h1>
      
      <div className="card">
        <h2>Add New Data</h2>
        
        {status.message && (
          <div className={`status-message ${status.type}`}>
            {status.message}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Name:</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="value">Value:</label>
            <input
              type="number"
              id="value"
              name="value"
              value={formData.value}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="category">Category:</label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              required
            >
              <option value="">Select a category</option>
              <option value="Sales">Sales</option>
              <option value="Marketing">Marketing</option>
              <option value="Finance">Finance</option>
              <option value="Operations">Operations</option>
            </select>
          </div>
          
          <button type="submit" className="btn">
            Add Data
          </button>
        </form>
      </div>
    </div>
  );
};

export default DataInput;