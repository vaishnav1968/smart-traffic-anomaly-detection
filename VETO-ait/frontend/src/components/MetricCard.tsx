import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'default' | 'danger' | 'warning' | 'success';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'default'
}) => {
  let borderColor = 'border-[#1e2923]';
  let iconColor = 'text-emerald-500';

  if (variant === 'danger') {
    borderColor = 'border-red-900/50';
    iconColor = 'text-red-400';
  } else if (variant === 'warning') {
    borderColor = 'border-amber-900/50';
    iconColor = 'text-amber-400';
  } else if (variant === 'success') {
    borderColor = 'border-emerald-800/60';
    iconColor = 'text-emerald-400';
  }

  return (
    <div className={`bg-[#111714] p-4 border ${borderColor} rounded-none flex items-start justify-between`}>
      <div>
        <div className="text-xs uppercase tracking-wider text-neutral-400 font-mono mb-1">{title}</div>
        <div className="text-2xl font-bold font-mono text-neutral-100">{value}</div>
        {subtitle && <div className="text-xs text-neutral-500 mt-1 font-mono">{subtitle}</div>}
      </div>
      <div className={`p-2 bg-[#0a0d0c] border border-[#1e2923] ${iconColor}`}>
        <Icon size={18} />
      </div>
    </div>
  );
};
