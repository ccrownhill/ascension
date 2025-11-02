import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ToastProps {
  message: string;
  duration?: number;
  onClose: () => void;
}

export function Toast({ message, duration = 3000, onClose }: ToastProps) {
  const [visible, setVisible] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
  }, []);

  useEffect(() => {
    // Show toast
    requestAnimationFrame(() => setVisible(true));

    // Auto dismiss
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onClose, prefersReducedMotion ? 0 : 220);
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose, prefersReducedMotion]);

  return createPortal(
    <div
      className={cn(
        'fixed bottom-8 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3',
        'panel px-6 py-3 min-w-[300px] max-w-[500px]',
        'transition-all duration-220',
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      )}
    >
      <p className="flex-1 text-[hsl(var(--text))] text-sm">{message}</p>
      <button
        onClick={() => {
          setVisible(false);
          setTimeout(onClose, prefersReducedMotion ? 0 : 220);
        }}
        className="text-[hsl(var(--muted))] hover:text-[hsl(var(--text))] transition-colors focus-ring rounded"
        aria-label="Close notification"
      >
        <X size={16} />
      </button>
    </div>,
    document.body
  );
}

// Toast manager hook
export function useToast() {
  const [toasts, setToasts] = useState<Array<{ id: string; message: string }>>([]);

  const showToast = (message: string) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { id, message }]);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  const ToastContainer = () => (
    <>
      {toasts.map(toast => (
        <Toast
          key={toast.id}
          message={toast.message}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </>
  );

  return { showToast, ToastContainer };
}
