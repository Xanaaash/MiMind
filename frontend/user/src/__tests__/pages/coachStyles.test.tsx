import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import CoachPage, { COACH_STYLES } from '../../pages/Coach/CoachPage';
import { useAuthStore } from '../../stores/auth';
import { useCoachStore } from '../../stores/coach';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

describe('CoachPage styles', () => {
  beforeEach(() => {
    useAuthStore.setState({
      userId: 'u-coach-style',
      email: 'coach@example.com',
      locale: 'en-US',
      channel: 'GREEN',
      isAuthenticated: true,
      isLoading: false,
      isInitialized: true,
    });
    useCoachStore.getState().reset();
    localStorage.setItem('mc_assessment_ts', String(Date.now()));
  });

  it('exposes five coaching styles including deep, mindful, and action', () => {
    expect(COACH_STYLES.map((style) => style.id)).toEqual([
      'warm_guide',
      'rational_analysis',
      'deep_exploration',
      'mindfulness_guide',
      'action_coach',
    ]);
  });

  it('renders five style options on coach entry screen', () => {
    render(
      <MemoryRouter>
        <CoachPage />
      </MemoryRouter>,
    );

    COACH_STYLES.forEach((style) => {
      expect(screen.getByText(style.nameKey)).toBeInTheDocument();
      expect(screen.getByText(style.descKey)).toBeInTheDocument();
    });
  });
});
