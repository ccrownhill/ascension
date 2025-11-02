import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'text';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', disabled, children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium transition-colors transition-shadow duration-220 focus-ring rounded-lg';
    
    const variants = {
      primary: 'bg-[hsl(var(--text))] text-[hsl(var(--bg))] hover:bg-[hsl(var(--text))]/90 shadow-[0_2px_8px_rgba(232,237,245,0.15)] hover:shadow-[0_4px_12px_rgba(232,237,245,0.25)]',
      secondary: 'panel text-[hsl(var(--text))] hover:bg-[hsl(var(--panel))]/80 hover:border-[hsl(var(--stroke))]/60',
      ghost: 'text-[hsl(var(--text))] hover:bg-[hsl(var(--panel))]',
      text: 'text-[hsl(var(--text))] hover:text-[hsl(var(--accent))] transition-colors duration-220'
    };
    
    const sizes = {
      sm: 'px-4 py-2 text-sm',
      md: 'px-6 py-2.5 text-base',
      lg: 'px-8 py-3 text-lg'
    };
    
    return (
      <button
        ref={ref}
        disabled={disabled}
        className={cn(
          baseStyles,
          variants[variant],
          sizes[size],
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
