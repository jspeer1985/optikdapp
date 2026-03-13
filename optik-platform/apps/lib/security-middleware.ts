import rateLimit from 'express-rate-limit';
import helmet from 'helmet';
import { NextRequest, NextResponse } from 'next/server';

// Rate limiting configuration
export const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});

// Security headers middleware
export function addSecurityHeaders(response: NextResponse) {
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
  response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  return response;
}

// Input validation utilities
export function validateInput(input: string, maxLength: number = 1000): boolean {
  if (!input || typeof input !== 'string') return false;
  if (input.length > maxLength) return false;
  
  // Basic XSS prevention
  const xssPatterns = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi,
  ];
  
  return !xssPatterns.some(pattern => pattern.test(input));
}

// SQL injection prevention
export function sanitizeSqlInput(input: string): string {
  if (!input) return '';
  
  const sqlPatterns = [
    /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)/gi,
    /(--|\#|\/\*|\*\/|;|'|"|`)/gi,
  ];
  
  let sanitized = input;
  sqlPatterns.forEach(pattern => {
    sanitized = sanitized.replace(pattern, '');
  });
  
  return sanitized.trim();
}

// Request logging for security monitoring
export function logSecurityEvent(event: string, details: any) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    event,
    details,
    ip: details.ip || 'unknown',
    userAgent: details.userAgent || 'unknown',
  };
  
  console.warn('SECURITY_EVENT:', JSON.stringify(logEntry));
  
  // In production, send to monitoring service
  if (process.env.NODE_ENV === 'production' && process.env.SECURITY_WEBHOOK) {
    fetch(process.env.SECURITY_WEBHOOK, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(logEntry),
    }).catch(console.error);
  }
}

// CSP nonce generation
export function generateNonce(): string {
  const array = new Uint8Array(16);
  crypto.getRandomValues(array);
  return Buffer.from(array).toString('base64');
}

// IP-based blocking for suspicious activity
const suspiciousIPs = new Map<string, number>();
const BLOCK_THRESHOLD = 10; // Block after 10 suspicious events

export function shouldBlockIP(ip: string): boolean {
  const attempts = suspiciousIPs.has(ip) ? 
    (suspiciousIPs.get(ip) as number) + 1 : 1;
  
  suspiciousIPs.set(ip, attempts);
  
  if (attempts >= BLOCK_THRESHOLD) {
    logSecurityEvent('IP_BLOCKED', { ip, attempts });
    return true;
  }
  
  return false;
}
