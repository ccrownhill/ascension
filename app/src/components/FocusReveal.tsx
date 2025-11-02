import { useEffect, useState, ReactNode } from 'react';

interface FocusRevealProps {
  children: ReactNode;
  duration?: number;
}

export function FocusReveal({ children, duration = 600 }: FocusRevealProps) {
  const [revealed, setRevealed] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    
    const handleChange = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handleChange);
    
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  useEffect(() => {
    // Reveal after a small delay to ensure smooth animation
    const timer = setTimeout(() => setRevealed(true), 50);
    return () => clearTimeout(timer);
  }, []);

  if (prefersReducedMotion) {
    return <div className="opacity-0 animate-in fade-in duration-300">{children}</div>;
  }

  return (
    <div 
      className="relative overflow-hidden"
      style={{
        WebkitMaskImage: revealed 
          ? 'linear-gradient(to right, black 100%, transparent 100%)'
          : 'linear-gradient(to right, black 0%, transparent 0%)',
        maskImage: revealed
          ? 'linear-gradient(to right, black 100%, transparent 100%)'
          : 'linear-gradient(to right, black 0%, transparent 0%)',
        transition: `all ${duration}ms cubic-bezier(0.22, 1, 0.36, 1)`
      }}
    >
      {children}
    </div>
  );
}
