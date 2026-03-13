'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';

type JobSummary = {
  id: string;
  status: string;
  store_url?: string;
  platform?: string;
  progress?: number;
  updated_at?: string;
};

type SystemStatus = {
  active_jobs: number;
  queued_jobs: number;
  failed_jobs: number;
};

type ProofRecord = {
  id: string;
  job_id?: string;
  workflow_id?: string;
  step_id?: string;
  status?: string;
  owner_agent?: string;
  created_at?: string;
  details?: Record<string, unknown>;
};

export default function OrchestratorPage() {
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [proofs, setProofs] = useState<ProofRecord[]>([]);
  const [proofLoading, setProofLoading] = useState(false);
  const [proofError, setProofError] = useState<string | null>(null);
  const [selectedJob, setSelectedJob] = useState<string>('all');

  useEffect(() => {
    let mounted = true;
    const loadData = async () => {
      try {
        const [statusRes, jobsRes] = await Promise.all([
          api<SystemStatus>('/api/v1/system/status'),
          api<{ jobs: JobSummary[] }>('/api/v1/convert'),
        ]);
        if (mounted) {
          setStatus(statusRes);
          setJobs(jobsRes.jobs || []);
        }
      } catch (err: unknown) {
        if (mounted) setError(err instanceof Error ? err.message : 'Failed to load orchestrator status.');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    loadData();
    const interval = setInterval(loadData, 15000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    let mounted = true;
    const loadProofs = async () => {
      setProofLoading(true);
      setProofError(null);
      try {
        const query = selectedJob !== 'all' ? `job_id=${selectedJob}` : '';
        const endpoint = query ? `/api/v1/system/proofs?${query}` : '/api/v1/system/proofs';
        const response = await api<{ proofs: ProofRecord[] }>(endpoint);
        if (mounted) setProofs(response.proofs || []);
      } catch (err: unknown) {
        if (mounted) setProofError(err instanceof Error ? err.message : 'Failed to load proofs.');
      } finally {
        if (mounted) setProofLoading(false);
      }
    };
    loadProofs();
    return () => {
      mounted = false;
    };
  }, [selectedJob]);

  return (
    <div className="min-h-screen pt-24 pb-20 px-8">
      <div className="max-w-7xl mx-auto space-y-12">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-black text-white mb-2">Agent <span className="gradient-text">Orchestrator</span></h1>
            <p className="text-gray-400">Live view of conversion and deployment workloads.</p>
          </div>
          <Link href="/create-dapp" className="text-blue-400 font-bold">Launch new conversion →</Link>
        </div>

        {error && <p className="text-red-400">{error}</p>}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass p-6 rounded-2xl border border-white/10">
            <p className="text-xs text-gray-500 uppercase font-bold">Active Jobs</p>
            <p className="text-3xl font-black text-white mt-2">{status?.active_jobs ?? '—'}</p>
          </div>
          <div className="glass p-6 rounded-2xl border border-white/10">
            <p className="text-xs text-gray-500 uppercase font-bold">Queued Jobs</p>
            <p className="text-3xl font-black text-white mt-2">{status?.queued_jobs ?? '—'}</p>
          </div>
          <div className="glass p-6 rounded-2xl border border-white/10">
            <p className="text-xs text-gray-500 uppercase font-bold">Failed Jobs</p>
            <p className="text-3xl font-black text-white mt-2">{status?.failed_jobs ?? '—'}</p>
          </div>
        </div>

        <div className="glass p-8 rounded-[3rem] border-white/5">
          <h2 className="text-2xl font-bold mb-6 text-white">Recent Jobs</h2>
          {loading ? (
            <p className="text-gray-500">Loading jobs...</p>
          ) : jobs.length === 0 ? (
            <p className="text-gray-500">No jobs submitted yet.</p>
          ) : (
            <div className="space-y-4">
              {jobs.map((job) => (
                <div key={job.id} className="flex flex-col md:flex-row md:items-center md:justify-between p-4 bg-white/5 rounded-2xl border border-white/5">
                  <div>
                    <p className="text-xs text-gray-500 uppercase">{job.platform || 'store'}</p>
                    <p className="text-lg font-bold text-white">{job.store_url || job.id}</p>
                    <p className="text-xs text-gray-500">Updated {job.updated_at ? new Date(job.updated_at).toLocaleString() : '—'}</p>
                  </div>
                  <div className="mt-4 md:mt-0 text-right">
                    <p className="text-sm font-bold text-emerald-400">{job.status}</p>
                    <p className="text-xs text-gray-500">{job.progress ?? 0}% complete</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="glass p-8 rounded-[3rem] border-white/5 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white">Proof of Completion</h2>
              <p className="text-gray-500 text-sm">Audit trail for each workflow step.</p>
            </div>
            <select
              value={selectedJob}
              onChange={(e) => setSelectedJob(e.target.value)}
              className="bg-black/30 border border-white/10 rounded-xl px-4 py-2 text-sm text-white"
            >
              <option value="all">All Jobs</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.store_url || job.id}
                </option>
              ))}
            </select>
          </div>

          {proofError && <p className="text-red-400">{proofError}</p>}

          {proofLoading ? (
            <p className="text-gray-500">Loading proofs...</p>
          ) : proofs.length === 0 ? (
            <p className="text-gray-500">No proofs recorded yet.</p>
          ) : (
            <div className="space-y-4">
              {proofs.map((proof) => (
                <div key={proof.id} className="p-4 rounded-2xl border border-white/10 bg-white/5">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                    <div>
                      <p className="text-xs text-gray-500 uppercase">{proof.workflow_id || 'workflow'}</p>
                      <p className="text-lg font-bold text-white">{proof.step_id || 'step'}</p>
                      <p className="text-xs text-gray-500">
                        {proof.created_at ? new Date(proof.created_at).toLocaleString() : '—'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-emerald-400">{(proof.status || 'completed').toUpperCase()}</p>
                      <p className="text-xs text-gray-500">{proof.owner_agent || 'system'}</p>
                    </div>
                  </div>
                  {proof.details && Object.keys(proof.details).length > 0 && (
                    <div className="mt-3 text-xs text-gray-400">
                      {Object.entries(proof.details).slice(0, 3).map(([key, value]) => (
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
