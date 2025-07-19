# Azure App Service Deployment Guide

This guide will help you deploy the On The Fly Update application to Azure App Service using the existing Azure resources.

## Prerequisites

Before starting the deployment, ensure you have the following installed:

1. **Azure CLI** - [Installation Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
3. **Python 3.12** - [Download](https://www.python.org/downloads/)
4. **Git** - [Download](https://git-scm.com/)

## Azure Resources

The deployment uses the following existing Azure resources:

- **Resource Group**: `on-the-fly-update`
- **App Service**: `onthe-fly-update-v1.azurewebsites.net`

## Environment Variables

Create a `config.env` file in the root directory with the following variables:

```env
MONGO_URI=mongodb://your-mongo-connection-string
DB_NAME=customer_management
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-storage-account;AccountKey=your-key;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER_NAME=programfiles
SECRET_KEY=your-secret-key-here
```

## Deployment Options

### Option 1: Combined Deployment (Recommended)

Deploy both backend and frontend to the same app service:

```bash
python deploy-to-azure.py
```

This script will:

1. Check prerequisites
2. Load environment variables
3. Create deployment files
4. Build the React frontend
5. Update API URLs
6. Deploy to the existing Azure App Service

### Option 2: Separate Deployments

#### Backend Only

```bash
python azure-deploy-backend.py
```

#### Frontend Only

```bash
python azure-deploy-frontend.py
```

## Deployment Process

### 1. Combined Deployment

The combined deployment script performs the following steps:

1. **Prerequisites Check**: Verifies Azure CLI, Node.js, and Python are installed
2. **Environment Setup**: Loads environment variables from `config.env`
3. **File Preparation**: Creates necessary deployment files
4. **Frontend Build**: Installs dependencies and builds the React app
5. **URL Updates**: Updates API endpoints to use the Azure app service URL
6. **Azure Deployment**: Deploys to the existing app service

### 2. Azure App Service Configuration

The deployment configures the following settings:

- **Runtime**: Python 3.12
- **Startup Command**: `gunicorn --bind=0.0.0.0 --timeout 600 app:app`
- **Environment Variables**: All variables from `config.env`
- **Build Configuration**: Optimized for combined backend/frontend deployment

### 3. Application Structure

After deployment, the app service will serve:

- **Backend API**: All `/api/*` routes handled by Flask
- **Frontend**: Static files served from the build directory
- **Routing**: React Router handles client-side routing

## Post-Deployment

### 1. Testing

After deployment, test the following:

1. **Backend API**: `https://onthe-fly-update-v1.azurewebsites.net/api/customers/`
2. **Frontend**: `https://onthe-fly-update-v1.azurewebsites.net`
3. **Admin Login**: Use admin credentials to test admin functionality
4. **Customer Registration**: Test customer registration and login

### 2. Monitoring

Monitor your application using:

1. **Azure Portal**: Check app service logs and metrics
2. **Application Insights**: Enable for detailed monitoring
3. **Log Stream**: View real-time logs in Azure Portal

### 3. Troubleshooting

Common issues and solutions:

#### Environment Variables

- Ensure all required environment variables are set in Azure App Service
- Check the `config.env` file format
- Verify MongoDB connection string is correct

#### CORS Issues

- The backend is configured with CORS for the frontend domain
- If using a custom domain, update CORS settings

#### Build Failures

- Check Node.js version compatibility
- Ensure all dependencies are properly installed
- Review build logs in Azure Portal

#### Database Connection

- Verify MongoDB/CosmosDB connection string
- Check network connectivity
- Ensure database exists and is accessible

## Custom Domain Configuration

To use a custom domain:

1. **Add Custom Domain** in Azure App Service
2. **Configure DNS** records
3. **Update CORS** settings if needed
4. **Update Frontend URLs** if necessary

## Scaling and Performance

### App Service Plans

- **Basic (B1)**: Suitable for development and testing
- **Standard (S1)**: Recommended for production
- **Premium (P1)**: For high-performance requirements

### Performance Optimization

- Enable **Always On** for consistent performance
- Configure **Auto Scaling** based on metrics
- Use **CDN** for static content delivery
- Enable **Compression** for better performance

## Security Considerations

### Environment Variables

- Never commit sensitive data to version control
- Use Azure Key Vault for production secrets
- Rotate secrets regularly

### Network Security

- Configure **IP Restrictions** if needed
- Use **Private Endpoints** for database connections
- Enable **HTTPS Only** for all traffic

### Authentication

- Ensure JWT tokens are properly configured
- Use strong secret keys
- Implement proper session management

## Backup and Recovery

### Database Backup

- Configure automated backups for CosmosDB
- Test restore procedures regularly
- Document recovery procedures

### Application Backup

- Use Azure App Service backup features
- Store backups in separate regions
- Test disaster recovery procedures

## Cost Optimization

### Resource Management

- Use appropriate app service plan sizes
- Monitor resource usage
- Scale down during non-peak hours

### Storage Optimization

- Clean up unused files regularly
- Use appropriate storage tiers
- Monitor storage costs

## Support and Maintenance

### Regular Maintenance

- Keep dependencies updated
- Monitor security advisories
- Review and update deployment scripts

### Monitoring

- Set up alerts for critical metrics
- Monitor error rates and response times
- Track user activity and performance

## Troubleshooting Commands

### Check App Service Status

```bash
az webapp show --resource-group on-the-fly-update --name onthe-fly-update-v1
```

### View Logs

```bash
az webapp log tail --resource-group on-the-fly-update --name onthe-fly-update-v1
```

### Restart App Service

```bash
az webapp restart --resource-group on-the-fly-update --name onthe-fly-update-v1
```

### Check Environment Variables

```bash
az webapp config appsettings list --resource-group on-the-fly-update --name onthe-fly-update-v1
```

## Additional Resources

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [React Production Build](https://create-react-app.dev/docs/production-build/)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/)

---

For support or questions, please refer to the project documentation or contact the development team.
