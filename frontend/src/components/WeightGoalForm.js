import React, { useState } from 'react';
import { createWeightGoal } from '../services/weightGoalApi';

const WeightGoalForm = ({ onGoalCreated }) => {
  const [formData, setFormData] = useState({
    target_weight: '',
    target_date: '',
    description: ''
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
      setStatus({ type: 'loading', message: '目標を設定中...' });
      
      // 日付形式の検証
      const targetDate = new Date(formData.target_date);
      if (isNaN(targetDate.getTime())) {
        throw new Error('有効な日付を入力してください');
      }
      
      // 現在の日付以降であるかを検証
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (targetDate < today) {
        throw new Error('目標日は今日以降の日付を指定してください');
      }
      
      // 体重の検証
      const targetWeight = parseFloat(formData.target_weight);
      if (isNaN(targetWeight) || targetWeight <= 0) {
        throw new Error('有効な体重を入力してください');
      }
      
      const response = await createWeightGoal({
        target_weight: targetWeight,
        target_date: formData.target_date,
        description: formData.description || undefined
      });
      
      setStatus({ type: 'success', message: '体重目標が設定されました！' });
      
      // フォームをリセット
      setFormData({
        target_weight: '',
        target_date: '',
        description: ''
      });
      
      // 親コンポーネントに通知
      if (onGoalCreated) {
        onGoalCreated(response);
      }
      
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || '目標の設定に失敗しました';
      setStatus({ type: 'error', message: errorMessage });
      console.error('目標設定エラー:', err);
    }
  };

  return (
    <div className="card">
      <h2>体重目標を設定</h2>
      
      {status.message && (
        <div className={`status-message ${status.type}`}>
          {status.message}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="target_weight">目標体重 (kg):</label>
          <input
            type="number"
            step="0.1"
            id="target_weight"
            name="target_weight"
            value={formData.target_weight}
            onChange={handleChange}
            required
            min="20"
            max="300"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="target_date">目標日:</label>
          <input
            type="date"
            id="target_date"
            name="target_date"
            value={formData.target_date}
            onChange={handleChange}
            required
            min={new Date().toISOString().split('T')[0]}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="description">メモ (オプション):</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="3"
          />
        </div>
        
        <button type="submit" className="btn">
          目標を設定
        </button>
      </form>
    </div>
  );
};

export default WeightGoalForm;