import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    if (!body.name || !body.walletAddress) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    const dappId = `dapp_${Date.now()}`;
    
    return NextResponse.json({
      success: true,
      dappId,
      message: 'Dapp registered successfully',
      data: { ...body, id: dappId, createdAt: new Date() }
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({ dapps: [] });
}
