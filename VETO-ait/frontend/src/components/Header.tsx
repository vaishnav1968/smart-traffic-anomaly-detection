import React from 'react';
import { Shield, Cpu, Box, AlertOctagon, RefreshCw } from 'lucide-react';
import { SystemStatus } from '../types';

interface HeaderProps {
  status: SystemStatus | null;
  onEmergencyStopToggle: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  status,
  onEmergencyStopToggle,
  onRefresh,
  isRefreshing
}) => {
  const isEstop = status?.emergency_stop;
  const isHardwareConnected = status?.hardware?.connected;
  const isSim = status?.hardware?.simulation_mode;

  return (
    <header className="h-16 bg-[#111714] border-b border-[#1e2923] px-6 flex items-center justify-between">
      {/* Brand */}
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-emerald-950 border border-emerald-600/70 flex items-center justify-center text-emerald-400">
          <Shield size={18} />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold tracking-widest text-neutral-100 font-mono text-base">VETO</span>
            <span className="text-[10px] bg-emerald-950 border border-emerald-800 text-emerald-400 font-mono px-1.5 py-0.2">v1.0 ZERO-TRUST</span>
          </div>
          <p className="text-[11px] text-neutral-400 tracking-tight">AI Agent Runtime Security Guard</p>
        </div>
      </div>

      {/* Environmental Status Indicators */}
      <div className="flex items-center space-x-4">
        {/* Hardware Status */}
        <div className="flex items-center space-x-2 bg-[#0a0d0c] border border-[#1e2923] px-3 py-1.5 text-xs font-mono">
          <Cpu size={14} className={isHardwareConnected ? 'text-emerald-400' : isSim ? 'text-amber-400' : 'text-neutral-500'} />
          <span className="text-neutral-400">ARDUINO:</span>
          <span className={isHardwareConnected ? 'text-emerald-400 font-semibold' : isSim ? 'text-amber-400' : 'text-neutral-400'}>
            {isHardwareConnected ? `${status?.hardware.port} (ONLINE)` : isSim ? 'DISCONNECTED (SIMULATION)' : 'DISCONNECTED'}
          </span>
        </div>

        {/* Sandbox Status */}
        <div className="flex items-center space-x-2 bg-[#0a0d0c] border border-[#1e2923] px-3 py-1.5 text-xs font-mono">
          <Box size={14} className="text-emerald-400" />
          <span className="text-neutral-400">SANDBOX:</span>
          <span className="text-neutral-200">
            {status?.sandbox?.docker_available ? 'DOCKER CONTAINER' : 'ISOLATED LOCAL JAIL'}
          </span>
        </div>

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          className="p-2 bg-[#0a0d0c] border border-[#1e2923] text-neutral-400 hover:text-white transition-colors"
          title="Refresh State"
        >
          <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
        </button>

        {/* Emergency Stop Button */}
        <button
          onClick={onEmergencyStopToggle}
          className={`flex items-center space-x-2 px-3 py-1.5 text-xs font-mono border font-bold transition-all ${
            isEstop
              ? 'bg-red-600 text-white border-red-500 shadow-lg shadow-red-950 animate-pulse'
              : 'bg-[#181212] border-red-900/80 text-red-400 hover:bg-red-950 hover:text-red-200'
          }`}
        >
          <AlertOctagon size={14} />
          <span>{isEstop ? 'ESTOP ACTIVE (CLICK TO RESET)' : 'TRIGGER ESTOP'}</span>
        </button>
      </div>
    </header>
  );
};
