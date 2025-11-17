import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // You would create this for basic styling
import App from './App';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    {/* Wrap the app in the Router for client-side routing */}
    <BrowserRouter>
      {/* Wrap the app in the AuthProvider for global auth state */}
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);