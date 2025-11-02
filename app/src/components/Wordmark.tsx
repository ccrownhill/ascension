import { FocusReveal } from './FocusReveal';

export function Wordmark() {
  return (
    <FocusReveal>
      <h1
        className="font-display font-bold text-[hsl(var(--text))] tracking-[0.02em] leading-none"
        style={{
          fontSize: 'clamp(44px, 7vw, 88px)'
        }}
      >
        FASTTRACK
      </h1>
    </FocusReveal>
  );
}
