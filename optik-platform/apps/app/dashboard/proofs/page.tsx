'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface ProofRecord {
  id: string;
  job_id?: string;
  workflow_id?: string;
  step_id?: string;
  status?: string;
  owner_agent?: string;
  created_at?: string;
  details?: Record<string, any>;
}

export default function ProofDashboard() {
  const [proofs, setProofs] = useState<ProofRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const response = await api<{ proofs: ProofRecord[] }>('/api/v1/system/proofs');
        if (mounted) setProofs(response.proofs || []);
      } catch (err: any) {
        if (mounted) setError(err.message || 'Failed to load proofs.');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="pb-20 px-8 py-10">
      <div className="max-w-6xl mx-auto space-y-10">
        <div>
          <h1 className="text-4xl font-black text-white">Proof Ledger</h1>
          <p className="text-gray-400">Completion evidence for every pipeline step.</p>
        </div>

        {error && <p className="text-red-400">{error}</p>}

        <div className="glass p-8 rounded-[3rem] border-white/5">
          {loading ? (
            <p className="text-gray-500">Loading proofs...</p>
          ) : proofs.length === 0 ? (
            <p className="text-gray-500">No proofs recorded yet.</p>
          ) : (
            <div className="space-y-4">
              {proofs.map((proof) => (
                <div key={proof.id} className="rounded-2xl border border-white/10 bg-white/5 p-5">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                    <div>
                      <p className="text-xs text-gray-500 uppercase">{proof.workflow_id || 'workflow'}</p>
                      <h3 className="text-lg font-bold text-white">{proof.step_id || 'step'}</h3>
                      <p className="text-xs text-gray-500">Job: {proof.job_id || '—'}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-emerald-400">{(proof.status || 'completed').toUpperCase()}</p>
                      <p className="text-xs text-gray-500">{proof.owner_agent || 'system'}</p>
                      <p className="text-xs text-gray-500">{proof.created_at ? new Date(proof.created_at).toLocaleString() : '—'}</p>
                    </div>
                  </div>
                  {proof.details && Object.keys(proof.details).length > 0 && (
                    <div className="mt-3 text-xs text-gray-400">
                      {Object.entries(proof.details).slice(0, 4).map(([key, value]) => (
                        <div key={key}>{key}: {String(value)}</div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
