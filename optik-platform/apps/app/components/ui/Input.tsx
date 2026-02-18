'use client';
import {forwardRef, InputHTMLAttributes} from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}

const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { className = '', ...props },
  ref
) {
  return (
    <input
      ref={ref}
      className={`w-full rounded-lg border border-white/20 bg-transparent px-3 py-2 text-white placeholder-white/50 focus:border-white/40 focus:outline-none ${className}`}
      {...props}
    />
  );
});

export default Input;
