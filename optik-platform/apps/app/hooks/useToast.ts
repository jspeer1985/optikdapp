'use client';
import { useCallback, useState } from 'react';

type Toast = { id: string; message: string; type?: 'info' | 'success' | 'error' };

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const remove = useCallback((id: string) => {
    setToasts((t) => t.filter((x) => x.id !== id));
  }, []);

  const push = useCallback((message: string, type: Toast['type'] = 'info') => {
    const id = Math.random().toString(36).slice(2);
    setToasts((t) => [...t, { id, message, type }]);
    setTimeout(() => remove(id), 4000);
  }, [remove]);

  return { toasts, push, remove };
}
