import { api } from './client';
import type { PairingReport, TestCatalogItem, TestResult } from '../types';

export function getCatalog() {
  return api.get<Record<string, TestCatalogItem>>('/api/tests/catalog');
}

export function getTestDetail(testId: string) {
  return api.get<TestCatalogItem>(`/api/tests/catalog/${testId}`);
}

export function submitTest(userId: string, testId: string, answers: Record<string, number>) {
  return api.post<TestResult>(`/api/tests/${userId}/submit`, {
    test_id: testId,
    answers,
  });
}

export function getReport(userId: string, resultId: string) {
  return api.get<TestResult>(`/api/tests/${userId}/report/${resultId}`);
}

export function shareResult(userId: string, resultId: string) {
  return api.post<{ share_url: string }>(`/api/tests/${userId}/share/${resultId}`);
}

export function getPairingReport(leftResultId: string, rightResultId: string) {
  return api.post<PairingReport>('/api/tests/pairing', {
    left_result_id: leftResultId,
    right_result_id: rightResultId,
  });
}
