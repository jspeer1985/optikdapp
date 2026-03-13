# Free SMTP Setup Guide - Optik Platform

## 🚀 Quick Setup Options

### Option 1: Gmail (Recommended for Development)
**Best for:** Testing, small projects  
**Free limit:** 500 emails/day  
**Setup time:** 5 minutes

#### Steps:
1. **Enable 2-Factor Authentication**
   - Go to: https://myaccount.google.com/apppasswords
   - Sign in to your Gmail account

2. **Create App Password**
   - Click "Select app" → "Other (Custom name)"
   - App name: `Optik Platform`
   - Generate 16-character password
   - **Important:** Use the App Password, NOT your regular Gmail password

3. **Configure Environment**
   ```bash
   SMTP_USER=your_gmail_address@gmail.com
   SMTP_PASSWORD=your_16_character_app_password
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_SECURE=true
   ```

4. **Test Configuration**
   ```bash
   curl -X POST http://localhost:3003/api/email \
     -H "Content-Type: application/json" \
     -d '{"type":"test","to":"test@example.com","subject":"Test Email"}'
   ```

---

### Option 2: SendGrid (Recommended for Production)
**Best for:** Production, transactional emails  
**Free tier:** 100 emails/day forever  
**Setup time:** 10 minutes

#### Steps:
1. **Create SendGrid Account**
   - Sign up: https://signup.sendgrid.com
   - Verify your email address

2. **Create API Key**
   - Go to: https://app.sendgrid.com/settings/api_keys
   - Create new API key
   - Copy the API key

3. **Configure Environment**
   ```bash
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USER=apikey
   SMTP_PASSWORD=your_sendgrid_api_key_here
   ```

4. **Update Email Service**
   ```typescript
   // In lib/email-service.ts
   host: process.env.SMTP_HOST || 'smtp.sendgrid.net',
   secure: false, // SendGrid uses TLS
   ```

---

### Option 3: Mailgun
**Best for:** Production, high volume  
**Free tier:** 1,000 emails/month  
**Setup time:** 15 minutes

#### Steps:
1. **Create Mailgun Account**
   - Sign up: https://www.mailgun.com

2. **Verify Domain**
   - Add your domain to Mailgun
   - Configure DNS records (TXT/ MX)

3. **Get API Credentials**
   - Go to: https://app.mailgun.com/settings/api_security
   - Create API key

4. **Configure Environment**
   ```bash
   SMTP_HOST=smtp.mailgun.org
   SMTP_PORT=587
   SMTP_USER=postmaster@mg.yourdomain.com
   SMTP_PASSWORD=your_mailgun_api_key_here
   ```

---

### Option 4: Brevo (Sendinblue)
**Best for:** Marketing, moderate volume  
**Free tier:** 300 emails/day  
**Setup time:** 10 minutes

#### Steps:
1. **Create Brevo Account**
   - Sign up: https://www.brevo.com

2. **Get SMTP Credentials**
   - Go to: https://app.brevo.com/settings/smtp_server
   - Create SMTP key

3. **Configure Environment**
   ```bash
   SMTP_HOST=smtp-relay.sendinblue.com
   SMTP_PORT=587
   SMTP_USER=your_brevo_account@email.com
   SMTP_PASSWORD=your_brevo_api_key_here
   ```

---

## 🔧 Configuration Examples

### Gmail Setup (Development)
```bash
# Copy secure template
cp .env.secure .env.local

# Edit with your Gmail credentials
nano .env.local

# Add these lines:
SMTP_USER=your_gmail@gmail.com
SMTP_PASSWORD=your_16_char_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURE=true

# Set permissions
chmod 600 .env.local
```

### SendGrid Setup (Production)
```bash
# Update .env.local
SMTP_HOST=smtp.sendgrid.net
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_PORT=587
SMTP_SECURE=false
```

## 🧪 Testing Your SMTP Setup

### Test Email Sending
```bash
# Test welcome email
curl -X POST http://localhost:3003/api/email \
  -H "Content-Type: application/json" \
  -d '{
    "type": "welcome",
    "to": "test@example.com",
    "subject": "Test Welcome Email",
    "name": "Test User"
  }'

# Test password reset
curl -X POST http://localhost:3003/api/email \
  -H "Content-Type: application/json" \
  -d '{
    "type": "password-reset",
    "to": "test@example.com", 
    "subject": "Test Password Reset",
    "resetToken": "test-reset-token-12345"
  }'
```

### Test Configuration
```bash
# Test SMTP configuration
curl -X GET http://localhost:3003/api/email
```

## 📧 Production Deployment

### Environment Variables Required
```bash
# Required for all SMTP services
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USER=your_username
SMTP_PASSWORD=your_password_or_api_key
SMTP_SECURE=true_or_false
FROM_EMAIL=noreply@optikcoin.com

# For Gmail specifically
SMTP_SECURE=true
```

### Security Best Practices
1. **Never commit** `.env.local` to version control
2. **Use environment variables** for all credentials
3. **Enable TLS/SSL** in production
4. **Set up SPF/DKIM** records for your domain
5. **Monitor email reputation** and deliverability
6. **Use dedicated IP** for sending emails
7. **Implement rate limiting** on your email endpoints

## 🚨 Common Issues & Solutions

### Gmail Issues
- **"Less secure app" error**: Enable 2-factor authentication
- **"Authentication failed"**: Use App Password, not regular password
- **"Daily limit exceeded"**: Use SendGrid for higher volume

### SendGrid Issues
- **"550 Unauthenticated sender"**: Verify API key is correct
- **"Invalid API key"**: Regenerate API key from SendGrid dashboard

### General Issues
- **Connection timeout**: Check firewall settings
- **"SSL/TLS handshake failed": Verify SMTP_SECURE setting
- **"Rate limit exceeded": Implement proper rate limiting

## 📊 Comparison Table

| Service | Free Limit | Setup Time | Best For | Difficulty |
|----------|-------------|------------|----------|----------|
| **Gmail** | 500/day | 5 min | Development | ⭐ Easy |
| **SendGrid** | 100/day | 10 min | Production | ⭐⭐ Easy |
| **Mailgun** | 1,000/month | 15 min | Production | ⭐⭐ Medium |
| **Brevo** | 300/day | 10 min | Marketing | ⭐⭐ Easy |

## 🎯 Recommendations

### For Development
- Use **Gmail** for quick setup and testing
- Perfect for small team and personal projects

### For Production
- Use **SendGrid** for reliable transactional emails
- Consider **Mailgun** for higher volume needs
- Implement **dedicated IP** and proper DNS records

### For Scale
- Consider **AWS SES** (62,000 emails/month free)
- Use **dedicated email service** for enterprise needs
- Implement **email queue** for high volume sending

---

**Need help?** Check the email service logs: `npm run dev` and watch for email-related logs.

**Security Reminder:** Never share your SMTP credentials or commit them to version control!
