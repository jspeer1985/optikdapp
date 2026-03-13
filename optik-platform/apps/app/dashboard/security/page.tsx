'use client';

import React, { useEffect, useState } from 'react';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';

type SecurityEvent = {
  id: string;
  message: string;
  created_at?: string;
};

export default function SecurityControl() {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [whitelist, setWhitelist] = useState<string[]>([]);
  const [newIp, setNewIp] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const loadSecurity = async () => {
      try {
        const [eventsRes, whitelistRes] = await Promise.all([
          api<{ events: SecurityEvent[] }>('/api/v1/security/events'),
          api<{ ips: string[] }>('/api/v1/security/whitelist'),
        ]);
        if (mounted) {
          setEvents(eventsRes.events || []);
          setWhitelist(whitelistRes.ips || []);
        }
      } catch (err: unknown) {
        if (mounted) setError(err instanceof Error ? err.message : 'Failed to load security data.');
      }
    };
    loadSecurity();
    return () => {
      mounted = false;
    };
  }, []);

  const handleAddIp = async () => {
    if (!newIp.trim()) {
      setError('Enter a valid IP address.');
      return;
    }
    setError(null);
    try {
      await api('/api/v1/security/whitelist', {
        method: 'POST',
        body: JSON.stringify({ ip: newIp.trim() }),
      });
      setWhitelist([...whitelist, newIp.trim()]);
      setNewIp('');
      setStatus('IP added to whitelist.');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to add IP.');
    }
  };

  const handleFreeze = async () => {
    if (!confirm('Freeze storefront operations?')) return;
    setError(null);
    try {
      await api('/api/v1/security/freeze', { method: 'POST' });
      setStatus('Freeze request submitted.');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to submit freeze request.');
    }
  };

  return (
    <div className="pb-20 px-8 py-10">
      <div className="max-w-7xl mx-auto space-y-12">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-black text-white mb-2">Security <span className="gradient-text">Protocol</span></h1>
            <p className="text-gray-400">Monitor security events and manage access controls.</p>
          </div>
        </div>

        {status && (
          <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-4 text-emerald-200 text-sm">
            {status}
          </div>
        )}
        {error && (
          <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-200 text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <section className="glass p-10 rounded-[3rem] border-red-500/20 relative overflow-hidden">
              <h2 className="text-2xl font-bold mb-6">Security Events</h2>
              <div className="space-y-4">
                {events.length === 0 ? (
                  <p className="text-gray-500 text-sm">No security events recorded.</p>
                ) : (
                  events.map((event) => (
                    <div key={event.id} className="p-6 bg-white/5 border border-white/5 rounded-2xl flex items-center justify-between">
                      <div>
                        <p className="text-white font-bold">{event.message}</p>
                        <p className="text-gray-500 text-xs">{event.created_at ? new Date(event.created_at).toLocaleString() : '—'}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="glass p-8 rounded-3xl border-white/5">
                <h3 className="font-bold mb-4">Merchant IP Whitelist</h3>
                <div className="space-y-2 mb-6">
                  {whitelist.length === 0 ? (
                    <p className="text-xs text-gray-500">No IPs whitelisted.</p>
                  ) : (
                    whitelist.map((ip) => (
                      <div key={ip} className="text-xs font-mono text-gray-500 bg-white/5 p-2 rounded">{ip}</div>
                    ))
                  )}
                </div>
                <div className="flex gap-2">
                  <input
                    value={newIp}
                    onChange={(e) => setNewIp(e.target.value)}
                    placeholder="IP address"
                    className="flex-1 bg-black/20 border border-white/10 rounded-xl px-3 py-2 text-white text-xs focus:outline-none focus:border-blue-500"
                  />
                  <Button size="sm" variant="outline" onClick={handleAddIp}>Add</Button>
                </div>
              </div>
              <div className="glass p-8 rounded-3xl border-white/5">
                <h3 className="font-bold mb-4">Emergency Controls</h3>
                <p className="text-gray-500 text-xs mb-6">Freeze storefront activity in response to security incidents.</p>
                <Button size="sm" className="w-full bg-red-600 hover:bg-red-700" onClick={handleFreeze}>Freeze Store</Button>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <section className="glass p-8 rounded-[2.5rem] border-blue-500/20">
              <h3 className="text-xl font-bold mb-6">Security Posture</h3>
              <div className="space-y-4 text-sm text-gray-400">
                <div className="flex justify-between">
                  <span>Rate limiting</span>
                  <span className="text-emerald-400 font-bold">Enabled</span>
                </div>
                <div className="flex justify-between">
                  <span>Session monitoring</span>
                  <span className="text-emerald-400 font-bold">Active</span>
                </div>
                <div className="flex justify-between">
                  <span>Webhook verification</span>
                  <span className="text-emerald-400 font-bold">Active</span>
                </div>
              </div>
            </section>
          </div>
        </div>

      </div>
    </div>
  );
}
