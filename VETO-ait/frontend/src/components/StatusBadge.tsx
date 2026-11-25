import React from 'react';

interface StatusBadgeProps {
  type: 'decision' | 'risk' | 'status' | 'mcp';
  value: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ type, value }) => {
  const upper = value.toUpperCase();

  let bg = 'bg-neutral-800 text-neutral-300 border-neutral-700';

  if (type === 'decision') {
    if (upper === 'ALLOW') {
      bg = 'bg-emerald-950/60 text-emerald-400 border-emerald-800/80';
    } else if (upper === 'REVIEW') {
      bg = 'bg-amber-950/60 text-amber-400 border-amber-800/80';
    } else if (upper === 'VETO') {
      bg = 'bg-red-950/60 text-red-400 border-red-800/80';
    }
  } else if (type === 'risk') {
    if (upper === 'LOW') {
      bg = 'bg-emerald-950/40 text-emerald-300 border-emerald-800/60';
    } else if (upper === 'MEDIUM') {
      bg = 'bg-blue-950/40 text-blue-300 border-blue-800/60';
    } else if (upper === 'HIGH') {
      bg = 'bg-amber-950/60 text-amber-400 border-amber-800/80';
    } else if (upper === 'CRITICAL') {
      bg = 'bg-red-950/70 text-red-300 border-red-800 font-bold';
    }
  } else if (type === 'mcp') {
    if (upper === 'VERIFIED' || upper === 'APPROVED') {
      bg = 'bg-emerald-950/60 text-emerald-400 border-emerald-800/80';
    } else {
      bg = 'bg-red-950/70 text-red-300 border-red-800 font-bold animate-pulse';
    }
  } else if (type === 'status') {
    if (upper === 'EXECUTED' || upper === 'APPROVED') {
      bg = 'bg-emerald-950/40 text-emerald-400 border-emerald-800/60';
    } else if (upper === 'PENDING' || upper === 'PENDING_APPROVAL') {
      bg = 'bg-amber-950/60 text-amber-400 border-amber-800/80';
    } else {
      bg = 'bg-red-950/50 text-red-400 border-red-800/60';
    }
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-xs font-mono border rounded ${bg}`}>
      {value}
    </span>
  );
};
