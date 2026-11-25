import React, { useState } from 'react';
import { PlaySquare, Play } from 'lucide-react';
import { DemoResult } from '../../types';
import { api } from '../../services/api';
import { StatusBadge } from '../StatusBadge';

interface DemoScenariosPageProps {
  onRefresh: () => void;
}

export const DemoScenariosPage: React.FC<DemoScenariosPageProps> = ({ onRefresh }) => {
  const [runningDemo, setRunningDemo] = useState<string | null>(null);
  const [demoResults, setDemoResults] = useState<Record<string, DemoResult>>({});

  const handleRun = async (scenario: string) => {
    setRunningDemo(scenario);
    try {
      const res = await api.runDemo(scenario, true);
      setDemoResults((prev) => ({ ...prev, [scenario]: res }));
      onRefresh();
    } catch (err: any) {
      alert(`Demo error: ${err.message}`);
    } finally {
      setRunningDemo(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-[#1e2923]">
        <h1 className="text-lg font-mono font-bold text-neutral-100 uppercase tracking-wide flex items-center space-x-2">
          <PlaySquare size={18} className="text-emerald-400" />
          <span>Reproducible Demonstration Scenarios</span>
        </h1>
        <p className="text-xs font-mono text-neutral-400 mt-0.5">
          Execute the three mandatory live adversarial scenarios with genuine enforcement mechanisms
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Scenario 1: Prompt Injection & Honeytokens */}
        <div className="bg-[#111714] border border-[#1e2923] p-5 space-y-4 font-mono text-xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-[#1e2923] gap-2">
            <div>
              <div className="text-[10px] text-emerald-400 uppercase font-bold">Scenario 01</div>
              <h2 className="text-sm font-bold text-neutral-100">Prompt Injection & Honeytoken Exfiltration</h2>
            </div>
            <button
              onClick={() => handleRun('prompt-injection')}
              disabled={runningDemo === 'prompt-injection'}
              className="px-4 py-2 bg-emerald-950 border border-emerald-600 text-emerald-300 hover:bg-emerald-900 font-bold flex items-center space-x-1.5 transition-colors"
            >
              <Play size={14} />
              <span>{runningDemo === 'prompt-injection' ? 'Executing...' : 'Run Demo 1'}</span>
            </button>
          </div>

          <p className="text-neutral-400 text-xs">
            A malicious prompt injection is embedded in <code className="text-neutral-200">README_task.md</code> instructing the agent to harvest decoy credentials from <code className="text-neutral-200">.env.decoy</code> and exfiltrate them to an external endpoint (<code className="text-neutral-200">attacker.com</code>). VETO intercepts both the honeytoken access and the outbound transmission attempt.
          </p>

          {demoResults['prompt-injection'] && (
            <div className="p-4 bg-[#0a0d0c] border border-emerald-900/60 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-emerald-400">DEMO 1 RESULT:</span>
                <span className="px-2 py-0.5 bg-red-950 text-red-300 border border-red-800 font-bold">
                  {demoResults['prompt-injection'].outcome}
                </span>
              </div>

              <div className="space-y-2 pt-2">
                {demoResults['prompt-injection'].steps.map((s) => (
                  <div key={s.step} className="p-2.5 bg-[#111714] border border-[#1e2923] flex items-start space-x-2">
                    <span className="text-neutral-500 font-bold">Step {s.step}:</span>
                    <div className="flex-1 space-y-1">
                      <div className="text-neutral-200">{s.action}</div>
                      <div className="flex items-center space-x-2">
                        {s.decision && <StatusBadge type="decision" value={s.decision} />}
                        <span className="text-neutral-400 text-[11px]">{s.reason}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Scenario 2: MCP Tool Tampering */}
        <div className="bg-[#111714] border border-[#1e2923] p-5 space-y-4 font-mono text-xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-[#1e2923] gap-2">
            <div>
              <div className="text-[10px] text-emerald-400 uppercase font-bold">Scenario 02</div>
              <h2 className="text-sm font-bold text-neutral-100">Model Context Protocol (MCP) Tool Tampering</h2>
            </div>
            <button
              onClick={() => handleRun('mcp-tampering')}
              disabled={runningDemo === 'mcp-tampering'}
              className="px-4 py-2 bg-emerald-950 border border-emerald-600 text-emerald-300 hover:bg-emerald-900 font-bold flex items-center space-x-1.5 transition-colors"
            >
              <Play size={14} />
              <span>{runningDemo === 'mcp-tampering' ? 'Executing...' : 'Run Demo 2'}</span>
            </button>
          </div>

          <p className="text-neutral-400 text-xs">
            Registers an approved read-only tool (<code className="text-neutral-200">read_file</code>) with baseline SHA-256 fingerprint. Modifies its schema to inject an unexpected destructive capability (<code className="text-neutral-200">system:arbitrary_exec</code>). VETO calculates canonical fingerprint mismatch, pauses execution, and generates high-severity threat alert.
          </p>

          {demoResults['mcp-tampering'] && (
            <div className="p-4 bg-[#0a0d0c] border border-emerald-900/60 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-emerald-400">DEMO 2 RESULT:</span>
                <span className="px-2 py-0.5 bg-red-950 text-red-300 border border-red-800 font-bold">
                  {demoResults['mcp-tampering'].outcome}
                </span>
              </div>

              <div className="space-y-2 pt-2">
                {demoResults['mcp-tampering'].steps.map((s) => (
                  <div key={s.step} className="p-2.5 bg-[#111714] border border-[#1e2923] flex items-start space-x-2">
                    <span className="text-neutral-500 font-bold">Step {s.step}:</span>
                    <div className="flex-1 space-y-1">
                      <div className="text-neutral-200">{s.action}</div>
                      {s.decision && (
                        <div className="flex items-center space-x-2">
                          <StatusBadge type="decision" value={s.decision} />
                          <span className="text-neutral-400 text-[11px]">{s.reason}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Scenario 3: Physical Approval and Rejection */}
        <div className="bg-[#111714] border border-[#1e2923] p-5 space-y-4 font-mono text-xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-[#1e2923] gap-2">
            <div>
              <div className="text-[10px] text-emerald-400 uppercase font-bold">Scenario 03</div>
              <h2 className="text-sm font-bold text-neutral-100">Physical Approval & Rejection (Arduino Uno R3)</h2>
            </div>
            <button
              onClick={() => handleRun('physical-approval')}
              disabled={runningDemo === 'physical-approval'}
              className="px-4 py-2 bg-emerald-950 border border-emerald-600 text-emerald-300 hover:bg-emerald-900 font-bold flex items-center space-x-1.5 transition-colors"
            >
              <Play size={14} />
              <span>{runningDemo === 'physical-approval' ? 'Executing...' : 'Run Demo 3'}</span>
            </button>
          </div>

          <p className="text-neutral-400 text-xs">
            Agent requests deletion of critical system file (<code className="text-neutral-200">system_config.json</code>). VETO intercepts the request and issues a cryptographic approval request to the Arduino OLED and Web Approval Center. Human presses REJECT button. VETO prevents execution and proves that the file is preserved intact.
          </p>

          {demoResults['physical-approval'] && (
            <div className="p-4 bg-[#0a0d0c] border border-emerald-900/60 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-emerald-400">DEMO 3 RESULT:</span>
                <span className="px-2 py-0.5 bg-red-950 text-red-300 border border-red-800 font-bold">
                  {demoResults['physical-approval'].outcome}
                </span>
              </div>

              <div className="space-y-2 pt-2">
                {demoResults['physical-approval'].steps.map((s) => (
                  <div key={s.step} className="p-2.5 bg-[#111714] border border-[#1e2923] flex items-start space-x-2">
                    <span className="text-neutral-500 font-bold">Step {s.step}:</span>
                    <div className="flex-1 space-y-1">
                      <div className="text-neutral-200">{s.action}</div>
                      {s.decision && (
                        <div className="flex items-center space-x-2">
                          <StatusBadge type="decision" value={s.decision} />
                          <span className="text-neutral-400 text-[11px]">{s.reason}</span>
                        </div>
                      )}
                      {s.file_still_intact !== undefined && (
                        <div className="text-emerald-400 font-bold text-[11px]">
                          ✓ File preserved safely: system_config.json still exists.
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
