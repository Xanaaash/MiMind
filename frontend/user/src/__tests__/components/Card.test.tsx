import React from "react";
import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import Card from '../../components/Card/Card';

describe('Card', () => {
  it('renders content', () => {
    render(<Card>Card body</Card>);
    expect(screen.getByText('Card body')).toBeInTheDocument();
  });

  it('becomes keyboard accessible when hoverable and clickable', () => {
    const handleClick = vi.fn();
    render(
      <Card hoverable onClick={handleClick}>
        Interactive card
      </Card>
    );

    const element = screen.getByRole('button', { name: 'Interactive card' });
    expect(element).toHaveAttribute('tabindex', '0');

    fireEvent.keyDown(element, { key: 'Enter' });
    fireEvent.keyDown(element, { key: ' ' });
    expect(handleClick).toHaveBeenCalledTimes(2);
  });

  it('is not interactive without onClick', () => {
    render(<Card hoverable>Static card</Card>);
    expect(screen.queryByRole('button', { name: 'Static card' })).not.toBeInTheDocument();
  });
});
