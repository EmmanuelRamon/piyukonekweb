# Piyukonek - Deployment Guide

## Before Hosting: Setup Environment Variables

1. **Copy the example file:**
   ```
   copy .env.example .env
   ```
   (On Mac/Linux: `cp .env.example .env`)

2. **Edit `.env`** and set all required values:
   - `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
   - `DATABASE_URL` - Your MySQL connection string from your host
   - `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER` - Gmail app password
   - `HF_API_TOKEN` - From https://huggingface.co/settings/tokens (for chatbot)

3. **For production, set:**
   ```
   FLASK_DEBUG=false
   FLASK_ENV=production
   HTTPS_ENABLED=true
   ```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# .env is optional for local - uses defaults
# SECRET_KEY auto-generates, DATABASE_URL defaults to local MySQL

python piyukonek/app.py
```

## Production Deployment

### 1. Use a production WSGI server (not Flask dev server)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "piyukonek.app:app"
```

### 2. Set environment variables on your host

- **PythonAnywhere:** Web tab → "Code" → WSGI file, set env in WSGI or "Virtualenv" section
- **Heroku:** `heroku config:set SECRET_KEY=xxx DATABASE_URL=xxx ...`
- **Railway/Render:** Project → Variables → Add each from .env

### 3. Use HTTPS

- Enable SSL on your hosting (Let's Encrypt, Cloudflare, etc.)
- Set `HTTPS_ENABLED=true` so session cookies are secure

### 4. Database

- Use a hosted MySQL (e.g., ClearDB, PlanetScale, AWS RDS)
- Set `DATABASE_URL=mysql+pymysql://user:pass@host:port/dbname`

## ⚠️ Important: Regenerate Exposed Credentials

If this code was previously committed with hardcoded secrets, **regenerate them**:
- **Gmail:** Revoke old App Password, create new at https://myaccount.google.com/apppasswords
- **OpenAI:** Revoke old key, create new at https://platform.openai.com/api-keys
- **Hugging Face:** Revoke old token, create new at https://huggingface.co/settings/tokens

## Security Checklist

- [ ] SECRET_KEY is 32+ characters, unique, never committed
- [ ] All API keys and passwords in .env, not in code
- [ ] FLASK_DEBUG=false in production
- [ ] HTTPS enabled, HTTPS_ENABLED=true
- [ ] Database uses non-root user with strong password
- [ ] .env is in .gitignore and never committed
