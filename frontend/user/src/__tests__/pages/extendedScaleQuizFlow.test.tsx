import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

import ScaleQuiz from '../../pages/Scales/ScaleQuiz';
import { getCatalog, scoreScale } from '../../api/scales';
import { useAuthStore } from '../../stores/auth';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, options?: { defaultValue?: string }) => options?.defaultValue ?? key,
    i18n: { language: 'en-US' },
  }),
}));

vi.mock('../../api/scales', () => ({
  getCatalog: vi.fn(),
  scoreScale: vi.fn(),
}));

describe('extended scale submission flow', () => {
  beforeEach(() => {
    vi.mocked(getCatalog).mockReset();
    vi.mocked(scoreScale).mockReset();
    useAuthStore.setState({
      userId: 'u-scale-flow',
      email: 'scale-flow@example.com',
      locale: 'en-US',
      channel: 'GREEN',
      isAuthenticated: true,
      isLoading: false,
      isInitialized: true,
    });
  });

  it('submits isi7 answers and navigates to result route', async () => {
    vi.mocked(getCatalog).mockResolvedValue({
      isi7: {
        display_name: 'Insomnia Severity Index (ISI-7)',
        item_count: 2,
        question_bank: {
          answer_labels: {
            'en-US': ['Never', 'Sometimes', 'Often'],
            'zh-CN': ['从不', '有时', '经常'],
          },
          questions: [
            {
              question_id: 'q1',
              text: { 'en-US': 'Difficulty falling asleep', 'zh-CN': '入睡困难' },
            },
            {
              question_id: 'q2',
              text: { 'en-US': 'Difficulty staying asleep', 'zh-CN': '维持睡眠困难' },
            },
          ],
        },
      },
    });
    vi.mocked(scoreScale).mockResolvedValue({
      scale_id: 'isi7',
      score: 3,
      severity: 'subthreshold',
    });

    render(
      <MemoryRouter initialEntries={['/scales/isi7']}>
        <Routes>
          <Route path="/scales/:scaleId" element={<ScaleQuiz />} />
          <Route path="/scales/:scaleId/result" element={<div>result-page</div>} />
        </Routes>
      </MemoryRouter>,
    );

    await screen.findByText(/Difficulty falling asleep/);
    fireEvent.click(screen.getByRole('button', { name: /Never/ }));
    fireEvent.click(screen.getByRole('button', { name: 'scales.next' }));

    await screen.findByText(/Difficulty staying asleep/);
    fireEvent.click(screen.getByRole('button', { name: /Sometimes/ }));
    fireEvent.click(screen.getByRole('button', { name: 'scales.submit' }));

    await waitFor(() => expect(scoreScale).toHaveBeenCalledWith('isi7', [0, 1]));
    await screen.findByText('result-page');
  });
});
