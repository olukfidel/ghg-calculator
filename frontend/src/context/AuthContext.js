import React, { createContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

// Create the context
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  // Get the token from storage on initial load
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  /**
   * This effect runs when the 'token' state changes or on app load.
   * It updates the 'isAuthenticated' state.
   */
  useEffect(() => {
    if (token) {
      setIsAuthenticated(true);
      // In a real app, you'd verify the token with a '/api/me' route here
      // and fetch the user data.
    } else {
      setIsAuthenticated(false);
    }
    // We are done loading, so show the app.
    setLoading(false);
  }, [token]);

  /**
   * Handle user login.
   */
  const login = useCallback(async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      const { auth_token, user } = response.data;

      // Store token in localStorage (for the api.js interceptor to use)
      localStorage.setItem('authToken', auth_token);
      // Set the user in state
      setUser(user);
      // Set the token in state, which triggers the useEffect
      setToken(auth_token);
      
      return true;
    } catch (error) {
      console.error('Login failed:', error.response?.data?.message || error.message);
      return false;
    }
  }, []);

  /**
   * Handle user registration.
   */
  const register = useCallback(async (username, email, password, company_name) => {
    try {
      const response = await api.post('/auth/register', {
        username,
        email,
        password,
        company_name,
      });
      const { auth_token, user } = response.data;

      // Log the user in immediately after registration
      localStorage.setItem('authToken', auth_token);
      setUser(user);
      setToken(auth_token);
      
      return true;
    } catch (error) {
      console.error('Registration failed:', error.response?.data?.message || error.message);
      return false;
    }
  }, []);

  /**
   * Handle user logout.
   */
  const logout = useCallback(() => {
    // Clear token from storage
    localStorage.removeItem('authToken');
    // Clear state
    setToken(null);
    setUser(null);
  }, []);

  // Provide the context value to children
  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated,
        loading,
        login,
        register,
        logout,
      }}
    >
      {/* Don't render the app until auth state is determined */}
      {!loading && children}
    </AuthContext.Provider>
  );
};

export default AuthContext;