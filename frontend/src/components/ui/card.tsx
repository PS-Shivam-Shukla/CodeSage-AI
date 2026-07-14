import type { HTMLAttributes } from 'react';
import { cn } from '@/utils/cn';

type CardProps = HTMLAttributes<HTMLDivElement>;

export function Card({ className, ...props }: CardProps) {
  return <div className={cn('rounded-3xl border border-white/10 bg-white/10 backdrop-blur-xl shadow-soft', className)} {...props} />;
}

export function CardContent({ className, ...props }: CardProps) {
  return <div className={cn('p-6', className)} {...props} />;
}
