import React, { useEffect, useState } from 'react';
import { Sliders, Save, CheckCircle2 } from 'lucide-react';
import { PolicyDocument } from '../../types';
import { api } from '../../services/api';
import { StatusBadge } from '../StatusBadge';

export const PolicyConfigPage: React.FC = () => {
  const [policies, setPolicies] = useState<PolicyDocument | null>(null);
  const [loading, setLoading] = useState(true);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    loadPolicies();
  }, []);

  const loadPolicies = async () => {
    setLoading(true);
    try {
      const data = await api.getPolicies();
      setPolicies(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!policies) return;
    try {
      await api.updatePolicies(policies);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err: any) {
      alert(`Save error: ${err.message}`);
    }
  };

  if (loading || !policies) {
    return <div className="p-8 text-neutral-500 font-mono text-xs">Loading policy rules...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#1e2923]">
        <div>
          <h1 className="text-lg font-mono font-bold text-neutral-100 uppercase tracking-wide flex items-center space-x-2">
            <Sliders size={18} className="text-emerald-400" />
            <span>Deterministic Policy Configuration</span>
          </h1>
          <p className="text-xs font-mono text-neutral-400 mt-0.5">
            Strict policy hierarchy: Priority 1-9 (AUTO-VETO), 10-19 (HUMAN REVIEW), 20-29 (AUTO-ALLOW)
          </p>
        </div>

        <button
          onClick={handleSave}
          className="px-4 py-2 bg-emerald-950 border border-emerald-600 text-emerald-300 hover:bg-emerald-900 font-mono text-xs font-bold flex items-center space-x-2 transition-colors"
        >
          <Save size={16} />
          <span>Save Policy Configuration</span>
        </button>
      </div>

      {savedSuccess && (
        <div className="p-3 bg-emerald-950/40 border border-emerald-800 text-emerald-300 font-mono text-xs flex items-center space-x-2">
          <CheckCircle2 size={16} />
          <span>Policies saved and hot-reloaded into active VETO policy engine.</span>
        </div>
      )}

      {/* Rules Table */}
      <div className="bg-[#111714] border border-[#1e2923] p-5 space-y-4 font-mono text-xs">
        <div className="flex items-center justify-between border-b border-[#1e2923] pb-2 text-neutral-400 text-[11px]">
          <span>ACTIVE RULES ({policies.rules.length})</span>
          <span>Fail-Closed Mode: STRICT</span>
        </div>

        <div className="space-y-3">
          {policies.rules.map((rule, idx) => (
            <div
              key={rule.id}
              className="p-3 bg-[#0a0d0c] border border-[#1e2923] space-y-2 hover:border-[#2a3b32] transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-neutral-500 font-bold">#{rule.priority}</span>
                  <span className="text-neutral-100 font-bold">{rule.id}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <StatusBadge type="risk" value={rule.risk_level} />
                  <StatusBadge type="decision" value={rule.decision} />
                </div>
              </div>

              <div className="text-neutral-300 text-[11px]">{rule.description}</div>

              <div className="p-2 bg-[#111714] border border-[#1e2923]/60 text-[10px] text-neutral-400">
                <span className="text-neutral-500 uppercase mr-1">Condition:</span>
                {JSON.stringify(rule.condition)}
              </div>

              <div className="text-[10px] text-neutral-500">
                <span className="uppercase text-neutral-600 mr-1">Reason:</span>
                {rule.reason}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
