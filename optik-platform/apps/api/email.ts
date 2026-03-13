import { NextRequest, NextResponse } from 'next/server';
import { emailService } from '../lib/email-service';

function isAuthenticated(request: NextRequest): boolean {
  const authHeader = request.headers.get('authorization');
  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.slice(7);
    const internalKey = process.env.INTERNAL_API_KEY;
    if (internalKey && token === internalKey) return true;
  }
  const sessionCookie = request.cookies.get('session_token') || request.cookies.get('access_token');
  return !!sessionCookie?.value;
}

export async function POST(request: NextRequest) {
  if (!isAuthenticated(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const { type, to, subject, text, html, from } = body;

    if (!type || !to || !subject) {
      return NextResponse.json(
        { error: 'Missing required fields: type, to, subject' },
        { status: 400 }
      );
    }

    let result;
    switch (type) {
      case 'welcome':
        if (!body.name) {
          return NextResponse.json(
            { error: 'Missing name field for welcome email' },
            { status: 400 }
          );
        }
        result = await emailService.sendWelcomeEmail(to, body.name);
        break;

      case 'password-reset':
        if (!body.resetToken) {
          return NextResponse.json(
            { error: 'Missing resetToken field for password reset' },
            { status: 400 }
          );
        }
        result = await emailService.sendPasswordResetEmail(to, body.resetToken);
        break;

      case 'verification':
        if (!body.verificationToken) {
          return NextResponse.json(
            { error: 'Missing verificationToken field for email verification' },
            { status: 400 }
          );
        }
        result = await emailService.sendVerificationEmail(to, body.verificationToken);
        break;

      case 'custom':
        result = await emailService.sendEmail({ to, subject, text, html, from });
        break;

      default:
        return NextResponse.json({ error: 'Invalid email type' }, { status: 400 });
    }

    if (result.success) {
      return NextResponse.json(
        { message: 'Email sent successfully', messageId: `email_${crypto.randomUUID()}` },
        { status: 200 }
      );
    } else {
      return NextResponse.json(
        { error: result.error || 'Failed to send email' },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Email API error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// Config health check — authenticated only, no secret values exposed
export async function GET(request: NextRequest) {
  if (!isAuthenticated(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const result = await emailService.testConfiguration();
    return NextResponse.json(
      {
        status: result.success ? 'ok' : 'error',
        timestamp: new Date().toISOString(),
      },
      { status: result.success ? 200 : 500 }
    );
  } catch (error) {
    console.error('Email test error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
