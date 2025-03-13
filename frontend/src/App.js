import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import DataInput from './pages/DataInput';
import Analysis from './pages/Analysis';
import FitbitConnect from './pages/FitbitConnect';
import FitbitDashboard from './pages/FitbitDashboard';
import WeightGoals from './pages/WeightGoals';
import WeightGoalDetail from './pages/WeightGoalDetail';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <div className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/input" element={<DataInput />} />
            <Route path="/analysis" element={<Analysis />} />
            
            {/* Fitbit関連のルート */}
            <Route path="/fitbit/connect" element={<FitbitConnect />} />
            <Route path="/fitbit/success" element={<FitbitConnect />} />
            <Route path="/fitbit/error" element={<FitbitConnect />} />
            <Route path="/fitbit/dashboard" element={<FitbitDashboard />} />
            
            {/* 体重目標関連のルート */}
            <Route path="/fitbit/goals" element={<WeightGoals />} />
            <Route path="/fitbit/goal/:goalId" element={<WeightGoalDetail />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;