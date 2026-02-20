import { Component, type ErrorInfo, type ReactNode } from 'react';

type BoundaryKind = 'runtime' | 'server' | 'network';

type State = {
  hasError: boolean;
  kind: BoundaryKind;
  message: string;
};

type Props = {
  children: ReactNode;
};

function classify(reason: unknown): State {
  const status = typeof reason === 'object' && reason !== null && 'status' in reason
    ? Number((reason as { status?: unknown }).status)
    : null;
  const message = reason instanceof Error ? reason.message : String(reason ?? 'Unknown error');
  const normalized = message.toLowerCase();

  if (status !== null && status >= 500) {
    return { hasError: true, kind: 'server', message };
  }

  if (
    normalized.includes('failed to fetch')
    || normalized.includes('networkerror')
    || normalized.includes('network request failed')
    || normalized.includes('load failed')
  ) {
    return { hasError: true, kind: 'network', message };
  }

  return { hasError: true, kind: 'runtime', message };
}

function titleByKind(kind: BoundaryKind): string {
  if (kind === 'server') return '服务暂时不可用 / Service unavailable';
  if (kind === 'network') return '网络连接异常 / Network issue';
  return '页面出现错误 / Something went wrong';
}

function hintByKind(kind: BoundaryKind): string {
  if (kind === 'server') {
    return '服务器可能正在维护，请稍后重试。';
  }
  if (kind === 'network') {
    return '请检查网络后重试。若问题持续，可稍后重新打开应用。';
  }
  return '应用遇到未预期错误，刷新后通常可恢复。';
}

export default class GlobalErrorBoundary extends Component<Props, State> {
  state: State = {
    hasError: false,
    kind: 'runtime',
    message: '',
  };

  static getDerivedStateFromError(error: Error): State {
    return classify(error);
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Keep lightweight diagnostics for debugging without exposing stack to users.
    console.error('GlobalErrorBoundary', error, errorInfo);
  }

  componentDidMount() {
    window.addEventListener('unhandledrejection', this.handleUnhandledRejection);
  }

  componentWillUnmount() {
    window.removeEventListener('unhandledrejection', this.handleUnhandledRejection);
  }

  handleUnhandledRejection = (event: PromiseRejectionEvent) => {
    this.setState(classify(event.reason));
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.assign('/home');
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div className="min-h-screen flex items-center justify-center px-4 py-10">
        <div className="w-full max-w-lg bg-panel border border-line rounded-3xl shadow-lg p-8 text-center">
          <div className="w-14 h-14 rounded-2xl bg-danger-soft text-danger text-3xl flex items-center justify-center mx-auto">
            !
          </div>
          <h1 className="font-heading text-2xl font-bold mt-5">{titleByKind(this.state.kind)}</h1>
          <p className="text-muted mt-2">{hintByKind(this.state.kind)}</p>

          <div className="grid sm:grid-cols-2 gap-3 mt-7">
            <button
              type="button"
              onClick={this.handleReload}
              className="px-4 py-3 rounded-xl bg-accent text-white font-semibold hover:opacity-95 transition-opacity"
            >
              刷新页面 / Reload
            </button>
            <button
              type="button"
              onClick={this.handleGoHome}
              className="px-4 py-3 rounded-xl border border-line bg-paper text-ink font-semibold hover:bg-cream transition-colors"
            >
              返回首页 / Home
            </button>
          </div>

          {this.state.message ? (
            <p className="text-xs text-muted mt-6 break-all">
              Error: {this.state.message}
            </p>
          ) : null}
        </div>
      </div>
    );
  }
}
