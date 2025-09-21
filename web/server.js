const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from public and src directories
app.use(express.static(path.join(__dirname, 'public')));
app.use('/src', express.static(path.join(__dirname, 'src')));

// Proxy API requests to the backend
app.use('/api', createProxyMiddleware({
    target: process.env.BACKEND_URL || 'http://localhost:8000',
    changeOrigin: true,
    pathRewrite: {
        '^/api': '/api/v1' // Rewrite /api to /api/v1 for backend
    },
    onProxyReq: (proxyReq, req, res) => {
        // Add any additional headers if needed
        console.log(`Proxying ${req.method} ${req.url} -> ${proxyReq.getHeader('host')}${proxyReq.path}`);
    },
    onError: (err, req, res) => {
        console.error('Proxy error:', err);
        res.status(500).json({ error: 'Backend service unavailable' });
    }
}));

// Catch all handler: send back index.html for client-side routing
// This should only handle routes that don't match static files
app.get('*', (req, res, next) => {
    // If the request has an extension or is for /src, let static middleware handle it
    if (req.path.includes('.') || req.path.startsWith('/src')) {
        return next();
    }

    // For SPA routes, always serve the main app (index.html)
    // The client-side router will handle authentication and page loading
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Healthcare Frontend Server running on http://localhost:${PORT}`);
    console.log(`Proxying API requests to: ${process.env.BACKEND_URL || 'http://localhost:8000'}`);
});