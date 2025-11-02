import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          'w-full px-4 py-2.5 rounded-lg',
          'bg-[hsl(var(--panel))] border border-[hsl(var(--stroke))]',
          'text-[hsl(var(--text))] placeholder:text-[hsl(var(--muted))]',
          'transition-colors duration-220 focus-ring',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          error && 'border-[hsl(var(--destructive))] focus:ring-[hsl(var(--destructive))]/40',
          className
        )}
        {...props}
      />
    );
  }
);

Input.displayName = 'Input';
