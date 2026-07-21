export type SessionStatus = 'pending' | 'processing' | 'completed' | 'error';
export type IgaLevel = 'baixo' | 'moderado' | 'critico';

export interface MediaFile {
  id: number;
  media_type: 'video' | 'audio' | 'document';
  filename: string;
  blob_url: string | null;
  file_size_bytes: number;
  status: string;
  analysis_score: number | null;
  uploaded_at: string;
}

export interface SessionOut {
  id: number;
  title: string;
  patient_code: string;
  professional_id: number;
  status: SessionStatus;
  iga_score: number | null;
  iga_level: IgaLevel | null;
  score_video: number | null;
  score_audio: number | null;
  score_document: number | null;
  score_notes: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  media_files: MediaFile[];
}

export interface PaginatedSessions {
  total: number;
  items: SessionOut[];
}
