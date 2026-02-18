'use client';
import { ReactNode } from 'react';

export default function Card({
  children,
  className = '',
  onClick
}: {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className={`glass-card p-6 rounded-[2rem] ${className}`}
    >
      {children}
    </div>
  );
}

