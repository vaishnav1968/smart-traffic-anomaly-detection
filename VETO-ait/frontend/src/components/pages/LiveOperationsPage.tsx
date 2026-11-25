import React, { useState } from 'react';
import { Activity, Search } from 'lucide-react';
import { SecurityEvent } from '../../types';
import { StatusBadge } from '../StatusBadge';

interface LiveOperationsPageProps {
  events: SecurityEvent[];
}

export const LiveOperationsPage: React.FC<LiveOperationsPageProps> = ({ events }) => {
  const [filterDecision, setFilterDecision] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);

  const filtered = events.filter((evt) => {
    const matchesDecision = filterDecision === 'ALL' || evt.decision === filterDecision;
    const matchesSearch =
      evt.operation.toLowerCase().includes(searchTerm.toLowerCase()) ||
      evt.target_resource.toLowerCase().includes(searchTerm.toLowerCase()) ||
      evt.event_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      evt.policy_reason.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesDecision && matchesSearch;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#1e2923]">
        <div>
          <h1 className="text-lg font-mono font-bold text-neutral-100 uppercase tracking-wide flex items-center space-x-2">
            <Activity size={18} className="text-emerald-400" />
            <span>Live Intercepted Operations</span>
          </h1>
          <p className="text-xs font-mono text-neutral-400 mt-0.5">
            Real-time pre-execution gatekeeper event log
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search size={14} className="absolute left-2.5 top-2.5 text-neutral-500" />
            <input
              type="text"
              placeholder="Search resource, op, id..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-[#111714] border border-[#1e2923] pl-8 pr-3 py-1.5 text-xs font-mono text-neutral-200 placeholder-neutral-500 focus:outline-none focus:border-emerald-600"
            />
          </div>

          <div className="flex items-center space-x-1 font-mono text-xs">
            {['ALL', 'ALLOW', 'REVIEW', 'VETO'].map((dec) => (
              <button
                key={dec}
                onClick={() => setFilterDecision(dec)}
                className={`px-2.5 py-1.5 border transition-colors ${
                  filterDecision === dec
                    ? 'bg-emerald-950 border-emerald-600 text-emerald-300 font-bold'
                    : 'bg-[#111714] border-[#1e2923] text-neutral-400 hover:text-white'
                }`}
              >
                {dec}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Events Table */}
      <div className="bg-[#111714] border border-[#1e2923] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="border-b border-[#1e2923] bg-[#0d1210] text-neutral-500 uppercase text-[10px]">
                <th className="py-2.5 px-3">Event ID</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Agent</th>
                <th className="py-2.5 px-3">Operation</th>
                <th className="py-2.5 px-3">Target Resource</th>
                <th className="py-2.5 px-3">Risk</th>
                <th className="py-2.5 px-3">Decision</th>
                <th className="py-2.5 px-3">Outcome</th>
                <th className="py-2.5 px-3 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e2923]">
              {filtered.map((evt) => (
                <tr
                  key={evt.event_id}
                  onClick={() => setSelectedEvent(evt)}
                  className="hover:bg-[#151c18] cursor-pointer transition-colors"
                >
                  <td className="py-2.5 px-3 text-emerald-400 font-semibold">{evt.event_id}</td>
                  <td className="py-2.5 px-3 text-neutral-400">{new Date(evt.timestamp).toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-neutral-300">{evt.agent_id}</td>
                  <td className="py-2.5 px-3 text-neutral-100 font-bold">{evt.operation}</td>
                  <td className="py-2.5 px-3 text-neutral-300 max-w-xs truncate">{evt.target_resource}</td>
                  <td className="py-2.5 px-3">
                    <StatusBadge type="risk" value={evt.risk_level} />
                  </td>
                  <td className="py-2.5 px-3">
                    <StatusBadge type="decision" value={evt.decision} />
                  </td>
                  <td className="py-2.5 px-3">
                    <StatusBadge type="status" value={evt.execution_outcome} />
                  </td>
                  <td className="py-2.5 px-3 text-right text-emerald-500 hover:underline">
                    View
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-neutral-500">
                    No matching operations found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Details Modal / Drawer */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-[#111714] border border-[#1e2923] max-w-2xl w-full p-6 space-y-4 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-[#1e2923] pb-3">
              <div>
                <span className="text-[10px] text-neutral-500 uppercase">Audit Record</span>
                <h3 className="text-base font-bold text-neutral-100">{selectedEvent.event_id}</h3>
              </div>
              <button
                onClick={() => setSelectedEvent(null)}
                className="px-2 py-1 bg-[#1a221d] border border-[#1e2923] text-neutral-400 hover:text-white"
              >
                ESC / Close
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 bg-[#0a0d0c] p-3 border border-[#1e2923]">
              <div>
                <span className="text-neutral-500 text-[10px] uppercase block">Operation</span>
                <span className="text-neutral-200 font-bold">{selectedEvent.operation}</span>
              </div>
              <div>
                <span className="text-neutral-500 text-[10px] uppercase block">Timestamp</span>
                <span className="text-neutral-200">{new Date(selectedEvent.timestamp).toISOString()}</span>
              </div>
              <div>
                <span className="text-neutral-500 text-[10px] uppercase block">Decision</span>
                <StatusBadge type="decision" value={selectedEvent.decision} />
              </div>
              <div>
                <span className="text-neutral-500 text-[10px] uppercase block">Execution Status</span>
                <StatusBadge type="status" value={selectedEvent.execution_outcome} />
              </div>
            </div>

            <div>
              <span className="text-neutral-500 text-[10px] uppercase block mb-1">Target Resource</span>
              <div className="p-2 bg-[#0a0d0c] border border-[#1e2923] text-neutral-200 break-all">
                {selectedEvent.target_resource}
              </div>
            </div>

            <div>
              <span className="text-neutral-500 text-[10px] uppercase block mb-1">Policy Reason</span>
              <div className="p-2 bg-[#0a0d0c] border border-[#1e2923] text-neutral-300">
                {selectedEvent.policy_reason}
              </div>
            </div>

            <div>
              <span className="text-neutral-500 text-[10px] uppercase block mb-1">Parameters (Payload)</span>
              <pre className="p-2 bg-[#0a0d0c] border border-[#1e2923] text-[11px] text-neutral-300 overflow-x-auto max-h-36">
                {JSON.stringify(selectedEvent.parameters, null, 2)}
              </pre>
            </div>

            <div className="space-y-1 text-[10px]">
              <div>
                <span className="text-neutral-500 uppercase">Previous Hash:</span>{' '}
                <span className="text-neutral-400 font-mono">{selectedEvent.previous_hash}</span>
              </div>
              <div>
                <span className="text-neutral-500 uppercase">Event Hash:</span>{' '}
                <span className="text-emerald-400 font-mono">{selectedEvent.event_hash}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
