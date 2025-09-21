# Healthcare Patient Management System - Frontend

A modern, responsive frontend for healthcare patient management built with HTMX, Alpine.js, and Tailwind CSS.

## Features

- **Authentication**: JWT-based login with role-based access (nurse, physician, admin)
- **Dashboard**: Overview of patient statistics and recent activity
- **Patient Management**: Search, view, and manage patient records
- **Medical Forms**: Dynamic forms for assessments and documentation
- **Responsive Design**: Mobile-first design with accessibility compliance
- **Real-time Updates**: HTMX-powered dynamic content loading

## Technology Stack

- **HTMX**: For dynamic content loading without SPA complexity
- **Alpine.js**: Lightweight reactivity for client-side interactions
- **Tailwind CSS**: Utility-first CSS framework with medical design tokens
- **Express.js**: Development server with API proxy
- **Jest**: Testing framework with Testing Library
- **ESLint & Prettier**: Code quality and formatting

## Project Structure

```
web/
├── public/                 # Static files served directly
│   ├── index.html         # Main application entry point
│   ├── login.html         # Authentication page
│   ├── dashboard.html     # Main dashboard
│   └── ...                # Other HTML pages
├── src/                   # Source code
│   ├── styles/            # CSS stylesheets
│   │   └── main.css       # Main stylesheet with Tailwind
│   ├── js/                # JavaScript modules
│   │   └── main.js        # Alpine.js stores and utilities
│   ├── components/        # Reusable HTML components
│   └── layouts/           # Page layouts
├── tests/                 # Test files
├── package.json           # Node.js dependencies and scripts
├── tailwind.config.js     # Tailwind CSS configuration
├── server.js              # Development server
└── .env                   # Environment variables
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API server running (see backend README)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your backend URL
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Development Scripts

- `npm run dev` - Start development server with API proxy
- `npm run dev:live` - Start live-server for static file serving
- `npm test` - Run Jest tests
- `npm run lint` - Lint JavaScript files
- `npm run format` - Format code with Prettier

## Configuration

### Environment Variables

- `PORT`: Development server port (default: 3000)
- `BACKEND_URL`: Backend API URL (default: http://localhost:8000)
- `NODE_ENV`: Environment mode

### Tailwind CSS

The project uses a custom Tailwind configuration with healthcare-specific design tokens:

- Medical color palette (primary, success, warning, error)
- Responsive typography
- RTL support for Arabic text
- Custom component classes

## API Integration

The frontend communicates with the FastAPI backend through:

- **Authentication**: JWT tokens stored in localStorage
- **API Proxy**: Express server proxies `/api/*` requests to backend
- **HTMX**: Automatic authorization headers on requests
- **Error Handling**: Automatic logout on 401 responses

## Testing

Run tests with:
```bash
npm test
```

Tests include:
- Component rendering
- Form validation
- API integration
- Accessibility checks

## Deployment

### Production Build

The application is static and can be served by any web server:

1. Build for production:
```bash
npm run build
```

2. Serve the `public/` directory with your web server

### Docker Deployment

```dockerfile
FROM nginx:alpine
COPY public /usr/share/nginx/html
EXPOSE 80
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the established code style
2. Write tests for new features
3. Ensure accessibility compliance
4. Test with screen readers and keyboard navigation

## Security

- JWT tokens are stored securely in localStorage
- All API requests include authorization headers
- Input validation on both client and server
- HTTPS required in production

## Performance

- Lazy loading of HTMX content
- Optimized Tailwind CSS (purge unused styles)
- Minimal JavaScript bundle
- Efficient API calls with caching

## Accessibility

- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- RTL language support