import React, { useState } from 'react';
import {
  ShieldCheck,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Play,
  Terminal,
  Activity
} from 'lucide-react';
import { SystemStatus, SecurityEvent } from '../../types';
import { MetricCard } from '../MetricCard';
import { StatusBadge } from '../StatusBadge';
import { api } from '../../services/api';

interface OverviewPageProps {
  status: SystemStatus | null;
  events: SecurityEvent[];
  onTriggerDemo: (scenario: string) => void;
  onRefresh: () => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  status,
  events,
  onTriggerDemo,
  onRefresh
}) => {
  const [testOp, setTestOp] = useState('read_file');
  const [testResource, setTestResource] = useState('project_data.txt');
  const [testResult, setTestResult] = useState<any>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleManualTest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await api.sendIntercept({
        operation: testOp,
        target_resource: testResource,
        parameters: { path: testResource }
      });
      setTestResult(res);
      onRefresh();
    } catch (err: any) {
      setTestResult({ error: err.message });
    } finally {
      setIsSubmitting(false);
    }
  };

  const stats = status?.stats || {
    total_operations: 0,
    allowed_operations: 0,
    blocked_operations: 0,
    pending_approvals: 0,
    security_incidents: 0
  };

  return (
    <div className="space-y-6">
      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <MetricCard
          title="Total Intercepted"
          value={stats.total_operations}
          subtitle="All agent tool calls"
          icon={Activity}
        />
        <MetricCard
          title="Auto-Allowed"
          value={stats.allowed_operations}
          subtitle="Verified low risk"
          icon={CheckCircle}
          variant="success"
        />
        <MetricCard
          title="Prohibited (VETO)"
          value={stats.blocked_operations}
          subtitle="Blocked immediately"
          icon={XCircle}
          variant="danger"
        />
        <MetricCard
          title="Pending Approval"
          value={stats.pending_approvals}
          subtitle="Human review queue"
          icon={Clock}
          variant="warning"
        />
        <MetricCard
          title="Security Incidents"
          value={stats.security_incidents}
          subtitle="Honeytoken / MCP / Egress"
          icon={AlertTriangle}
          variant="danger"
        />
      </div>

      {/* Main Grid: Status & Manual Test */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System & Enforcer State */}
        <div className="bg-[#111714] border border-[#1e2923] p-5 lg:col-span-2">
          <div className="flex items-center justify-between pb-3 border-b border-[#1e2923] mb-4">
            <h2 className="text-sm font-mono font-bold uppercase text-neutral-200 flex items-center space-x-2">
              <ShieldCheck size={16} className="text-emerald-400" />
              <span>Runtime Enforcement Architecture</span>
            </h2>
            <span className="text-xs font-mono text-emerald-400">Zero-Trust Active</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div className="bg-[#0a0d0c] border border-[#1e2923] p-3">
              <div className="text-neutral-500 uppercase tracking-widest text-[10px] mb-1">Execution Sandbox</div>
              <div className="text-neutral-200 font-semibold">{status?.sandbox?.mode || 'Isolated Local Jail'}</div>
              <div className="text-neutral-400 text-[11px] mt-1 truncate">Path: {status?.sandbox?.workspace_path}</div>
              <div className="text-emerald-500 text-[10px] mt-1 font-semibold">Boundary Check: ENFORCED</div>
            </div>

            <div className="bg-[#0a0d0c] border border-[#1e2923] p-3">
              <div className="text-neutral-500 uppercase tracking-widest text-[10px] mb-1">Arduino Physical Control</div>
              <div className="text-neutral-200 font-semibold">{status?.hardware?.status_label}</div>
              <div className="text-neutral-400 text-[11px] mt-1">Port: {status?.hardware?.port || 'N/A'} @ 115200 baud</div>
              <div className="text-emerald-500 text-[10px] mt-1 font-semibold">OLED & Buttons: SYNCHRONIZED</div>
            </div>

            <div className="bg-[#0a0d0c] border border-[#1e2923] p-3">
              <div className="text-neutral-500 uppercase tracking-widest text-[10px] mb-1">Policy Engine</div>
              <div className="text-neutral-200 font-semibold">Deterministic Rule Evaluator</div>
              <div className="text-neutral-400 text-[11px] mt-1">Fail-Closed: Enabled (No LLM Decisions)</div>
              <div className="text-emerald-500 text-[10px] mt-1 font-semibold">Priority Tiers: 1-VETO, 2-REVIEW, 3-ALLOW</div>
            </div>

            <div className="bg-[#0a0d0c] border border-[#1e2923] p-3">
              <div className="text-neutral-500 uppercase tracking-widest text-[10px] mb-1">Audit Ledger</div>
              <div className="text-neutral-200 font-semibold">SHA-256 Hash Chained</div>
              <div className="text-neutral-400 text-[11px] mt-1">Storage: SQLite with WAL mode</div>
              <div className="text-emerald-500 text-[10px] mt-1 font-semibold">Cryptographic Verification: AVAILABLE</div>
            </div>
          </div>

          {/* Quick Demo Launchers */}
          <div className="mt-5 pt-4 border-t border-[#1e2923]">
            <div className="text-[11px] font-mono uppercase text-neutral-400 mb-2">One-Click Demonstration Scenarios</div>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => onTriggerDemo('prompt-injection')}
                className="px-3 py-1.5 bg-[#16201a] border border-emerald-800/80 text-emerald-300 hover:bg-emerald-950 text-xs font-mono flex items-center space-x-1.5 transition-colors"
              >
                <Play size={12} />
                <span>Demo 1: Honeytoken Exfiltration</span>
              </button>
              <button
                onClick={() => onTriggerDemo('mcp-tampering')}
                className="px-3 py-1.5 bg-[#16201a] border border-emerald-800/80 text-emerald-300 hover:bg-emerald-950 text-xs font-mono flex items-center space-x-1.5 transition-colors"
              >
                <Play size={12} />
                <span>Demo 2: MCP Tool Tampering</span>
              </button>
              <button
                onClick={() => onTriggerDemo('physical-approval')}
                className="px-3 py-1.5 bg-[#16201a] border border-emerald-800/80 text-emerald-300 hover:bg-emerald-950 text-xs font-mono flex items-center space-x-1.5 transition-colors"
              >
                <Play size={12} />
                <span>Demo 3: Physical Approval / Reject</span>
              </button>
            </div>
          </div>
        </div>

        {/* Live Interception Tester */}
        <div className="bg-[#111714] border border-[#1e2923] p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 pb-3 border-b border-[#1e2923] mb-4">
              <Terminal size={16} className="text-emerald-400" />
              <h2 className="text-sm font-mono font-bold uppercase text-neutral-200">Interactive Interceptor</h2>
            </div>

            <form onSubmit={handleManualTest} className="space-y-3 font-mono text-xs">
              <div>
                <label className="block text-neutral-400 mb-1">Operation Type</label>
                <select
                  value={testOp}
                  onChange={(e) => setTestOp(e.target.value)}
                  className="w-full bg-[#0a0d0c] border border-[#1e2923] p-2 text-neutral-200 focus:outline-none focus:border-emerald-600"
                >
                  <option value="read_file">read_file (Permitted / Low)</option>
                  <option value="delete_file">delete_file (Sensitive / Review)</option>
                  <option value="write_file">write_file (Sensitive Config / Review)</option>
                  <option value="execute_command">execute_command (Shell command)</option>
                  <option value="http_request">http_request (Network Egress)</option>
                </select>
              </div>

              <div>
                <label className="block text-neutral-400 mb-1">Target Resource</label>
                <input
                  type="text"
                  value={testResource}
                  onChange={(e) => setTestResource(e.target.value)}
                  className="w-full bg-[#0a0d0c] border border-[#1e2923] p-2 text-neutral-200 focus:outline-none focus:border-emerald-600"
                  placeholder="e.g. project_data.txt or .env.decoy"
                />
              </div>

              <div className="flex space-x-2 pt-1">
                <button
                  type="button"
                  onClick={() => { setTestOp('read_file'); setTestResource('.env.decoy'); }}
                  className="px-2 py-1 bg-[#1a1212] border border-red-900/60 text-red-400 text-[10px]"
                >
                  Decoy Test
                </button>
                <button
                  type="button"
                  onClick={() => { setTestOp('delete_file'); setTestResource('system_config.json'); }}
                  className="px-2 py-1 bg-[#1a1710] border border-amber-900/60 text-amber-400 text-[10px]"
                >
                  Review Test
                </button>
                <button
                  type="button"
                  onClick={() => { setTestOp('read_file'); setTestResource('project_data.txt'); }}
                  className="px-2 py-1 bg-[#101a14] border border-emerald-900/60 text-emerald-400 text-[10px]"
                >
                  Allow Test
                </button>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-2 bg-emerald-900 border border-emerald-600 text-emerald-100 hover:bg-emerald-800 font-semibold transition-colors mt-2"
              >
                {isSubmitting ? 'Evaluating...' : 'Dispatch Operation to VETO'}
              </button>
            </form>
          </div>

          {/* Test Response */}
          {testResult && (
            <div className="mt-4 p-3 bg-[#0a0d0c] border border-[#1e2923] text-xs font-mono">
              <div className="text-[10px] text-neutral-500 uppercase mb-1">Evaluation Outcome</div>
              <div className="flex items-center space-x-2 mb-1">
                <StatusBadge type="decision" value={testResult.decision || 'ERROR'} />
                <span className="text-neutral-300 font-bold">{testResult.status}</span>
              </div>
              <div className="text-neutral-400 text-[11px] break-words">{testResult.reason}</div>
            </div>
          )}
        </div>
      </div>

      {/* Live Interception Event Feed */}
      <div className="bg-[#111714] border border-[#1e2923] p-5">
        <div className="flex items-center justify-between pb-3 border-b border-[#1e2923] mb-4">
          <div className="flex items-center space-x-2">
            <Activity size={16} className="text-emerald-400" />
            <h2 className="text-sm font-mono font-bold uppercase text-neutral-200">Live Intercepted Operations Stream</h2>
          </div>
          <span className="text-xs font-mono text-neutral-400">Real-time WebSocket feed</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="border-b border-[#1e2923] text-neutral-500 uppercase text-[10px]">
                <th className="py-2 px-3">Event ID</th>
                <th className="py-2 px-3">Timestamp</th>
                <th className="py-2 px-3">Operation</th>
                <th className="py-2 px-3">Target Resource</th>
                <th className="py-2 px-3">Risk</th>
                <th className="py-2 px-3">Decision</th>
                <th className="py-2 px-3">Outcome</th>
                <th className="py-2 px-3">Policy Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e2923]">
              {events.slice(0, 8).map((evt) => (
                <tr key={evt.event_id} className="hover:bg-[#151c18] transition-colors">
                  <td className="py-2 px-3 text-emerald-400 font-semibold">{evt.event_id}</td>
                  <td className="py-2 px-3 text-neutral-400">{new Date(evt.timestamp).toLocaleTimeString()}</td>
                  <td className="py-2 px-3 text-neutral-200">{evt.operation}</td>
                  <td className="py-2 px-3 text-neutral-300 max-w-xs truncate">{evt.target_resource}</td>
                  <td className="py-2 px-3">
                    <StatusBadge type="risk" value={evt.risk_level} />
                  </td>
                  <td className="py-2 px-3">
                    <StatusBadge type="decision" value={evt.decision} />
                  </td>
                  <td className="py-2 px-3">
                    <StatusBadge type="status" value={evt.execution_outcome} />
                  </td>
                  <td className="py-2 px-3 text-neutral-400 max-w-sm truncate" title={evt.policy_reason}>
                    {evt.policy_reason}
                  </td>
                </tr>
              ))}
              {events.length === 0 && (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-neutral-500">
                    No intercepted operations recorded yet. Dispatch a test or run a demonstration above.
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
