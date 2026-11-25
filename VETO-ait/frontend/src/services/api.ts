import {
  SystemStatus,
  SecurityEvent,
  ApprovalRequest,
  ThreatIncident,
  McpTool,
  PolicyDocument,
  DemoResult
} from '../types';

const API_BASE = '/api';

export const api = {
  // Status
  async getStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error('Failed to fetch status');
    return res.json();
  },

  // Events & Audit
  async getEvents(limit = 50, offset = 0): Promise<SecurityEvent[]> {
    const res = await fetch(`${API_BASE}/events?limit=${limit}&offset=${offset}`);
    if (!res.ok) throw new Error('Failed to fetch events');
    return res.json();
  },

  async verifyAuditChain(): Promise<{ valid: boolean; total_events: number; head_hash?: string; message: string; tampered_event_id?: string }> {
    const res = await fetch(`${API_BASE}/audit/verify`);
    if (!res.ok) throw new Error('Failed to verify audit chain');
    return res.json();
  },

  // Approvals
  async getApprovals(status?: string): Promise<ApprovalRequest[]> {
    const url = status ? `${API_BASE}/approvals?status=${status}` : `${API_BASE}/approvals`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch approvals');
    return res.json();
  },

  async approveRequest(id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/approvals/${id}/approve`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to approve request');
    return res.json();
  },

  async rejectRequest(id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/approvals/${id}/reject`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reject request');
    return res.json();
  },

  // Emergency Stop
  async triggerEmergencyStop(): Promise<any> {
    const res = await fetch(`${API_BASE}/emergency-stop`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to trigger emergency stop');
    return res.json();
  },

  async resetEmergencyStop(): Promise<any> {
    const res = await fetch(`${API_BASE}/emergency-stop/reset`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset emergency stop');
    return res.json();
  },

  // Threats
  async getThreats(limit = 50): Promise<ThreatIncident[]> {
    const res = await fetch(`${API_BASE}/threats?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch threats');
    return res.json();
  },

  // MCP Integrity
  async getMcpTools(): Promise<McpTool[]> {
    const res = await fetch(`${API_BASE}/mcp/integrity`);
    if (!res.ok) throw new Error('Failed to fetch MCP tools');
    return res.json();
  },

  async tamperMcpTool(toolName = 'read_file'): Promise<any> {
    const res = await fetch(`${API_BASE}/mcp/tamper?tool_name=${encodeURIComponent(toolName)}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to simulate MCP tampering');
    return res.json();
  },

  async approveMcpFingerprint(toolName = 'read_file'): Promise<any> {
    const res = await fetch(`${API_BASE}/mcp/approve-fingerprint?tool_name=${encodeURIComponent(toolName)}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to approve MCP fingerprint');
    return res.json();
  },

  // Policies
  async getPolicies(): Promise<PolicyDocument> {
    const res = await fetch(`${API_BASE}/policies`);
    if (!res.ok) throw new Error('Failed to fetch policies');
    return res.json();
  },

  async updatePolicies(policy: PolicyDocument): Promise<any> {
    const res = await fetch(`${API_BASE}/policies`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(policy)
    });
    if (!res.ok) throw new Error('Failed to update policies');
    return res.json();
  },

  // Demos
  async runDemo(scenario: string, simulateRejection = true): Promise<DemoResult> {
    const res = await fetch(`${API_BASE}/demo/${scenario}/run?simulate_rejection=${simulateRejection}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to execute demonstration');
    return res.json();
  },

  // Intercept test
  async sendIntercept(data: { operation: string; target_resource: string; parameters?: any }): Promise<any> {
    const res = await fetch(`${API_BASE}/intercept`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_id: 'AGENT-TEST-01',
        session_id: 'SESS-MANUAL',
        ...data
      })
    });
    if (!res.ok) throw new Error('Failed to intercept operation');
    return res.json();
  }
};
