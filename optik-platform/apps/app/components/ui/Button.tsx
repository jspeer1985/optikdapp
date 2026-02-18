'use client';
import { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  className = '',
  disabled,
  ...props
}: ButtonProps) {
  const baseStyles = 'font-semibold rounded-lg transition-all disabled:opacity-50 inline-flex items-center justify-center';

  const variants = {
    primary: 'bg-primary text-primary-foreground hover:opacity-90 shadow-lg shadow-primary/20',
    secondary: 'bg-white/10 text-white border border-white/20 hover:bg-white/20',
    danger: 'bg-red-500 text-white hover:bg-red-600',
    ghost: 'bg-transparent text-white hover:bg-white/10',
    outline: 'bg-transparent text-white border-2 border-primary hover:bg-primary/5'
  } as const;

  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-6 py-3',
    lg: 'px-8 py-4 text-lg',
    xl: 'px-12 py-5 text-xl'

  } as const;

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          Loading...
        </div>
      ) : children}
    </button>
  );
}
