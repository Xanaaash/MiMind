import { api } from './client';
import type { ScaleCatalogItem, ScaleScoreResult } from '../types';

export function getCatalog() {
  return api.get<Record<string, ScaleCatalogItem>>('/api/scales/catalog');
}

export function scoreScale(scaleId: string, answers: unknown) {
  return api.post<ScaleScoreResult>('/api/scales/score', {
    scale_id: scaleId,
    answers,
  });
}
