import React, { useState } from 'react';
import { AlertTriangle, ShieldX, Globe, Key, FileWarning } from 'lucide-react';
import { ThreatIncident } from '../../types';
import { StatusBadge } from '../StatusBadge';

interface ThreatDetectionPageProps {
  threats: ThreatIncident[];
}

export const ThreatDetectionPage: React.FC<ThreatDetectionPageProps> = ({ threats }) => {
  const [selectedThreat, setSelectedThreat] = useState<ThreatIncident | null>(null);

  const getThreatIcon = (type: string) => {
    if (type.includes('HONEYTOKEN')) return <FileWarning size={16} className="text-red-400" />;
    if (type.includes('EGRESS')) return <Globe size={16} className="text-red-400" />;
    if (type.includes('MCP')) return <Key size={16} className="text-red-400" />;
    return <ShieldX size={16} className="text-red-400" />;
  };

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-[#1e2923]">
        <h1 className="text-lg font-mono font-bold text-neutral-100 uppercase tracking-wide flex items-center space-x-2">
          <AlertTriangle size={18} className="text-red-400" />
          <span>Threat Detection & Forensic Incidents</span>
        </h1>
        <p className="text-xs font-mono text-neutral-400 mt-0.5">
          Automated interception of decoy honeytoken access, network exfiltration, and tool tampering
        </p>
      </div>

      {/* Threats Table */}
      <div className="bg-[#111714] border border-[#1e2923]">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="border-b border-[#1e2923] bg-[#0d1210] text-neutral-500 uppercase text-[10px]">
                <th className="py-2.5 px-3">Incident ID</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Threat Vector</th>
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-3">Enforcement</th>
                <th className="py-2.5 px-3">Description</th>
                <th className="py-2.5 px-3 text-right">Forensics</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e2923]">
              {threats.map((th) => (
                <tr
                  key={th.id}
                  onClick={() => setSelectedThreat(th)}
                  className="hover:bg-[#151c18] cursor-pointer transition-colors"
                >
                  <td className="py-2.5 px-3 text-red-400 font-semibold">{th.id}</td>
                  <td className="py-2.5 px-3 text-neutral-400">{new Date(th.timestamp).toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-neutral-200 flex items-center space-x-2">
                    {getThreatIcon(th.threat_type)}
                    <span>{th.threat_type}</span>
                  </td>
                  <td className="py-2.5 px-3">
                    <StatusBadge type="risk" value={th.severity} />
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="px-2 py-0.5 text-xs font-mono bg-red-950/80 text-red-300 border border-red-800 font-bold">
                      {th.blocked ? 'BLOCKED' : 'DETECTED'}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-neutral-300 max-w-sm truncate">{th.description}</td>
                  <td className="py-2.5 px-3 text-right text-emerald-400 hover:underline">
                    Inspect
                  </td>
                </tr>
              ))}
              {threats.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-neutral-500">
                    No threat incidents recorded. Run Demo 1 or Demo 2 to simulate adversarial attacks.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Forensic Details Modal */}
      {selectedThreat && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-[#111714] border border-red-900/60 max-w-xl w-full p-6 space-y-4 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-[#1e2923] pb-3">
              <div>
                <span className="text-[10px] text-red-400 uppercase font-bold">Security Incident Dossier</span>
                <h3 className="text-base font-bold text-neutral-100">{selectedThreat.id}</h3>
              </div>
              <button
                onClick={() => setSelectedThreat(null)}
                className="px-2 py-1 bg-[#1a221d] border border-[#1e2923] text-neutral-400 hover:text-white"
              >
                Close
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 bg-[#0a0d0c] p-3 border border-[#1e2923]">
              <div>
                <span className="text-neutral-500 text-[10px] uppercase block">Threat Vector</span>
                <span className="text-neutral-200 font-bold">{selectedThreat.threat_type}</span>
              </div>
              <div>
                <span className="text-neutral-500 text-[10px] uppercase block">Enforcement Status</span>
                <span className="text-red-400 font-bold">100% PREVENTED (BLOCKED)</span>
              </div>
              <div>
                <span className="text-neutral-500 text-[10px] uppercase block">Severity</span>
                <StatusBadge type="risk" value={selectedThreat.severity} />
              </div>
              <div>
                <span className="text-neutral-500 text-[10px] uppercase block">Timestamp</span>
                <span className="text-neutral-200">{new Date(selectedThreat.timestamp).toISOString()}</span>
              </div>
            </div>

            <div>
              <span className="text-neutral-500 text-[10px] uppercase block mb-1">Incident Summary</span>
              <div className="p-2.5 bg-[#0a0d0c] border border-[#1e2923] text-neutral-300">
                {selectedThreat.description}
              </div>
            </div>

            <div>
              <span className="text-neutral-500 text-[10px] uppercase block mb-1">Forensic Details</span>
              <pre className="p-2.5 bg-[#0a0d0c] border border-[#1e2923] text-[11px] text-neutral-300 overflow-x-auto max-h-48">
                {JSON.stringify(selectedThreat.details, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
