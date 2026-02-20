import React from "react";
import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import Modal from '../../components/Modal/Modal';

describe('Modal', () => {
  it('does not render when closed', () => {
    render(
      <Modal open={false} title="Dialog">
        Hidden content
      </Modal>
    );
    expect(screen.queryByText('Dialog')).not.toBeInTheDocument();
  });

  it('renders title and content when open, and restores body overflow when closed', () => {
    const { rerender, unmount } = render(
      <Modal open title="Dialog">
        Visible content
      </Modal>
    );
    expect(screen.getByText('Dialog')).toBeInTheDocument();
    expect(document.body.style.overflow).toBe('hidden');

    rerender(
      <Modal open={false} title="Dialog">
        Visible content
      </Modal>
    );
    expect(document.body.style.overflow).toBe('');

    unmount();
    expect(document.body.style.overflow).toBe('');
  });

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn();
    render(
      <Modal open title="Dialog" onClose={onClose}>
        Content
      </Modal>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Close' }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('hides close affordance when closable is false', () => {
    const onClose = vi.fn();
    const { container } = render(
      <Modal open title="Dialog" onClose={onClose} closable={false}>
        Content
      </Modal>
    );

    expect(screen.queryByRole('button', { name: 'Close' })).not.toBeInTheDocument();

    const overlay = container.querySelector('.bg-overlay');
    expect(overlay).toBeInTheDocument();
    fireEvent.click(overlay!);
    expect(onClose).not.toHaveBeenCalled();
  });
});
