import { api } from './client';
import type { ProfessionalScaleLibraryItem, ScaleCatalogItem, ScaleScoreResult } from '../types';

export function getCatalog() {
  return api.get<Record<string, ScaleCatalogItem>>('/api/scales/catalog');
}

export function getProfessionalLibrary() {
  return api.get<Record<string, ProfessionalScaleLibraryItem>>('/api/scales/professional-library');
}

export function scoreScale(scaleId: string, answers: unknown) {
  return api.post<ScaleScoreResult>('/api/scales/score', {
    scale_id: scaleId,
    answers,
  });
}
