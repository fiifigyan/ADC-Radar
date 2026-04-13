# Production Deployment Guide

## ADC-Radar - Production Ready Setup

This guide covers the production-ready configurations for the ADC-Radar application.

## Pre-Deployment Checklist

### Backend Setup
- [ ] Copy `.env.example` to `.env` and configure production values
- [ ] Update `FLASK_ENV=production` in environment
- [ ] Set `PYTHONUNBUFFERED=1` for proper logging
- [ ] Generate strong secret keys for Flask
- [ ] Configure CORS for production origins only
- [ ] Set up database credentials securely

### Frontend Setup
- [ ] Update API endpoints to production backend URL
- [ ] Set `NODE_ENV=production`
- [ ] Configure CDN URLs if needed
- [ ] Update social media links in Header/Footer components
- [ ] Verify all environment variables are correctly set

## Environment Variables

### Backend (.env)
```
FLASK_ENV=production
PYTHONUNBUFFERED=1
FLASK_APP=src.main
OPENAI_API_KEY=your-api-key
NOTION_INTEGRATION_TOKEN=your-token
DATABASE_URL=your-db-url
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
```

### Frontend (.env)
```
VITE_API_URL=https://api.yourdomain.com
VITE_ENVIRONMENT=production
```

## Docker Deployment

### Build Images
```bash
# Build backend
docker build -t adc-radar-backend:latest ./backend

# Build frontend
docker build -t adc-radar-frontend:latest ./frontend
```

### Run with Docker Compose
```bash
docker-compose up -d
```

- Backend API: http://localhost:5000
- Frontend: http://localhost:3000

## Production Optimizations Applied

### Frontend
✅ Dark/Light theme system with CSS variables
✅ Removed mock data files
✅ Theme persistence in localStorage
✅ Smooth theme transitions
✅ Mobile-responsive theme toggle

### Backend
✅ Removed debug and test scripts
✅ Removed test files and test dependencies
✅ Optimized requirements.txt (removed pytest)
✅ Cleaned up empty directories
✅ Production-ready Docker configuration

## Security Recommendations

1. **CORS Configuration**: Update CORS_ORIGINS to only allow your frontend domain
2. **Database**: Use environment variables for all credentials
3. **Secrets**: Never commit .env files; use secret management tools
4. **HTTPS**: Always use HTTPS in production
5. **Rate Limiting**: Consider adding rate limiting middleware
6. **Input Validation**: Validate all API inputs
7. **Logging**: Configure proper logging for monitoring

## Performance Tips

1. **Caching**: Implement Redis for session/data caching
2. **Database Indexing**: Ensure proper DB indexes for queries
3. **CDN**: Serve static assets from a CDN
4. **Compression**: Enable gzip compression on middleware
5. **Database Pooling**: Configure connection pooling for production

## Monitoring

Set up monitoring for:
- API response times
- Error rates and types
- Database query performance
- Resource usage (CPU, Memory)
- Scheduled job execution times

## Backup Strategy

1. Regular database backups (daily/hourly)
2. Configuration backups
3. Version control for all code changes
4. Document all production credentials in secure vault

## Version Updates

Keep these packages updated:
- Flask and extensions
- openai library
- notion-client
- React and dependencies

Check for security updates regularly:
```bash
pip audit  # For Python
npm audit  # For Node.js
```

## Troubleshooting

### Backend Issues
- Check logs: `docker logs adc-radar-backend`
- Verify database connectivity
- Check API endpoints with curl

### Frontend Issues
- Check browser console for errors
- Verify API URL configuration
- Test theme persistence in localStorage

## Support

For issues or questions:
1. Check logs first
2. Review environment configuration
3. Verify network connectivity
4. Check authentication tokens
