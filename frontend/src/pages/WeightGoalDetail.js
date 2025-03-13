import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchWeightGoal, fetchWeightDiff, fetchWeightProjection, updateWeightGoal } from '../services/weightGoalApi';
import { Line } from 'react-chartjs-2';

const WeightGoalDetail = () => {
  const { goalId } = useParams();
  const navigate = useNavigate();
  const [goal, setGoal] = useState(null);
  const [weightDiff, setWeightDiff] = useState(null);
  const [projection, setProjection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    target_weight: '',
    target_date: '',
    description: ''
  });

  // データのロード
  useEffect(() => {
    // loadDataメソッドを次のように修正します
    const loadData = async () => {
      try {
        setLoading(true);
        
        // 目標データの取得
        const goalData = await fetchWeightGoal(goalId);
        setGoal(goalData);
        
        // フォームデータの初期化
        setFormData({
          target_weight: goalData.target_weight,
          target_date: goalData.target_date,
          description: goalData.description || ''
        });
        
        // 差分データの取得 - エラーでも続行
        try {
          const diffData = await fetchWeightDiff(goalId);
          setWeightDiff(diffData);
        } catch (diffErr) {
          console.warn('Error loading weight diff data:', diffErr);
          // 差分データのエラーでも続行
        }
        
        // 予測データの取得 - エラーでも続行
        try {
          const projectionData = await fetchWeightProjection(goalId, 60);
          setProjection(projectionData);
        } catch (projErr) {
          console.warn('Error loading weight projection data:', projErr);
          // 予測データのエラーでも続行
        }
        
        setError(null);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('データのロードに失敗しました。後でもう一度お試しください。');
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [goalId]);
  
  // フォーム入力の処理
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  // 目標の更新
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const updatedGoal = await updateWeightGoal(goalId, {
        target_weight: parseFloat(formData.target_weight),
        target_date: formData.target_date,
        description: formData.description || undefined
      });
      
      setGoal(updatedGoal);
      setEditMode(false);
      
      // 差分データと予測データを再取得
      const diffData = await fetchWeightDiff(goalId);
      setWeightDiff(diffData);
      
      const projectionData = await fetchWeightProjection(goalId, 60);
      setProjection(projectionData);
      
    } catch (err) {
      console.error('Error updating goal:', err);
      setError('目標の更新に失敗しました。');
    }
  };
  
  // 目標の達成状態を切り替え
  const handleToggleAchieved = async () => {
    try {
      const updatedGoal = await updateWeightGoal(goalId, {
        is_achieved: !goal.is_achieved
      });
      
      setGoal(updatedGoal);
    } catch (err) {
      console.error('Error updating goal:', err);
      setError('目標の更新に失敗しました。');
    }
  };
  
  // 実際の体重と目標体重のチャートデータを作成
  const getActualVsTargetChartData = () => {
    if (!weightDiff || !weightDiff.daily_weight_diffs) {
      return {
        labels: [],
        datasets: []
      };
    }
    
    return {
      labels: weightDiff.daily_weight_diffs.map(diff => diff.date),
      datasets: [
        {
          label: '目標体重',
          data: weightDiff.daily_weight_diffs.map(diff => diff.target_weight),
          fill: false,
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgba(75, 192, 192, 1)',
          tension: 0.1
        },
        {
          label: '実際の体重',
          data: weightDiff.daily_weight_diffs.map(diff => diff.actual_weight),
          fill: false,
          backgroundColor: 'rgba(153, 102, 255, 0.2)',
          borderColor: 'rgba(153, 102, 255, 1)',
          tension: 0.1
        }
      ]
    };
  };
  
  // 将来の体重予測チャートデータを作成
  const getProjectionChartData = () => {
    if (!projection || !weightDiff) {
      return {
        labels: [],
        datasets: []
      };
    }
    
    // 実績データと予測データを結合
    const actualData = weightDiff.daily_weight_diffs.map(diff => ({
      date: diff.date,
      weight: diff.actual_weight
    })).filter(item => item.weight !== null);
    
    const projectionData = projection.weight_projections.map(proj => ({
      date: proj.date,
      weight: proj.projected_weight
    }));
    
    // 目標達成ラインを作成
    const targetWeight = goal.target_weight;
    const allDates = [
      ...actualData.map(item => item.date),
      ...projectionData.map(item => item.date)
    ];
    
    return {
      labels: allDates,
      datasets: [
        {
          label: '実績体重',
          data: allDates.map(date => {
            const found = actualData.find(item => item.date === date);
            return found ? found.weight : null;
          }),
          fill: false,
          backgroundColor: 'rgba(153, 102, 255, 0.2)',
          borderColor: 'rgba(153, 102, 255, 1)',
          tension: 0.1
        },
        {
          label: '予測体重',
          data: allDates.map(date => {
            const found = projectionData.find(item => item.date === date);
            return found ? found.weight : null;
          }),
          fill: false,
          backgroundColor: 'rgba(255, 159, 64, 0.2)',
          borderColor: 'rgba(255, 159, 64, 1)',
          borderDash: [5, 5],
          tension: 0.1
        },
        {
          label: '目標体重',
          data: allDates.map(() => targetWeight),
          fill: false,
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderDash: [3, 3],
          tension: 0
        }
      ]
    };
  };
  
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: '体重推移',
      },
    },
    scales: {
      x: {
        ticks: {
          maxTicksLimit: 10
        }
      },
      y: {
        beginAtZero: false,
      }
    }
  };

  if (loading) {
    return <p>データを読み込んでいます...</p>;
  }

  if (error) {
    return (
      <div className="card error-message">
        <p>{error}</p>
        <button className="btn" onClick={() => navigate('/fitbit/goals')}>
          戻る
        </button>
      </div>
    );
  }

  if (!goal) {
    return (
      <div className="card error-message">
        <p>目標が見つかりません。</p>
        <button className="btn" onClick={() => navigate('/fitbit/goals')}>
          戻る
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1>体重目標詳細</h1>
      
      <div className="action-bar">
        <button className="btn" onClick={() => navigate('/fitbit/goals')}>
          目標リストに戻る
        </button>
      </div>
      
      <div className="card goal-card">
        {editMode ? (
          <>
            <h2>目標を編集</h2>
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
              
              <div className="form-actions">
                <button type="submit" className="btn">
                  更新
                </button>
                <button type="button" className="btn secondary" onClick={() => setEditMode(false)}>
                  キャンセル
                </button>
              </div>
            </form>
          </>
        ) : (
          <>
            <div className="goal-header">
              <h2>{goal.target_weight} kg の目標</h2>
              <div className="goal-actions">
                <button 
                  className="btn small" 
                  onClick={() => setEditMode(true)}
                >
                  編集
                </button>
                <button 
                  className="btn small" 
                  onClick={handleToggleAchieved}
                >
                  {goal.is_achieved ? '未達成に戻す' : '達成済みにする'}
                </button>
              </div>
            </div>
            
            <div className="summary-stats">
              <div className="stat-box">
                <h3>開始体重</h3>
                <p>{goal.start_weight} kg</p>
              </div>
              <div className="stat-box">
                <h3>目標体重</h3>
                <p>{goal.target_weight} kg</p>
              </div>
              <div className="stat-box">
                <h3>残り日数</h3>
                <p>{goal.days_remaining} 日</p>
              </div>
              <div className="stat-box">
                <h3>目標期日</h3>
                <p>{new Date(goal.target_date).toLocaleDateString()}</p>
              </div>
            </div>
            
            {goal.description && (
              <div className="goal-description">
                <h3>メモ</h3>
                <p>{goal.description}</p>
              </div>
            )}
            
            <div className="progress-container">
              <h3>進捗 ({Math.round(goal.progress_percentage)}%)</h3>
              <div className="progress-bar">
                <div 
                  className="progress" 
                  style={{
                    width: `${goal.progress_percentage}%`,
                    backgroundColor: goal.progress_percentage < 30 ? '#dc3545' : 
                                    goal.progress_percentage < 70 ? '#ffc107' : '#28a745'
                  }}
                ></div>
              </div>
            </div>
          </>
        )}
      </div>
      
      {!editMode && weightDiff && (
        <div className="card">
          <h2>進捗状況</h2>
          
          <div className="summary-stats">
            <div className="stat-box">
              <h3>現在の体重</h3>
              <p>{weightDiff.current_weight?.toFixed(1) || 'N/A'} kg</p>
            </div>
            <div className="stat-box">
              <h3>目標との差分</h3>
              <p className={weightDiff.weight_to_lose > 0 ? 'increase' : 'decrease'}>
                {weightDiff.weight_to_lose?.toFixed(1) || 'N/A'} kg
              </p>
            </div>
            <div className="stat-box">
              <h3>1日あたりの変化</h3>
              <p className={weightDiff.avg_actual_change_per_day > 0 ? 'increase' : 'decrease'}>
                {weightDiff.avg_actual_change_per_day?.toFixed(2) || 'N/A'} kg/日
              </p>
            </div>
          </div>
          
          <div className="chart-container">
            <Line data={getActualVsTargetChartData()} options={chartOptions} />
          </div>
        </div>
      )}
      
      {!editMode && projection && (
        <div className="card">
          <h2>将来予測</h2>
          
          {projection.insufficient_data && (
            <div className="warning-message">
              <p>注意: 体重の記録が不足しているため、理想的な体重変化に基づく予測を表示しています。より正確な予測には、定期的な体重記録が必要です。</p>
            </div>
          )}
          
          <div className="summary-stats">
            <div className="stat-box">
              <h3>平均変化率</h3>
              <p className={projection.avg_change_per_day > 0 ? 'increase' : 'decrease'}>
                {projection.avg_change_per_day?.toFixed(2) || 'N/A'} kg/日
              </p>
            </div>
            <div className="stat-box">
              <h3>予測達成日</h3>
              <p>
                {projection.projected_completion_date 
                  ? new Date(projection.projected_completion_date).toLocaleDateString()
                  : '達成困難'}
              </p>
            </div>
          </div>
          
          <div className="chart-container">
            <Line data={getProjectionChartData()} options={chartOptions} />
          </div>
        </div>
      )}
    </div>
  );
};

export default WeightGoalDetail;