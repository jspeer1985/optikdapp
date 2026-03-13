import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // Check environment variables
    const envChecks = {
      SMTP_HOST: !!process.env.SMTP_HOST,
      SMTP_USER: !!process.env.SMTP_USER,
      SMTP_PASSWORD: !!process.env.SMTP_PASSWORD,
      REDIS_PASSWORD: !!process.env.REDIS_PASSWORD,
      SOLANA_TREASURY_WALLET: !!process.env.SOLANA_TREASURY_WALLET,
      NEXT_PUBLIC_SOLANA_NETWORK: !!process.env.NEXT_PUBLIC_SOLANA_NETWORK,
    };

    const allEnvSet = Object.values(envChecks).every(Boolean);

    // Check database connections (basic check)
    const services = {
      frontend: true,
      email_service: allEnvSet,
      env_variables: envChecks,
    };

    const healthData = {
      status: allEnvSet ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      services,
      version: '1.0.0',
      uptime: process.uptime(),
      memory: {
        used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
        total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024),
      },
    };

    return NextResponse.json(healthData, {
      status: allEnvSet ? 200 : 503,
    });

  } catch (error) {
    console.error('Health check error:', error);
    return NextResponse.json(
      {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: 'Health check failed',
      },
      { status: 503 }
    );
  }
}
