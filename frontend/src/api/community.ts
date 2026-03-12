import { apiRequest } from './client';
import type { SuccessPostResponse, SuccessPostCreate, SuccessPostListResponse } from './types';

export async function listSuccessPosts(params?: {
  limit?: number;
  offset?: number;
}): Promise<SuccessPostListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.offset) searchParams.set('offset', String(params.offset));
  
  const query = searchParams.toString();
  return apiRequest<SuccessPostListResponse>(`/community/posts${query ? `?${query}` : ''}`);
}

export async function createSuccessPost(body: SuccessPostCreate): Promise<SuccessPostResponse> {
  return apiRequest<SuccessPostResponse>('/community/posts', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function likePost(postId: number): Promise<SuccessPostResponse> {
  return apiRequest<SuccessPostResponse>(`/community/posts/${postId}/like`, {
    method: 'POST',
  });
}

export async function deleteSuccessPost(postId: number): Promise<void> {
  return apiRequest<void>(`/community/posts/${postId}`, { method: 'DELETE' });
}
