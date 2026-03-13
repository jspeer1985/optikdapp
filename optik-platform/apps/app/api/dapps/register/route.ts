import { NextRequest, NextResponse } from 'next/server';
import { isAddress } from '../../../lib/validation';

function getAuthToken(request: NextRequest): string | null {
  const authHeader = request.headers.get('authorization');
  if (authHeader?.startsWith('Bearer ')) {
    return authHeader.slice(7);
  }
  return null;
}

function isAuthenticated(request: NextRequest): boolean {
  // Accept a valid Bearer token or an active session cookie
  const token = getAuthToken(request);
  if (token) {
    const internalKey = process.env.INTERNAL_API_KEY;
    if (internalKey && token === internalKey) return true;
  }
  // Cookie-based session (set by the backend auth flow)
  const sessionCookie = request.cookies.get('session_token') || request.cookies.get('access_token');
  return !!sessionCookie?.value;
}

export async function POST(request: NextRequest) {
  if (!isAuthenticated(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const { name, walletAddress } = body;

    if (!name || typeof name !== 'string' || name.trim().length === 0) {
      return NextResponse.json({ error: 'Invalid or missing field: name' }, { status: 400 });
    }
    if (name.length > 100) {
      return NextResponse.json({ error: 'name exceeds maximum length of 100 characters' }, { status: 400 });
    }

    if (!walletAddress || typeof walletAddress !== 'string') {
      return NextResponse.json({ error: 'Invalid or missing field: walletAddress' }, { status: 400 });
    }
    try {
      isAddress(walletAddress);
    } catch {
      return NextResponse.json({ error: 'Invalid wallet address format' }, { status: 400 });
    }

    const dappId = `dapp_${crypto.randomUUID()}`;

    return NextResponse.json({
      success: true,
      dappId,
      message: 'Dapp registered successfully',
      data: { id: dappId, name: name.trim(), walletAddress, createdAt: new Date() },
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({ dapps: [] });
}
