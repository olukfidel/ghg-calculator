/*
 * This file sets up a proxy for the development server (npm start).
 * It intercepts requests to /api and /auth and forwards them
 * to the backend Flask server, avoiding CORS issues in development.
 */
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  app.use(
    ['/api', '/auth'], // Paths to proxy
    createProxyMiddleware({
      target: process.env.REACT_APP_API_URL || 'http://localhost:5000',
      changeOrigin: true,
    })
  );
};