import { Signal, SignalsResponse, NewsResponse } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchSignals(symbols?: string): Promise<SignalsResponse> {
  const params = symbols ? `?symbols=${symbols}` : '';
  const response = await fetch(`${API_URL}/api/signals${params}`, {
    next: { revalidate: 60 },
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch signals');
  }
  
  return response.json();
}

export async function fetchSymbolSignal(symbol: string): Promise<Signal> {
  const response = await fetch(`${API_URL}/api/signals/${symbol}`, {
    next: { revalidate: 30 },
  });
  
  if (!response.ok) {
    throw new Error(`Failed to fetch signal for ${symbol}`);
  }
  
  return response.json();
}

export async function fetchNews(): Promise<NewsResponse> {
  const response = await fetch(`${API_URL}/api/news`, {
    next: { revalidate: 300 },
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch news');
  }
  
  return response.json();
}

export async function triggerScan(symbols?: string): Promise<any> {
  const params = symbols ? `?symbols=${symbols}` : '';
  const response = await fetch(`${API_URL}/api/scan${params}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error('Failed to trigger scan');
  }
  
  return response.json();
}

export async function sendNotification(signal: Signal): Promise<any> {
  const response = await fetch(`${API_URL}/api/notifications/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(signal),
  });
  
  if (!response.ok) {
    throw new Error('Failed to send notification');
  }
  
  return response.json();
}
