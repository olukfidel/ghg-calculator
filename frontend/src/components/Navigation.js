import React, { useContext } from 'react';
import { NavLink } from 'react-router-dom';
import AuthContext from '../context/AuthContext';

// Basic inline styles for the nav bar
const navStyle = {
  backgroundColor: '#f0f0f0',
  padding: '1rem',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
};

const linkStyle = {
  margin: '0 10px',
  textDecoration: 'none',
  color: '#333',
  fontWeight: 'bold',
};

const activeLinkStyle = {
  color: '#007bff',
};

function Navigation() {
  const { isAuthenticated, logout } = useContext(AuthContext);

  return (
    <nav style={navStyle}>
      <div>
        <NavLink
          to="/"
          style={linkStyle}
          className={({ isActive }) => (isActive ? 'active' : '')}
        >
          GHG Calculator
        </NavLink>
      </div>
      <div>
        {isAuthenticated ? (
          <>
            <NavLink
              to="/"
              style={linkStyle}
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/input"
              style={linkStyle}
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              Add Data
            </NavLink>
            <NavLink
              to="/reports"
              style={linkStyle}
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              Reports
            </NavLink>
            <button onClick={logout} style={{ ...linkStyle, border: 'none', background: 'none' }}>
              Logout
            </button>
          </>
        ) : (
          <NavLink
            to="/login"
            style={linkStyle}
            className={({ isActive }) => (isActive ? 'active' : '')}
          >
            Login / Register
          </NavLink>
        )}
      </div>
      {/* Basic CSS for active class */}
      <style>{`
        .active {
          color: #007bff;
        }
      `}</style>
    </nav>
  );
}

export default Navigation;