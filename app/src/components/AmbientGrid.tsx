import { useEffect, useState } from 'react';

export function AmbientGrid() {
  const [scrolled, setScrolled] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    
    const handleChange = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handleChange);
    
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    
    const handleScroll = () => {
      setScrolled(true);
      clearTimeout(timeout);
      timeout = setTimeout(() => setScrolled(false), 150);
    };

    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
      clearTimeout(timeout);
    };
  }, []);

  return (
    <div 
      className="pointer-events-none fixed inset-0 z-0"
      style={{
        backgroundImage: `
          linear-gradient(to right, hsl(var(--stroke)) 1px, transparent 1px),
          linear-gradient(to bottom, hsl(var(--stroke)) 1px, transparent 1px)
        `,
        backgroundSize: '48px 48px',
        opacity: scrolled && !prefersReducedMotion ? 0.05 : 0.03,
        transition: prefersReducedMotion ? 'none' : 'opacity 260ms cubic-bezier(0.22, 1, 0.36, 1)'
      }}
    />
  );
}
