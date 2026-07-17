export interface TranscriptionSegment {
  speaker: string;
  role: 'profissional' | 'paciente' | 'desconhecido';
  start: number;
  end: number;
  text: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  sentiment_confidence: number;
}

export interface TranscriptionData {
  full_text: string;
  segments: TranscriptionSegment[];
}

export interface VideoFinding {
  type: string;
  timestamp_seconds: number;
  description: string;
  confidence: number;
}

export interface RiskDetailItem {
  text: string;
  key_indicators: string[];
  recommendation: string;
}

export interface RiskDetails {
  video: RiskDetailItem | null;
  audio: RiskDetailItem | null;
  document: RiskDetailItem | null;
}

export interface AnalysisFactors {
  positive: string[];
  attention: string[];
  recommendation: string;
}

export interface Participant {
  id: number;
  participant_id: string;
  role: string;
  face_id: string | null;
  confidence: number;
  first_frame: number | null;
  last_frame: number | null;
}

export interface ParticipantEvent {
  id: number;
  participant_id: string;
  event_type: string;
  emotion: string | null;
  body_language: string | null;
  speech: string | null;
  alert_level: string | null;
  timestamp: string | null;
  confidence: number;
}

export interface ParticipantObject {
  id: number;
  participant_id: string;
  face_id: string | null;
  object_name: string;
  interaction_type: string | null;
  timestamp: string | null;
  frame: number | null;
  confidence: number;
}

export interface SessionAnalysisOut {
  session_id: number;
  status: 'pending' | 'processing' | 'completed' | 'error';
  transcription: TranscriptionData | null;
  video_findings: VideoFinding[];
  video_analyses: Record<string, any>;
  risk_details: RiskDetails | null;
  factors: AnalysisFactors | null;
  notes_analysis_text?: string;
  participants?: Participant[];
  participant_events?: ParticipantEvent[];
  participant_objects?: ParticipantObject[];
}

export interface RiskSourcesOut {
  video: number | null;
  audio: number | null;
  document: number | null;
}

export interface SessionRiskSummaryOut {
  sessionId: number;
  globalScore: number;
  riskLevel: string;
  sources: RiskSourcesOut;
}
