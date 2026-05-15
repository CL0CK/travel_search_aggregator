import type { TripRead, SearchAIResponse, SearchParams, ExtractionParams } from '../types/trip';

const BASE = '';

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || res.statusText);
  }
  return res.json();
}

export async function searchTrips(params: SearchParams): Promise<TripRead[]> {
  const qs = new URLSearchParams({
    destination: params.destination,
    origin: params.origin,
    check_in: params.check_in,
    check_out: params.check_out,
    mock: 'false',
  });
  if (params.max_price !== undefined) qs.set('max_price', String(params.max_price));
  if (params.hotel_stars !== undefined) qs.set('hotel_stars', String(params.hotel_stars));
  return request<TripRead[]>(`/search?${qs.toString()}`);
}

export async function extractParams(query: string, accumulated?: Partial<ExtractionParams>): Promise<ExtractionParams> {
  return request<ExtractionParams>('/extract', {
    method: 'POST',
    body: JSON.stringify({ query, accumulated }),
  });
}

export async function searchTripsAI(query: string): Promise<SearchAIResponse> {
  return request<SearchAIResponse>('/search_ai', {
    method: 'POST',
    body: JSON.stringify({ query, mock: false }),
  });
}
