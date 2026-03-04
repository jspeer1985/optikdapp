const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

let refreshPromise: Promise<void> | null = null;

async function refreshSession(): Promise<void> {
  if (!refreshPromise) {
    refreshPromise = fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
    }).then(async (res) => {
      if (!res.ok) {
        throw new Error('Session refresh failed');
      }
    }).finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

export async function api<T = unknown>(endpoint: string, init?: RequestInit): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  const baseHeaders =
    init?.headers instanceof Headers
      ? Object.fromEntries(init.headers.entries())
      : Array.isArray(init?.headers)
        ? Object.fromEntries(init.headers)
        : (init?.headers || {});

  const headers = { ...baseHeaders } as Record<string, string>;
  const hasContentType = Object.keys(headers).some((key) => key.toLowerCase() === 'content-type');
  const isFormData = typeof FormData !== 'undefined' && init?.body instanceof FormData;
  if (!hasContentType && !isFormData) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(url, {
    ...init,
    credentials: 'include',
    headers,
  });

  const authRetryHeader = headers['x-auth-retry'] || headers['X-Auth-Retry'];
  if (res.status === 401 && authRetryHeader !== '1') {
    await refreshSession();
    return api<T>(endpoint, {
      ...init,
      headers: { ...headers, 'x-auth-retry': '1' },
    });
  }

  if (!res.ok) {
    const text = await res.text();
    let detail = text || res.statusText;
    if (text) {
      try {
        const parsed = JSON.parse(text) as { detail?: string; message?: string };
        detail = parsed.detail || parsed.message || text;
      } catch {
        detail = text;
      }
    }
    throw new Error(`API ${res.status}: ${detail}`);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return (await res.json()) as T;
  }
  if (!contentType) {
    return undefined as T;
  }

  return (await res.text()) as T;
}

export interface ConversionResponse {
  success: boolean;
  job_id: string;
  message: string;
  status_endpoint: string;
}

export interface StatusResponse {
  job_id: string;
  status: 'pending' | 'scraping' | 'analyzing' | 'converting' | 'generating_nfts' | 'completed' | 'failed' | 'deployed';
  progress: number;
  message: string;
  dapp_url?: string;
  error?: string;
}

export interface Product {
  id: string;
  name: string;
  description?: string;
  supply: string;
  sold: number;
  price: string;
  status: string;
}

export interface Integration {
  id: string;
  name: string;
  detail: string;
  status: string;
  icon: string;
}

export const optikApi = {
  submitConversion: (data: any) =>
    api<ConversionResponse>('/api/v1/convert/submit', { method: 'POST', body: JSON.stringify(data) }),

  getConversionStatus: (jobId: string) =>
    api<StatusResponse>(`/api/v1/convert/status/${jobId}`),

  startDeployment: (jobId: string) =>
    api<{ success: boolean; message: string }>(`/api/v1/deploy/start/${jobId}`, { method: 'POST' }),

  getAnalytics: (jobId: string) =>
    api<any>(`/api/v1/analytics/${jobId}`),

  // Products
  getProducts: () => api<Product[]>('/api/v1/products/'),
  createProduct: (data: Omit<Product, 'id' | 'sold'>) => api<Product>('/api/v1/products/', { method: 'POST', body: JSON.stringify(data) }),
  updateProduct: (id: string, data: Partial<Product>) => api<any>(`/api/v1/products/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProduct: (id: string) => api<any>(`/api/v1/products/${id}`, { method: 'DELETE' }),

  // Integrations
  getIntegrations: () => api<Integration[]>('/api/v1/integrations/'),
  connectIntegration: (id: string) => api<any>(`/api/v1/integrations/${id}/connect`, { method: 'POST' }),
  disconnectIntegration: (id: string) => api<any>(`/api/v1/integrations/${id}/disconnect`, { method: 'POST' }),

};
