export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type DecisionType = 'ALLOW' | 'REVIEW' | 'VETO';
export type ExecutionStatus = 'EXECUTED' | 'BLOCKED' | 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'FAILED';

export interface SecurityEvent {
  event_id: string;
  timestamp: string;
  agent_id: string;
  session_id: string;
  operation: string;
  target_resource: string;
  risk_level: RiskLevel;
  decision: DecisionType;
  policy_reason: string;
  execution_outcome: ExecutionStatus;
  parameters: Record<string, any>;
  previous_hash: string;
  event_hash: string;
}

export interface ApprovalRequest {
  id: string;
  session_id: string;
  agent_id: string;
  operation: string;
  target_resource: string;
  action_hash: string;
  parameters: Record<string, any>;
  created_at: string;
  expires_at: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED' | 'CANCELLED';
  resolved_by?: string;
  resolved_at?: string;
}

export interface ThreatIncident {
  id: string;
  timestamp: string;
  threat_type: string;
  severity: RiskLevel;
  description: string;
  details: Record<string, any>;
  blocked: boolean;
}

export interface McpTool {
  name: string;
  description: string;
  version: string;
  input_schema: Record<string, any>;
  capabilities: string[];
  approved_fingerprint: string;
  current_fingerprint: string;
  status: 'VERIFIED' | 'TAMPERED';
  last_verified: string;
}

export interface SystemStatus {
  status: 'NOMINAL' | 'DEGRADED' | 'EMERGENCY_STOPPED';
  emergency_stop: boolean;
  hardware: {
    connected: boolean;
    port: string;
    baudrate: number;
    simulation_mode: boolean;
    available_ports: string[];
    status_label: string;
  };
  sandbox: {
    mode: string;
    workspace_path: string;
    docker_available: boolean;
    isolation_active: boolean;
    enforce_boundary: boolean;
  };
  stats: {
    total_operations: number;
    allowed_operations: number;
    blocked_operations: number;
    pending_approvals: number;
    security_incidents: number;
  };
  timestamp: string;
}

export interface PolicyRule {
  id: string;
  priority: number;
  description: string;
  decision: DecisionType;
  risk_level: RiskLevel;
  condition: Record<string, any>;
  reason: string;
}

export interface PolicyDocument {
  version: string;
  policy_name: string;
  enforcement_mode: string;
  risk_tier_mapping: Record<string, string>;
  honeytokens: {
    files: string[];
    secret_patterns: string[];
  };
  network_egress: {
    default_action: string;
    allowed_hosts: string[];
    blocked_hosts: string[];
  };
  rules: PolicyRule[];
}

export interface DemoStep {
  step: number;
  action: string;
  decision?: DecisionType;
  status?: string;
  reason?: string;
  [key: string]: any;
}

export interface DemoResult {
  scenario: string;
  outcome: string;
  enforcement_successful: boolean;
  message?: string;
  steps: DemoStep[];
}
