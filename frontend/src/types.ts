export interface Source {
  page: number;
  text: string;
}

export interface Difference {
  id: string;
  change_type: '新增' | '刪除' | '修改';
  risk: 'High' | 'Medium' | 'Low';
  confidence: '高' | '中' | '低';
  explanation: string;
  affected: string;
  recommended_action: string;
  old: Source | null;
  new: Source | null;
  needs_review?: boolean;
  review_status: '未覆核' | '已確認' | '需追蹤' | '不採納';
  reviewer_note: string;
}

export interface DocMetadata {
  title: string;
  version: string;
  date: string;
  is_complete: boolean;
  missing_fields: string[];
}

export type Role = 'manager' | 'engineer';

export interface MultiVersionItem {
  section_id: string;
  title: string;
  v10: string;
  v11: string;
  v12: string;
  v20: string;
  risk: 'High' | 'Medium' | 'Low';
  impact_equipment: string;
}
