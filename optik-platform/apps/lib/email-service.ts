import nodemailer from 'nodemailer';

// Email configuration interface
interface EmailConfig {
  host: string;
  port: number;
  secure: boolean;
  auth: {
    user: string;
    pass: string;
  };
}

// Email message interface
interface EmailMessage {
  to: string | string[];
  subject: string;
  text?: string;
  html?: string;
  from?: string;
}

// Email service class
export class EmailService {
  private transporter: nodemailer.Transporter;
  private config: EmailConfig;

  constructor() {
    this.config = {
      host: process.env.SMTP_HOST || 'smtp.gmail.com',
      port: parseInt(process.env.SMTP_PORT || '587'),
      secure: process.env.SMTP_SECURE === 'true',
      auth: {
        user: process.env.SMTP_USER || 'apikey',
        pass: process.env.SMTP_PASSWORD || '',
      },
    };

    this.transporter = nodemailer.createTransport(this.config);
  }

  // Send email
  async sendEmail(message: EmailMessage): Promise<{ success: boolean; error?: string }> {
    try {
      const mailOptions = {
        from: message.from || process.env.FROM_EMAIL || 'noreply@optikcoin.com',
        to: message.to,
        subject: message.subject,
        text: message.text,
        html: message.html,
      };

      const info = await this.transporter.sendMail(mailOptions);
      console.log('Email sent successfully:', info.messageId);
      
      return { success: true };
    } catch (error) {
      console.error('Email sending failed:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error occurred' 
      };
    }
  }

  // Send welcome email
  async sendWelcomeEmail(email: string, name: string): Promise<{ success: boolean; error?: string }> {
    const htmlContent = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
          <h1 style="margin: 0; font-size: 28px; margin-bottom: 20px;">Welcome to OptikCoin! 🚀</h1>
          <p style="font-size: 16px; line-height: 1.5; margin: 0 0 20px 0;">
            Hi ${name},<br><br>
            Welcome to the future of NFT pairing on Solana! Your account has been successfully created.
          </p>
          <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin: 0 0 10px 0; color: #FFD700;">Getting Started:</h3>
            <ul style="text-align: left; font-size: 14px; line-height: 1.6;">
              <li style="margin-bottom: 8px;">🔗 Connect your Solana wallet</li>
              <li style="margin-bottom: 8px;">🎨 Create your first NFT pair</li>
              <li style="margin-bottom: 8px;">💎 Explore the marketplace</li>
              <li style="margin-bottom: 8px;">📊 Track your portfolio</li>
            </ul>
          </div>
          <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
            <p style="font-size: 12px; opacity: 0.8; margin: 0;">
              Need help? Reply to this email or visit our 
              <a href="https://optikcoin.com/support" style="color: #FFD700; text-decoration: none;">support center</a>
            </p>
          </div>
        </div>
        <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
          <p style="margin: 0; font-size: 12px; color: #6c757d;">
            This is an automated message from OptikCoin. Please do not reply to this email directly.
          </p>
          <div style="margin-top: 15px;">
            <a href="https://optikcoin.com" style="display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
              Visit OptikCoin
            </a>
          </div>
        </div>
      </div>
    `;

    return this.sendEmail({
      to: email,
      subject: 'Welcome to OptikCoin! 🚀',
      html: htmlContent,
      text: `Welcome ${name} to OptikCoin! Your account has been successfully created.`,
    });
  }

  // Send password reset email
  async sendPasswordResetEmail(email: string, resetToken: string): Promise<{ success: boolean; error?: string }> {
    const resetUrl = `${process.env.NEXT_PUBLIC_APP_URL}/reset-password?token=${resetToken}`;
    
    const htmlContent = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
          <h1 style="margin: 0; font-size: 28px; margin-bottom: 20px;">Password Reset Request 🔐</h1>
          <p style="font-size: 16px; line-height: 1.5; margin: 0 0 20px 0;">
            We received a request to reset your password for your OptikCoin account.
          </p>
          <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0 0 15px 0; font-size: 14px;">
              Click the button below to reset your password. This link will expire in 1 hour.
            </p>
            <div style="text-align: center; margin: 20px 0;">
              <a href="${resetUrl}" style="display: inline-block; background: #ffc107; color: #212529; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                Reset Password
              </a>
            </div>
            <p style="margin: 15px 0 0 0; font-size: 12px; opacity: 0.8;">
              If the button doesn't work, copy and paste this link:<br>
              <code style="background: #f8f9fa; padding: 5px; border-radius: 3px; font-size: 11px;">
                ${resetUrl}
              </code>
            </p>
          </div>
          <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
            <p style="font-size: 12px; opacity: 0.8; margin: 0;">
              If you didn't request this password reset, please ignore this email or contact support.
            </p>
          </div>
        </div>
      </div>
    `;

    return this.sendEmail({
      to: email,
      subject: 'Reset Your OptikCoin Password 🔐',
      html: htmlContent,
      text: `Reset your OptikCoin password here: ${resetUrl}`,
    });
  }

  // Send verification email
  async sendVerificationEmail(email: string, verificationToken: string): Promise<{ success: boolean; error?: string }> {
    const verifyUrl = `${process.env.NEXT_PUBLIC_APP_URL}/verify-email?token=${verificationToken}`;
    
    const htmlContent = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
          <h1 style="margin: 0; font-size: 28px; margin-bottom: 20px;">Verify Your Email ✉️</h1>
          <p style="font-size: 16px; line-height: 1.5; margin: 0 0 20px 0;">
            Please verify your email address to complete your OptikCoin registration.
          </p>
          <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0 0 15px 0; font-size: 14px;">
              Click the button below to verify your email address.
            </p>
            <div style="text-align: center; margin: 20px 0;">
              <a href="${verifyUrl}" style="display: inline-block; background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                Verify Email
              </a>
            </div>
          </div>
          <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
            <p style="font-size: 12px; opacity: 0.8; margin: 0;">
              This verification link will expire in 24 hours.
            </p>
          </div>
        </div>
      </div>
    `;

    return this.sendEmail({
      to: email,
      subject: 'Verify Your OptikCoin Email ✉️',
      html: htmlContent,
      text: `Verify your OptikCoin email here: ${verifyUrl}`,
    });
  }

  // Test email configuration
  async testConfiguration(): Promise<{ success: boolean; error?: string }> {
    try {
      await this.transporter.verify();
      console.log('SMTP configuration is valid');
      return { success: true };
    } catch (error) {
      console.error('SMTP configuration error:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'SMTP configuration failed' 
      };
    }
  }
}

// Export singleton instance
export const emailService = new EmailService();
