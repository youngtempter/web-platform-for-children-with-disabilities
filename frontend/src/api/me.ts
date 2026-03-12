import { apiRequest } from './client';
import type { UserResponse, UserUpdate, UserAchievementStats, StudyFriendsListResponse, PasswordChange } from './types';

export async function getMe(): Promise<UserResponse> {
  return apiRequest<UserResponse>('/me');
}

export async function updateMe(body: UserUpdate): Promise<UserResponse> {
  return apiRequest<UserResponse>('/me', {
    method: 'PATCH',
    body: JSON.stringify(body),
  });
}

export async function changePassword(body: PasswordChange): Promise<{ message: string }> {
  return apiRequest<{ message: string }>('/me/password', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function getMyAchievements(): Promise<UserAchievementStats> {
  return apiRequest<UserAchievementStats>('/me/achievements');
}

export async function getStudyFriends(): Promise<StudyFriendsListResponse> {
  return apiRequest<StudyFriendsListResponse>('/me/study-friends');
}
