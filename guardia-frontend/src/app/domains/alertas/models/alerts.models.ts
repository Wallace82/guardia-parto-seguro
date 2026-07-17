export type AlertSeverity = 'moderate' | 'critical';
export type AlertType = 'ira_critico' | 'ira_moderado' | 'system_error';

export interface AlertOut {
  id: number;
  session_id: number;
  patient_code?: string;
  session_title?: string;
  alert_type: AlertType;
  severity: AlertSeverity;
  title: string;
  description: string;
  ira_score: number | null;
  is_acknowledged: boolean;
  acknowledged_by: number | null;
  acknowledged_at: string | null;
  is_dismissed: boolean;
  dismissed_by: number | null;
  dismissed_at: string | null;
  email_sent: boolean;
  created_at: string;
  participant_id?: string;
  role?: string;
  confidence?: number;
  related_object?: string;
}

export interface PaginatedAlerts {
  total: number;
  items: AlertOut[];
}
