import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { OverviewPage } from './components/pages/OverviewPage';
import { LiveOperationsPage } from './components/pages/LiveOperationsPage';
import { ApprovalCenterPage } from './components/pages/ApprovalCenterPage';
import { ThreatDetectionPage } from './components/pages/ThreatDetectionPage';
import { McpIntegrityPage } from './components/pages/McpIntegrityPage';
import { AuditTrailPage } from './components/pages/AuditTrailPage';
import { PolicyConfigPage } from './components/pages/PolicyConfigPage';
import { DemoScenariosPage } from './components/pages/DemoScenariosPage';

import { SystemStatus, SecurityEvent, ApprovalRequest, ThreatIncident, McpTool } from './types';
import { api } from './services/api';
import { wsClient } from './services/websocket';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [threats, setThreats] = useState<ThreatIncident[]>([]);
  const [tools, setTools] = useState<McpTool[]>([]);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const fetchAllData = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const [statusData, eventsData, approvalsData, threatsData, toolsData] = await Promise.all([
        api.getStatus().catch(() => null),
        api.getEvents(100).catch(() => []),
        api.getApprovals().catch(() => []),
        api.getThreats(100).catch(() => []),
        api.getMcpTools().catch(() => [])
      ]);

      if (statusData) setStatus(statusData);
      setEvents(eventsData);
      setApprovals(approvalsData);
      setThreats(threatsData);
      setTools(toolsData);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
    wsClient.connect();

    const unsubscribe = wsClient.subscribe((type, data) => {
      if (
        type === 'OPERATION_INTERCEPTED' ||
        type === 'APPROVAL_REQUESTED' ||
        type === 'APPROVAL_RESOLVED' ||
        type === 'EMERGENCY_STOP_TRIGGERED' ||
        type === 'EMERGENCY_STOP_RESET' ||
        type === 'MCP_TOOL_TAMPERED' ||
        type === 'MCP_TOOL_APPROVED' ||
        type === 'DEMO_COMPLETED' ||
        type === 'ARDUINO_MESSAGE'
      ) {
        fetchAllData();
      }
    });

    const interval = setInterval(fetchAllData, 8000);
    return () => {
      unsubscribe();
      clearInterval(interval);
    };
  }, [fetchAllData]);

  const handleEmergencyStopToggle = async () => {
    try {
      if (status?.emergency_stop) {
        await api.resetEmergencyStop();
      } else {
        await api.triggerEmergencyStop();
      }
      fetchAllData();
    } catch (err: any) {
      alert(`Emergency stop error: ${err.message}`);
    }
  };

  const handleTriggerDemo = (scenario: string) => {
    setCurrentTab('demos');
  };

  const pendingApprovalsCount = approvals.filter((a) => a.status === 'PENDING').length;

  return (
    <div className="min-h-screen bg-[#0a0d0c] text-neutral-100 flex flex-col font-sans">
      <Header
        status={status}
        onEmergencyStopToggle={handleEmergencyStopToggle}
        onRefresh={fetchAllData}
        isRefreshing={isRefreshing}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          pendingApprovalsCount={pendingApprovalsCount}
          threatsCount={threats.length}
        />

        <main className="flex-1 overflow-y-auto p-6 bg-[#0a0d0c]">
          {currentTab === 'overview' && (
            <OverviewPage
              status={status}
              events={events}
              onTriggerDemo={handleTriggerDemo}
              onRefresh={fetchAllData}
            />
          )}

          {currentTab === 'live-operations' && (
            <LiveOperationsPage events={events} />
          )}

          {currentTab === 'approval-center' && (
            <ApprovalCenterPage approvals={approvals} onRefresh={fetchAllData} />
          )}

          {currentTab === 'threat-detection' && (
            <ThreatDetectionPage threats={threats} />
          )}

          {currentTab === 'mcp-integrity' && (
            <McpIntegrityPage tools={tools} onRefresh={fetchAllData} />
          )}

          {currentTab === 'audit-trail' && (
            <AuditTrailPage events={events} />
          )}

          {currentTab === 'policies' && (
            <PolicyConfigPage />
          )}

          {currentTab === 'demos' && (
            <DemoScenariosPage onRefresh={fetchAllData} />
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
