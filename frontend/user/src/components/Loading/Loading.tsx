interface LoadingProps {
  fullScreen?: boolean;
  text?: string;
}

export default function Loading({ fullScreen, text }: LoadingProps) {
  const spinner = (
    <div className="flex flex-col items-center gap-3">
      <div className="w-10 h-10 border-4 border-accent-soft border-t-accent rounded-full animate-spin" />
      {text && <p className="text-muted text-sm">{text}</p>}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        {spinner}
      </div>
    );
  }

  return <div className="flex items-center justify-center py-12">{spinner}</div>;
}
