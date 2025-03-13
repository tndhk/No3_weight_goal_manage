import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          React-Flask App
        </Link>
        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/" className="nav-link">
              Dashboard
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/input" className="nav-link">
              Data Input
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/analysis" className="nav-link">
              Analysis
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;