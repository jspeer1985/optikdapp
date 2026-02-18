'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

type ModelMode = {
  id: string;
  label: string;
  model: string;
};

type ModelResponse = {
  provider: string;
  default_mode: string;
  modes: ModelMode[];
};

export default function ModelsPage() {
  const [data, setData] = useState<ModelResponse | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const response = await api<ModelResponse>('/api/v1/assistant/models');
        if (!mounted) return;
        setData(response);
        const stored = window.localStorage.getItem('optik_model_mode');
        setSelected(stored || response.default_mode || 'balanced');
      } catch (err: any) {
        if (mounted) setError(err.message || 'Failed to load model options.');
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const handleSelect = (modeId: string) => {
    setSelected(modeId);
    window.localStorage.setItem('optik_model_mode', modeId);
    setStatus(`Model preference set to ${modeId.toUpperCase()}.`);
    setTimeout(() => setStatus(null), 4000);
  };

  return (
    <div className="min-h-screen bg-black text-white pt-28 pb-20">
      <div className="max-w-6xl mx-auto px-6 space-y-10">
        <div>
          <h1 className="text-4xl font-black">Optik Model Control</h1>
          <p className="text-gray-400 mt-2">
            Select the assistant mode you want: faster responses or maximum accuracy.
          </p>
        </div>

        {error && <p className="text-red-400">{error}</p>}
        {status && <p className="text-emerald-400">{status}</p>}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {(data?.modes || []).map((mode) => (
            <button
              key={mode.id}
              onClick={() => handleSelect(mode.id)}
              className={`text-left rounded-3xl border p-6 transition-all ${
                selected === mode.id
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-white/10 bg-white/5 hover:bg-white/10'
              }`}
            >
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold">{mode.label}</h2>
                {selected === mode.id && (
                  <span className="text-[10px] font-black uppercase text-blue-300">Active</span>
                )}
              </div>
              <p className="text-xs text-gray-400 mt-3">Provider: {data?.provider || 'unknown'}</p>
              <p className="text-xs text-gray-500 mt-1">Model: {mode.model}</p>
              <div className="mt-6 text-xs text-gray-400">
                {mode.id === 'fast' && 'Lowest latency. Best for quick checks and routing.'}
                {mode.id === 'balanced' && 'Recommended default for daily operations.'}
                {mode.id === 'accurate' && 'Highest accuracy for critical decisions.'}
              </div>
            </button>
          ))}
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 text-sm text-gray-400">
          <p>
            Current selection is stored locally in this browser and sent with every OptikGPT request.
            If you need global enforcement, set the default in the backend env variables.
          </p>
        </div>
      </div>
    </div>
  );
}
