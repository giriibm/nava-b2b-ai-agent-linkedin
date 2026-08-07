export interface ICP {
  id: string;
  organization_id: string;
  name: string;
  industry?: string;
  geography?: string;
  company_size_range?: string;
  revenue_range?: string;
  target_roles: string[];
  keywords: string[];
  business_challenges: string[];
  created_at: string;
}

export interface ScoreRecord {
  id: string;
  score: number;
  reasoning?: string;
  factors: Record<string, number>;
  created_at: string;
}

export interface ProspectContact {
  id: string;
  company_id: string;
  full_name: string;
  title?: string;
  linkedin_url?: string;
  email?: string;
}

export interface ProspectContactDetail extends ProspectContact {
  scores: ScoreRecord[];
  messages: GeneratedMessage[];
}

export interface ResearchRecord {
  id: string;
  summary?: string;
  business_challenges: string[];
  ai_opportunity_areas: string[];
  recommended_solution?: string;
  model_used?: string;
  created_at: string;
}

export interface ProspectCompany {
  id: string;
  icp_id: string;
  name: string;
  website?: string;
  industry?: string;
  location?: string;
  employee_count?: number;
  stage: string;
  created_at: string;
  contacts: ProspectContact[];
  research_records: ResearchRecord[];
}

export interface GeneratedMessage {
  id: string;
  channel: string;
  message_type: string;
  content: string;
  status: string;
  created_at: string;
}

export interface Job {
  id: string;
  job_type: string;
  entity_type: string;
  entity_id: string;
  status: string;
  result?: Record<string, unknown>;
  error?: string;
}
