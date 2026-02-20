import { api } from './client';
import type { BillingEntitlements, BillingPlan, SubscriptionRecord } from '../types';

export function getPlans() {
  return api.get<BillingPlan[]>('/api/billing/plans');
}

export function startTrial(userId: string) {
  return api.post<SubscriptionRecord>(`/api/billing/${userId}/trial/start`);
}

export function checkout(userId: string, planId: string) {
  return api.post<SubscriptionRecord>(`/api/billing/${userId}/checkout`, { plan_id: planId });
}

export function getSubscription(userId: string) {
  return api.get<SubscriptionRecord>(`/api/billing/${userId}/subscription`);
}

export function getEntitlements(userId: string) {
  return api.get<BillingEntitlements>(`/api/billing/${userId}/entitlements`);
}
