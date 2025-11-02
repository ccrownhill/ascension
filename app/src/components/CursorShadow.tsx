import { useEffect, useRef, useState } from 'react';

interface CursorShadowProps {
  size?: number;
  intensity?: number;
  softness?: number;
  enabled?: boolean;
}

export function CursorShadow({ 
  size = 280, 
  intensity = 0.08, 
  softness = 0.35,
  enabled = true 
}: CursorShadowProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isTouchDevice, setIsTouchDevice] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const rafRef = useRef<number>();
  const targetPos = useRef({ x: 0, y: 0 });
  const currentPos = useRef({ x: 0, y: 0 });

  useEffect(() => {
    // Check for touch device
    setIsTouchDevice('ontouchstart' in window || navigator.maxTouchPoints > 0);
    
    // Check for reduced motion preference
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    
    const handleChange = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handleChange);
    
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  useEffect(() => {
    if (!enabled || isTouchDevice || prefersReducedMotion) return;

    const handleMouseMove = (e: MouseEvent) => {
      targetPos.current = { x: e.clientX, y: e.clientY };
    };

    const lerp = (start: number, end: number, factor: number) => {
      return start + (end - start) * factor;
    };

    const animate = () => {
      currentPos.current.x = lerp(currentPos.current.x, targetPos.current.x, 0.15);
      currentPos.current.y = lerp(currentPos.current.y, targetPos.current.y, 0.15);
      
      setPosition({ 
        x: Math.round(currentPos.current.x), 
        y: Math.round(currentPos.current.y) 
      });
      
      rafRef.current = requestAnimationFrame(animate);
    };

    window.addEventListener('mousemove', handleMouseMove);
    rafRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [enabled, isTouchDevice, prefersReducedMotion]);

  if (!enabled || isTouchDevice || prefersReducedMotion) return null;

  return (
    <div 
      className="pointer-events-none fixed inset-0 z-50 transition-opacity duration-300"
      style={{ 
        background: `radial-gradient(${size}px circle at ${position.x}px ${position.y}px, hsl(var(--accent) / ${intensity}) 0%, transparent ${softness * 100}%)`,
        mixBlendMode: 'lighten'
      }}
    />
  );
}
