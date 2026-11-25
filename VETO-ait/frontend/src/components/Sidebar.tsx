import React from 'react';
import {
  LayoutDashboard,
  Activity,
  CheckCircle,
  AlertTriangle,
  KeyRound,
  FileText,
  Sliders,
  PlaySquare
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  pendingApprovalsCount: number;
  threatsCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  pendingApprovalsCount,
  threatsCount
}) => {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'live-operations', label: 'Live Operations', icon: Activity },
    { id: 'approval-center', label: 'Approval Center', icon: CheckCircle, badge: pendingApprovalsCount },
    { id: 'threat-detection', label: 'Threat Detection', icon: AlertTriangle, badge: threatsCount, badgeVariant: 'danger' },
    { id: 'mcp-integrity', label: 'MCP Integrity', icon: KeyRound },
    { id: 'audit-trail', label: 'Audit Trail', icon: FileText },
    { id: 'policies', label: 'Policy Configuration', icon: Sliders },
    { id: 'demos', label: 'Demo Scenarios', icon: PlaySquare, highlight: true },
  ];

  return (
    <aside className="w-64 bg-[#111714] border-r border-[#1e2923] flex flex-col justify-between p-4">
      <div className="space-y-1">
        <div className="text-[11px] font-mono uppercase tracking-wider text-neutral-500 px-3 py-2">
          Navigation
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 text-xs font-mono transition-colors text-left ${
                isActive
                  ? 'bg-emerald-950/70 border border-emerald-800 text-emerald-300 font-semibold'
                  : 'text-neutral-400 hover:bg-[#161f1a] hover:text-neutral-200 border border-transparent'
              } ${item.highlight && !isActive ? 'text-emerald-400' : ''}`}
            >
              <div className="flex items-center space-x-2.5">
                <Icon size={16} className={isActive ? 'text-emerald-400' : item.highlight ? 'text-emerald-500' : 'text-neutral-500'} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-none font-bold ${
                    item.badgeVariant === 'danger'
                      ? 'bg-red-950 text-red-400 border border-red-800'
                      : 'bg-amber-950 text-amber-400 border border-amber-800'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Footer Info */}
      <div className="pt-4 border-t border-[#1e2923] space-y-2">
        <div className="p-2.5 bg-[#0a0d0c] border border-[#1e2923] text-[11px] font-mono text-neutral-400">
          <div className="text-neutral-500 uppercase tracking-widest text-[9px] mb-1">Enforcement Model</div>
          <div className="text-neutral-300 font-medium">FAIL-CLOSED STRICT</div>
          <div className="text-[10px] text-neutral-500 mt-1">Determinism: 100% Non-LLM</div>
        </div>
      </div>
    </aside>
  );
};
