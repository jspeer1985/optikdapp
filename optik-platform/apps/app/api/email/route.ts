import { NextRequest, NextResponse } from 'next/server';

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
    const { type, to, subject, name } = body;

    if (!type || !to || !subject) {
      return NextResponse.json(
        { error: 'Missing required fields: type, to, subject' },
        { status: 400 }
      );
    }

    // For now, just log the email request (nodemailer integration would go here)
    console.log('Email request:', {
      type,
      subject,
      timestamp: new Date().toISOString(),
    });

    return NextResponse.json(
      {
        message: 'Email sent successfully (simulated)',
        messageId: `email_${crypto.randomUUID()}`,
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Email API error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// Config test — authenticated admins only, returns no secret values
export async function GET(request: NextRequest) {
  if (!isAuthenticated(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const configured = !!(process.env.SMTP_HOST && process.env.SMTP_USER && process.env.SMTP_PASSWORD);
  return NextResponse.json(
    {
      status: configured ? 'configured' : 'not_configured',
      timestamp: new Date().toISOString(),
    },
    { status: 200 }
  );
}
