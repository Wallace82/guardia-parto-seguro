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

export interface SessionAnalysisOut {
  session_id: number;
  status: 'pending' | 'processing' | 'completed' | 'error';
  transcription: TranscriptionData | null;
  video_findings: VideoFinding[];
  video_analyses: Record<string, any>;
  risk_details: RiskDetails | null;
  factors: AnalysisFactors | null;
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
