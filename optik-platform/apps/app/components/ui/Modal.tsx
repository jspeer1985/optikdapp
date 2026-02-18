'use client';
import {ReactNode} from 'react';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
}

export default function Modal({ open, onClose, title, children }: ModalProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="w-full max-w-lg rounded-xl border border-white/10 bg-gray-900 p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          {title ? <h3 className="text-lg font-semibold text-white">{title}</h3> : <div />}
          <button onClick={onClose} className="text-white/70 hover:text-white">✕</button>
        </div>
        <div className="text-white">{children}</div>
      </div>
    </div>
  );
}
