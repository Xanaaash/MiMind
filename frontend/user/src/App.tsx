import { Suspense } from 'react';
import { useRoutes } from 'react-router-dom';
import { routes } from './router';
import Loading from './components/Loading/Loading';
import ToastContainer from './components/Toast/Toast';

export default function App() {
  const element = useRoutes(routes);

  return (
    <>
      <Suspense fallback={<Loading fullScreen />}>
        {element}
      </Suspense>
      <ToastContainer />
    </>
  );
}
