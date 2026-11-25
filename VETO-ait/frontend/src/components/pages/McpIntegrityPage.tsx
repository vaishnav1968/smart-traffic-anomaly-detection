import React, { useState } from 'react';
import { KeyRound } from 'lucide-react';
import { McpTool } from '../../types';
import { api } from '../../services/api';
import { StatusBadge } from '../StatusBadge';

interface McpIntegrityPageProps {
  tools: McpTool[];
  onRefresh: () => void;
}

export const McpIntegrityPage: React.FC<McpIntegrityPageProps> = ({ tools, onRefresh }) => {
  const [processingTool, setProcessingTool] = useState<string | null>(null);

  const handleSimulateTamper = async (toolName: string) => {
    setProcessingTool(toolName);
    try {
      await api.tamperMcpTool(toolName);
      onRefresh();
    } catch (err: any) {
      alert(`Error tampering tool: ${err.message}`);
    } finally {
      setProcessingTool(null);
    }
  };

  const handleApproveFingerprint = async (toolName: string) => {
    setProcessingTool(toolName);
    try {
      await api.approveMcpFingerprint(toolName);
      onRefresh();
    } catch (err: any) {
      alert(`Error approving fingerprint: ${err.message}`);
    } finally {
      setProcessingTool(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-[#1e2923]">
        <h1 className="text-lg font-mono font-bold text-neutral-100 uppercase tracking-wide flex items-center space-x-2">
          <KeyRound size={18} className="text-emerald-400" />
          <span>MCP Tool Integrity Verification</span>
        </h1>
        <p className="text-xs font-mono text-neutral-400 mt-0.5">
          SHA-256 cryptographic canonical fingerprinting of Model Context Protocol tool metadata & capabilities
        </p>
      </div>

      <div className="bg-[#111714] border border-[#1e2923] p-5">
        <div className="flex items-center justify-between pb-3 border-b border-[#1e2923] mb-4">
          <span className="text-xs font-mono uppercase text-neutral-400">Registered MCP Catalog ({tools.length})</span>
          <span className="text-xs font-mono text-neutral-500">Algorithm: SHA-256 Canonical JSON</span>
        </div>

        <div className="space-y-4">
          {tools.map((tool) => {
            const isTampered = tool.status === 'TAMPERED';
            return (
              <div
                key={tool.name}
                className={`p-4 border font-mono text-xs space-y-3 transition-colors ${
                  isTampered
                    ? 'bg-red-950/20 border-red-800'
                    : 'bg-[#0a0d0c] border-[#1e2923]'
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-bold text-neutral-100">{tool.name}</span>
                    <span className="text-neutral-500 text-[10px]">v{tool.version}</span>
                    <StatusBadge type="mcp" value={tool.status} />
                  </div>

                  <div className="flex items-center space-x-2">
                    {isTampered ? (
                      <button
                        onClick={() => handleApproveFingerprint(tool.name)}
                        disabled={processingTool === tool.name}
                        className="px-3 py-1 bg-emerald-950 border border-emerald-700 text-emerald-300 hover:bg-emerald-900 text-xs font-bold transition-colors"
                      >
                        Re-Approve Baseline
                      </button>
                    ) : (
                      <button
                        onClick={() => handleSimulateTamper(tool.name)}
                        disabled={processingTool === tool.name}
                        className="px-3 py-1 bg-red-950/60 border border-red-800 text-red-300 hover:bg-red-900 text-xs font-bold transition-colors"
                      >
                        Simulate Tampering
                      </button>
                    )}
                  </div>
                </div>

                <div className="text-neutral-300 text-xs">{tool.description}</div>

                {/* Capabilities */}
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  <span className="text-neutral-500 text-[10px] uppercase">Declared Capabilities:</span>
                  {tool.capabilities.map((cap) => (
                    <span
                      key={cap}
                      className={`px-1.5 py-0.5 text-[10px] border ${
                        cap.includes('arbitrary')
                          ? 'bg-red-900/60 text-red-200 border-red-700 font-bold'
                          : 'bg-[#151c18] text-neutral-300 border-[#1e2923]'
                      }`}
                    >
                      {cap}
                    </span>
                  ))}
                </div>

                {/* Fingerprints */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 pt-2 border-t border-[#1e2923]/60 text-[11px]">
                  <div>
                    <span className="text-neutral-500 uppercase text-[9px] block">Approved Baseline SHA-256</span>
                    <div className="text-neutral-300 break-all">{tool.approved_fingerprint}</div>
                  </div>
                  <div>
                    <span className="text-neutral-500 uppercase text-[9px] block">Current Computed SHA-256</span>
                    <div className={`break-all ${isTampered ? 'text-red-400 font-bold' : 'text-emerald-400'}`}>
                      {tool.current_fingerprint}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
