# Heroku Deployment Guide

## Quick Setup (5 minutes)

### 1. Create Heroku App
```bash
heroku login
heroku create your-app-name
```
Note the app URL (e.g., `https://your-app-name.herokuapp.com`)

### 2. Set GitHub Secrets
Go to your GitHub repo → Settings → Secrets and variables → Actions → New repository secret

Add these three secrets:
- **HEROKU_API_KEY**: Get from https://dashboard.heroku.com/account/applications/authorizations/new
- **HEROKU_APP_NAME**: The app name you created above (e.g., `your-app-name`)
- **HEROKU_EMAIL**: Your Heroku account email

### 3. Push to Deploy
```bash
git push origin main
```

The GitHub Actions workflow will automatically deploy to Heroku in ~2-3 minutes.

### 4. Access Your App
```
https://your-app-name.herokuapp.com
```

Default Login:
- Username: `admin`
- Password: `admin123`

---

## Production Notes

- Database: PostgreSQL addon (auto-provisioned on first deploy)
- Uploads: Stored on ephemeral filesystem (use S3 for persistence)
- Environment: Python 3.11, gunicorn server
