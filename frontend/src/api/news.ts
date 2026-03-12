import { apiRequest } from './client';
import type { NewsResponse, NewsCreate, NewsUpdate, NewsListResponse } from './types';

// Public endpoints (for all authenticated users)

export async function listNews(params?: {
  limit?: number;
  offset?: number;
}): Promise<NewsListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.offset) searchParams.set('offset', String(params.offset));
  
  const query = searchParams.toString();
  return apiRequest<NewsListResponse>(`/news${query ? `?${query}` : ''}`);
}

export async function getNews(newsId: number): Promise<NewsResponse> {
  return apiRequest<NewsResponse>(`/news/${newsId}`);
}

// Admin endpoints

export async function listAllNewsAdmin(params?: {
  limit?: number;
  offset?: number;
}): Promise<NewsListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.offset) searchParams.set('offset', String(params.offset));
  
  const query = searchParams.toString();
  return apiRequest<NewsListResponse>(`/news/admin/all${query ? `?${query}` : ''}`);
}

export async function createNews(body: NewsCreate): Promise<NewsResponse> {
  return apiRequest<NewsResponse>('/news', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function updateNews(newsId: number, body: NewsUpdate): Promise<NewsResponse> {
  return apiRequest<NewsResponse>(`/news/${newsId}`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  });
}

export async function deleteNews(newsId: number): Promise<void> {
  return apiRequest<void>(`/news/${newsId}`, { method: 'DELETE' });
}
