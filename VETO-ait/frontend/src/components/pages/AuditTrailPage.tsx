import React, { useState } from 'react';
import { FileText, ShieldCheck, AlertCircle } from 'lucide-react';
import { SecurityEvent } from '../../types';
import { api } from '../../services/api';
import { StatusBadge } from '../StatusBadge';

interface AuditTrailPageProps {
  events: SecurityEvent[];
}

export const AuditTrailPage: React.FC<AuditTrailPageProps> = ({ events }) => {
  const [verificationResult, setVerificationResult] = useState<any>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  const handleVerifyChain = async () => {
    setIsVerifying(true);
    try {
      const res = await api.verifyAuditChain();
      setVerificationResult(res);
    } catch (err: any) {
      setVerificationResult({ valid: false, message: `Verification failed: ${err.message}` });
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#1e2923]">
        <div>
          <h1 className="text-lg font-mono font-bold text-neutral-100 uppercase tracking-wide flex items-center space-x-2">
            <FileText size={18} className="text-emerald-400" />
            <span>Tamper-Evident Audit Ledger</span>
          </h1>
          <p className="text-xs font-mono text-neutral-400 mt-0.5">
            Sequential cryptographic SHA-256 hash chaining of all security decisions and execution outcomes
          </p>
        </div>

        <button
          onClick={handleVerifyChain}
          disabled={isVerifying}
          className="px-4 py-2 bg-emerald-950 border border-emerald-600 text-emerald-300 hover:bg-emerald-900 font-mono text-xs font-bold flex items-center space-x-2 transition-colors"
        >
          <ShieldCheck size={16} />
          <span>{isVerifying ? 'Verifying Chain...' : 'Verify Complete Hash Chain'}</span>
        </button>
      </div>

      {/* Verification Result Banner */}
      {verificationResult && (
        <div
          className={`p-4 border font-mono text-xs space-y-1 ${
            verificationResult.valid
              ? 'bg-emerald-950/30 border-emerald-800 text-emerald-300'
              : 'bg-red-950/40 border-red-800 text-red-300'
          }`}
        >
          <div className="font-bold flex items-center space-x-2">
            {verificationResult.valid ? <ShieldCheck size={16} /> : <AlertCircle size={16} />}
            <span>
              {verificationResult.valid
                ? `LEDGER INTEGRITY VERIFIED (Events Checked: ${verificationResult.total_events})`
                : 'SECURITY ALERT: HASH CHAIN INTEGRITY VIOLATION DETECTED'}
            </span>
          </div>
          <div className="text-[11px] text-neutral-300">{verificationResult.message}</div>
          {verificationResult.head_hash && (
            <div className="text-[10px] text-neutral-400 break-all">
              Head Block Hash: {verificationResult.head_hash}
            </div>
          )}
        </div>
      )}

      {/* Audit Events Log */}
      <div className="bg-[#111714] border border-[#1e2923]">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="border-b border-[#1e2923] bg-[#0d1210] text-neutral-500 uppercase text-[10px]">
                <th className="py-2.5 px-3">Event ID</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Operation</th>
                <th className="py-2.5 px-3">Decision</th>
                <th className="py-2.5 px-3">Outcome</th>
                <th className="py-2.5 px-3">Previous Hash (Link)</th>
                <th className="py-2.5 px-3">Event Hash (SHA-256)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e2923]">
              {events.map((evt) => (
                <tr key={evt.event_id} className="hover:bg-[#151c18]">
                  <td className="py-2.5 px-3 text-emerald-400 font-semibold">{evt.event_id}</td>
                  <td className="py-2.5 px-3 text-neutral-400">{new Date(evt.timestamp).toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-neutral-200 font-bold">{evt.operation}</td>
                  <td className="py-2.5 px-3">
                    <StatusBadge type="decision" value={evt.decision} />
                  </td>
                  <td className="py-2.5 px-3">
                    <StatusBadge type="status" value={evt.execution_outcome} />
                  </td>
                  <td className="py-2.5 px-3 text-neutral-500 text-[10px] font-mono">
                    {evt.previous_hash.slice(0, 16)}...
                  </td>
                  <td className="py-2.5 px-3 text-emerald-500 text-[10px] font-mono">
                    {evt.event_hash.slice(0, 16)}...
                  </td>
                </tr>
              ))}
              {events.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-10 text-center text-neutral-500">
                    Audit ledger is currently empty.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
