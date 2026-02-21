import { lazy } from 'react';
import type { RouteObject } from 'react-router-dom';
import { Navigate } from 'react-router-dom';
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
const ReliefHub = lazy(() => import('./pages/Relief/ReliefHub'));
const MindfulnessHub = lazy(() => import('./pages/Mindfulness/MindfulnessHub'));
const ManifestationPage = lazy(() => import('./pages/Mindfulness/ManifestationPage'));
const BreathingExercise = lazy(() => import('./pages/Relief/BreathingExercise'));
const SensoryRelief = lazy(() => import('./pages/Relief/SensoryRelief'));
const PomodoroTimer = lazy(() => import('./pages/Tools/PomodoroTimer'));
const MeditationPlayer = lazy(() => import('./pages/Tools/MeditationPlayer'));
const JournalPage = lazy(() => import('./pages/Journal/JournalPage'));
const BillingPage = lazy(() => import('./pages/Billing/BillingPage'));
const ProfilePage = lazy(() => import('./pages/Profile/ProfilePage'));
const SafetyPage = lazy(() => import('./pages/Landing/SafetyPage'));
const PrivacyPage = lazy(() => import('./pages/Legal/PrivacyPage'));
const TermsPage = lazy(() => import('./pages/Legal/TermsPage'));
const NeuroHub = lazy(() => import('./pages/Neurodiversity/NeuroHub'));
const NeuroQuiz = lazy(() => import('./pages/Neurodiversity/NeuroQuiz'));
const NeuroResult = lazy(() => import('./pages/Neurodiversity/NeuroResult'));
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
      { path: '/relief', element: <ReliefHub /> },
      { path: '/relief/breathing', element: <BreathingExercise /> },
      { path: '/relief/sensory', element: <SensoryRelief /> },
      { path: '/mindfulness', element: <MindfulnessHub /> },
      { path: '/mindfulness/meditation', element: <MeditationPlayer /> },
      { path: '/mindfulness/manifestation', element: <ManifestationPage /> },
      { path: '/tools', element: <Navigate to="/relief" replace /> },
      { path: '/tools/breathing', element: <Navigate to="/relief/breathing" replace /> },
      { path: '/tools/sensory-relief', element: <Navigate to="/relief/sensory" replace /> },
      { path: '/tools/pomodoro', element: <PomodoroTimer /> },
      { path: '/tools/meditation', element: <Navigate to="/mindfulness/meditation" replace /> },
      { path: '/neurodiversity', element: <NeuroHub /> },
      { path: '/neurodiversity/:scaleId', element: <NeuroQuiz /> },
      { path: '/neurodiversity/:scaleId/result', element: <NeuroResult /> },
      { path: '/journal', element: <JournalPage /> },
      { path: '/billing', element: <BillingPage /> },
      { path: '/profile', element: <ProfilePage /> },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
];
