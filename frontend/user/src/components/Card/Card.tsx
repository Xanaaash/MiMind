import { type ReactNode, type HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  hoverable?: boolean;
  padding?: 'sm' | 'md' | 'lg';
}

const paddingClasses = {
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export default function Card({
  children,
  hoverable,
  padding = 'md',
  className = '',
  onClick,
  onKeyDown,
  role,
  tabIndex,
  ...rest
}: CardProps) {
  const interactive = hoverable && typeof onClick === 'function';

  const handleKeyDown: HTMLAttributes<HTMLDivElement>['onKeyDown'] = (event) => {
    onKeyDown?.(event);
    if (event.defaultPrevented) return;
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      event.currentTarget.click();
    }
  };

  return (
    <div
      className={`
        bg-panel border border-line rounded-2xl shadow-sm
        ${hoverable ? 'hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 cursor-pointer' : ''}
        ${paddingClasses[padding]}
        ${className}
      `}
      onClick={onClick}
      role={interactive ? role ?? 'button' : role}
      tabIndex={interactive ? tabIndex ?? 0 : tabIndex}
      onKeyDown={interactive ? handleKeyDown : onKeyDown}
      {...rest}
    >
      {children}
    </div>
  );
}
