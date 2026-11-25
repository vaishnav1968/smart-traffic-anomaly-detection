import React, { useState } from 'react';
import { CheckCircle, XCircle, Clock, Cpu } from 'lucide-react';
import { ApprovalRequest } from '../../types';
import { api } from '../../services/api';

interface ApprovalCenterPageProps {
  approvals: ApprovalRequest[];
  onRefresh: () => void;
}

export const ApprovalCenterPage: React.FC<ApprovalCenterPageProps> = ({ approvals, onRefresh }) => {
  const [processingId, setProcessingId] = useState<string | null>(null);

  const pendingList = approvals.filter((a) => a.status === 'PENDING');
  const resolvedList = approvals.filter((a) => a.status !== 'PENDING');

  const handleApprove = async (id: string) => {
    setProcessingId(id);
    try {
      await api.approveRequest(id);
      onRefresh();
    } catch (err: any) {
      alert(`Approval error: ${err.message}`);
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (id: string) => {
    setProcessingId(id);
    try {
      await api.rejectRequest(id);
      onRefresh();
    } catch (err: any) {
      alert(`Rejection error: ${err.message}`);
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-[#1e2923]">
        <h1 className="text-lg font-mono font-bold text-neutral-100 uppercase tracking-wide flex items-center space-x-2">
          <CheckCircle size={18} className="text-amber-400" />
          <span>Human-in-the-Loop Approval Center</span>
        </h1>
        <p className="text-xs font-mono text-neutral-400 mt-0.5">
          Dual-interface authorization: Physical Arduino buttons or dashboard verification
        </p>
      </div>

      {/* Active Pending Approvals Queue */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-amber-400 flex items-center space-x-2">
            <Clock size={14} />
            <span>Pending Authorization Requests ({pendingList.length})</span>
          </h2>
          <span className="text-[11px] font-mono text-neutral-500">
            Hardware LED: Yellow | OLED Active
          </span>
        </div>

        {pendingList.length === 0 ? (
          <div className="bg-[#111714] border border-[#1e2923] p-8 text-center font-mono text-xs text-neutral-500">
            No sensitive operations currently waiting for human approval.
            <div className="text-[11px] text-neutral-600 mt-1">
              Trigger a file deletion or run Demo 3 to generate a review request.
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {pendingList.map((req) => (
              <div
                key={req.id}
                className="bg-[#111714] border-2 border-amber-800/80 p-5 space-y-4 font-mono text-xs shadow-lg shadow-amber-950/20"
              >
                <div className="flex items-center justify-between pb-3 border-b border-[#1e2923]">
                  <div>
                    <span className="text-[10px] text-neutral-500 uppercase">Approval ID</span>
                    <div className="text-sm font-bold text-amber-400">{req.id}</div>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-neutral-500 uppercase">Expires At</span>
                    <div className="text-neutral-300">{new Date(req.expires_at).toLocaleTimeString()}</div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div>
                    <span className="text-[10px] text-neutral-500 uppercase block">Operation Type</span>
                    <span className="text-neutral-100 font-bold text-sm">{req.operation}</span>
                  </div>

                  <div>
                    <span className="text-[10px] text-neutral-500 uppercase block">Target Resource</span>
                    <div className="p-2 bg-[#0a0d0c] border border-[#1e2923] text-neutral-200 break-all">
                      {req.target_resource}
                    </div>
                  </div>

                  <div>
                    <span className="text-[10px] text-neutral-500 uppercase block">Cryptographic Action Hash</span>
                    <div className="text-[10px] text-neutral-400 break-all font-mono">
                      {req.action_hash}
                    </div>
                  </div>
                </div>

                {/* Control Action Buttons */}
                <div className="pt-3 border-t border-[#1e2923] flex items-center justify-between gap-3">
                  <div className="flex items-center space-x-1.5 text-[10px] text-neutral-400">
                    <Cpu size={14} className="text-amber-400" />
                    <span>Or use physical Arduino buttons</span>
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleReject(req.id)}
                      disabled={processingId === req.id}
                      className="px-4 py-2 bg-red-950 border border-red-700 text-red-300 hover:bg-red-900 font-bold flex items-center space-x-1 transition-colors"
                    >
                      <XCircle size={14} />
                      <span>REJECT</span>
                    </button>
                    <button
                      onClick={() => handleApprove(req.id)}
                      disabled={processingId === req.id}
                      className="px-4 py-2 bg-emerald-950 border border-emerald-600 text-emerald-300 hover:bg-emerald-900 font-bold flex items-center space-x-1 transition-colors"
                    >
                      <CheckCircle size={14} />
                      <span>APPROVE</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Resolved Approvals History */}
      <div className="bg-[#111714] border border-[#1e2923] p-5 space-y-3">
        <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-neutral-400">
          Authorization History ({resolvedList.length})
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="border-b border-[#1e2923] text-neutral-500 uppercase text-[10px]">
                <th className="py-2 px-3">ID</th>
                <th className="py-2 px-3">Requested At</th>
                <th className="py-2 px-3">Operation</th>
                <th className="py-2 px-3">Target Resource</th>
                <th className="py-2 px-3">Status</th>
                <th className="py-2 px-3">Resolved By</th>
                <th className="py-2 px-3">Resolved At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e2923]">
              {resolvedList.map((apr) => (
                <tr key={apr.id} className="hover:bg-[#151c18]">
                  <td className="py-2 px-3 text-neutral-300 font-semibold">{apr.id}</td>
                  <td className="py-2 px-3 text-neutral-400">{new Date(apr.created_at).toLocaleTimeString()}</td>
                  <td className="py-2 px-3 text-neutral-200">{apr.operation}</td>
                  <td className="py-2 px-3 text-neutral-300 max-w-xs truncate">{apr.target_resource}</td>
                  <td className="py-2 px-3">
                    <span
                      className={`px-2 py-0.5 text-xs font-mono border rounded ${
                        apr.status === 'APPROVED'
                          ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
                          : 'bg-red-950 text-red-400 border-red-800'
                      }`}
                    >
                      {apr.status}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-neutral-400">{apr.resolved_by || 'SYSTEM'}</td>
                  <td className="py-2 px-3 text-neutral-400">
                    {apr.resolved_at ? new Date(apr.resolved_at).toLocaleTimeString() : 'N/A'}
                  </td>
                </tr>
              ))}
              {resolvedList.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-6 text-center text-neutral-500">
                    No historical approvals recorded yet.
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
