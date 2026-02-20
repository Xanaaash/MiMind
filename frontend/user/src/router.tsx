import { lazy } from 'react';
import type { RouteObject } from 'react-router-dom';
import AppLayout from './components/Layout/AppLayout';

const Landing = lazy(() => import('./pages/Landing/Landing'));
const Auth = lazy(() => import('./pages/Auth/Auth'));
const Onboarding = lazy(() => import('./pages/Onboarding/Onboarding'));
const Home = lazy(() => import('./pages/Home/Home'));
const ScaleCenter = lazy(() => import('./pages/Scales/ScaleCenter'));
const ScaleQuiz = lazy(() => import('./pages/Scales/ScaleQuiz'));
const ScaleResult = lazy(() => import('./pages/Scales/ScaleResult'));
const TestCenter = lazy(() => import('./pages/Tests/TestCenter'));
const TestQuiz = lazy(() => import('./pages/Tests/TestQuiz'));
const TestResult = lazy(() => import('./pages/Tests/TestResult'));
const CoachPage = lazy(() => import('./pages/Coach/CoachPage'));
const CoachHistoryPage = lazy(() => import('./pages/Coach/CoachHistoryPage'));
const ToolsHub = lazy(() => import('./pages/Tools/ToolsHub'));
const BreathingExercise = lazy(() => import('./pages/Tools/BreathingExercise'));
const SensoryRelief = lazy(() => import('./pages/Tools/SensoryRelief'));
const MeditationPlayer = lazy(() => import('./pages/Tools/MeditationPlayer'));
const JournalPage = lazy(() => import('./pages/Journal/JournalPage'));
const BillingPage = lazy(() => import('./pages/Billing/BillingPage'));
const ProfilePage = lazy(() => import('./pages/Profile/ProfilePage'));
const SafetyPage = lazy(() => import('./pages/Landing/SafetyPage'));
const PrivacyPage = lazy(() => import('./pages/Legal/PrivacyPage'));
const TermsPage = lazy(() => import('./pages/Legal/TermsPage'));
const NotFoundPage = lazy(() => import('./pages/Error/NotFoundPage'));

export const routes: RouteObject[] = [
  { path: '/', element: <Landing /> },
  { path: '/auth', element: <Auth /> },
  { path: '/privacy', element: <PrivacyPage /> },
  { path: '/terms', element: <TermsPage /> },
  { path: '/onboarding', element: <Onboarding /> },
  { path: '/safety', element: <SafetyPage /> },
  {
    element: <AppLayout />,
    children: [
      { path: '/home', element: <Home /> },
      { path: '/scales', element: <ScaleCenter /> },
      { path: '/scales/:scaleId', element: <ScaleQuiz /> },
      { path: '/scales/:scaleId/result', element: <ScaleResult /> },
      { path: '/tests', element: <TestCenter /> },
      { path: '/tests/:testId', element: <TestQuiz /> },
      { path: '/tests/:testId/result', element: <TestResult /> },
      { path: '/coach', element: <CoachPage /> },
      { path: '/coach/history', element: <CoachHistoryPage /> },
      { path: '/tools', element: <ToolsHub /> },
      { path: '/tools/breathing', element: <BreathingExercise /> },
      { path: '/tools/sensory-relief', element: <SensoryRelief /> },
      { path: '/tools/meditation', element: <MeditationPlayer /> },
      { path: '/journal', element: <JournalPage /> },
      { path: '/billing', element: <BillingPage /> },
      { path: '/profile', element: <ProfilePage /> },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
];
