import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchWeightGoals, deleteWeightGoal, updateWeightGoal } from '../services/weightGoalApi';
import { checkFitbitStatus } from '../services/fitbitApi';
import WeightGoalForm from '../components/WeightGoalForm';

const WeightGoals = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const navigate = useNavigate();

  // 認証状態とデータをロード
  useEffect(() => {
    const loadData = async () => {
      try {
        // Fitbit認証状態の確認
        const authStatus = await checkFitbitStatus();
        if (!authStatus.is_authenticated) {
          navigate('/fitbit/connect');
          return;
        }
        
        // 目標データのロード
        setLoading(true);
        const goalData = await fetchWeightGoals();
        setGoals(goalData);
        setError(null);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('データのロードに失敗しました。後でもう一度お試しください。');
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [navigate]);
  
  // 目標の削除
  const handleDeleteGoal = async (goalId) => {
    if (!window.confirm('この目標を削除してもよろしいですか？')) {
      return;
    }
    
    try {
      await deleteWeightGoal(goalId);
      // 削除後のリストを更新
      setGoals(prevGoals => prevGoals.filter(goal => goal.id !== goalId));
    } catch (err) {
      console.error('Error deleting goal:', err);
      setError('目標の削除に失敗しました。');
    }
  };
  
  // 目標の達成状態を切り替え
  const handleToggleAchieved = async (goal) => {
    try {
      const updatedGoal = await updateWeightGoal(goal.id, {
        is_achieved: !goal.is_achieved
      });
      
      // 更新後のリストを更新
      setGoals(prevGoals => 
        prevGoals.map(g => g.id === updatedGoal.id ? updatedGoal : g)
      );
    } catch (err) {
      console.error('Error updating goal:', err);
      setError('目標の更新に失敗しました。');
    }
  };
  
  // 新しい目標が作成されたときの処理
  const handleGoalCreated = (newGoal) => {
    setGoals(prevGoals => [...prevGoals, newGoal]);
    setShowForm(false);
  };
  
  // 目標ごとの進捗状況のスタイル
  const getProgressStyle = (percentage) => {
    return {
      width: `${percentage}%`,
      backgroundColor: percentage < 30 ? '#dc3545' : 
                      percentage < 70 ? '#ffc107' : '#28a745',
      height: '10px',
      borderRadius: '5px'
    };
  };

  return (
    <div>
      <h1>体重目標</h1>
      
      {error && (
        <div className="card error-message">
          <p>{error}</p>
        </div>
      )}
      
      <div className="action-bar">
        <button 
          className="btn" 
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? '目標フォームを閉じる' : '新しい目標を設定'}
        </button>
      </div>
      
      {showForm && (
        <WeightGoalForm onGoalCreated={handleGoalCreated} />
      )}
      
      {loading ? (
        <p>データを読み込んでいます...</p>
      ) : goals.length === 0 ? (
        <div className="card">
          <p>まだ体重目標が設定されていません。</p>
        </div>
      ) : (
        <div>
          <h2>現在の目標</h2>
          {goals.filter(goal => !goal.is_achieved).map(goal => (
            <div key={goal.id} className="card goal-card">
              <div className="goal-header">
                <h3>{goal.target_weight} kg までに痩せる</h3>
                <div className="goal-actions">
                  <button 
                    className="btn small" 
                    onClick={() => handleToggleAchieved(goal)}
                  >
                    達成済みにする
                  </button>
                  <button 
                    className="btn small secondary" 
                    onClick={() => handleDeleteGoal(goal.id)}
                  >
                    削除
                  </button>
                </div>
              </div>
              
              <p><strong>目標期日:</strong> {new Date(goal.target_date).toLocaleDateString()}</p>
              <p><strong>残り日数:</strong> {goal.days_remaining} 日</p>
              <p><strong>開始体重:</strong> {goal.start_weight} kg</p>
              
              {goal.description && (
                <p><strong>メモ:</strong> {goal.description}</p>
              )}
              
              <div className="progress-container">
                <div className="progress-bar">
                  <div className="progress" style={getProgressStyle(goal.progress_percentage)}></div>
                </div>
                <p className="progress-text">{Math.round(goal.progress_percentage)}% 達成</p>
              </div>
              
              <div className="goal-footer">
                <button 
                  className="btn small" 
                  onClick={() => navigate(`/fitbit/goal/${goal.id}`)}
                >
                  詳細を表示
                </button>
              </div>
            </div>
          ))}
          
          {goals.some(goal => goal.is_achieved) && (
            <>
              <h2>達成済みの目標</h2>
              {goals.filter(goal => goal.is_achieved).map(goal => (
                <div key={goal.id} className="card goal-card achieved">
                  <div className="goal-header">
                    <h3>{goal.target_weight} kg の目標を達成!</h3>
                    <div className="goal-actions">
                      <button 
                        className="btn small" 
                        onClick={() => handleToggleAchieved(goal)}
                      >
                        未達成に戻す
                      </button>
                      <button 
                        className="btn small secondary" 
                        onClick={() => handleDeleteGoal(goal.id)}
                      >
                        削除
                      </button>
                    </div>
                  </div>
                  
                  <p><strong>達成日:</strong> {new Date(goal.achieved_date).toLocaleDateString()}</p>
                  <p><strong>開始体重:</strong> {goal.start_weight} kg</p>
                  
                  {goal.description && (
                    <p><strong>メモ:</strong> {goal.description}</p>
                  )}
                  
                  <div className="progress-container">
                    <div className="progress-bar">
                      <div className="progress" style={getProgressStyle(100)}></div>
                    </div>
                    <p className="progress-text">100% 達成</p>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default WeightGoals;