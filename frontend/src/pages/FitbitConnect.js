import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { checkFitbitStatus, getFitbitAuthUrl } from '../services/fitbitApi';

const FitbitConnect = () => {
  const [status, setStatus] = useState({ loading: true, isAuthenticated: false, error: null });
  const location = useLocation();
  const navigate = useNavigate();
  
  // コンポーネントマウント時と、URLパラメータ変更時に認証状態を確認
  useEffect(() => {
    const checkAuth = async () => {
      try {
        setStatus(prev => ({ ...prev, loading: true }));
        const result = await checkFitbitStatus();
        setStatus({ 
          loading: false, 
          isAuthenticated: result.is_authenticated, 
          error: null,
          expiresAt: result.expires_at,
          scope: result.scope
        });
      } catch (err) {
        setStatus({ 
          loading: false, 
          isAuthenticated: false, 
          error: 'Failed to check authentication status'
        });
      }
    };
    
    checkAuth();
    
    // URLにエラーパラメータがある場合（認証失敗時のリダイレクト）
    const errorParam = new URLSearchParams(location.search).get('message');
    if (errorParam) {
      setStatus({ 
        loading: false,
        isAuthenticated: false,
        error: `Authentication failed: ${errorParam}`
      });
    }
    
    // success パスの場合（認証成功時のリダイレクト）
    if (location.pathname.includes('/success')) {
      setStatus(prev => ({ 
        ...prev,
        loading: false,
        successMessage: 'Successfully connected with Fitbit!'
      }));
    }
  }, [location]);
  
  // Fitbitへの接続を開始
  const handleConnect = () => {
    window.location.href = getFitbitAuthUrl();
  };
  
  // 接続後にダッシュボードへ移動
  const handleContinue = () => {
    navigate('/fitbit/dashboard');
  };
  
  return (
    <div>
      <h1>Connect with Fitbit</h1>
      
      <div className="card">
        {status.loading ? (
          <p>Checking authentication status...</p>
        ) : status.error ? (
          <div className="error-message">
            <p>{status.error}</p>
            <button className="btn" onClick={handleConnect}>Try Again</button>
          </div>
        ) : status.successMessage ? (
          <div className="success-message">
            <p>{status.successMessage}</p>
            <button className="btn" onClick={handleContinue}>Continue to Dashboard</button>
          </div>
        ) : status.isAuthenticated ? (
          <div>
            <p className="success-message">Connected with Fitbit!</p>
            <p>Your authentication expires at: {new Date(status.expiresAt).toLocaleString()}</p>
            <p>Authorized scopes: {status.scope}</p>
            <button className="btn" onClick={handleContinue}>Go to Fitbit Dashboard</button>
            <button className="btn secondary" onClick={handleConnect} style={{ marginLeft: '10px' }}>Re-authenticate</button>
          </div>
        ) : (
          <div>
            <p>Connect your Fitbit account to access your health data.</p>
            <p>This app will request access to your weight data.</p>
            <button className="btn" onClick={handleConnect}>Connect Fitbit Account</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default FitbitConnect;