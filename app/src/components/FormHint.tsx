import { cn } from '@/lib/utils';

interface FormHintProps {
  children: React.ReactNode;
  error?: boolean;
  id?: string;
  className?: string;
}

export function FormHint({ children, error, id, className }: FormHintProps) {
  return (
    <p
      id={id}
      className={cn(
        'text-sm',
        error ? 'text-[hsl(var(--destructive))]' : 'text-[hsl(var(--text))]/70',
        className
      )}
    >
      {children}
    </p>
  );
}
