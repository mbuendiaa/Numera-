export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

export type User = {
  id: string;
  email: string;
  name: string;
  company_id: string | null;
  role: string;
  is_active: boolean;
};

export type Dashboard = {
  company_id: string;
  documents_processed: number;
  pending_review: number;
  proposed_entries: number;
  approved_entries: number;
  posted_entries: number;
  purchase_volume_month: number;
  vat_supported_month: number;
  suppliers: number;
  products: number;
  price_alerts: number;
  latest_documents: Array<{
    id: string;
    filename: string;
    status: string;
    document_type: string;
    created_at: string;
  }>;
};

export type Invoice = {
  id: string;
  company_id: string;
  supplier_id: string | null;
  invoice_number: string;
  issue_date: string;
  base_amount: number;
  tax_amount: number;
  total_amount: number;
  status: string;
  source_document_id: string | null;
};

export type DocumentItem = {
  id: string;
  company_id: string;
  filename: string;
  content_type: string;
  storage_path: string;
  document_type: string;
  status: string;
  extracted_text_preview: string;
  extracted_fields_json: string;
  created_invoice_id: string | null;
};

export type JournalLine = {
  id?: string | null;
  position?: number | null;
  account_code: string;
  account_name?: string | null;
  description: string;
  debit: number;
  credit: number;
};

export type JournalEntry = {
  id?: string | null;
  company_id: string;
  event_type: string;
  source_event_id?: string | null;
  source_document_id?: string | null;
  entry_date: string;
  description: string;
  status: string;
  lines: JournalLine[];
  total_debit: number;
  total_credit: number;
  is_balanced: boolean;
};

export type UploadResponse = {
  duplicate: boolean;
  message: string | null;
  existing_invoice_id: string | null;
  existing_journal_id: string | null;
  document: DocumentItem;
  pipeline_status: string;
  detected_type: string;
  explanation: string[];
  extracted_fields: Record<string, unknown>;
  created_invoice: Invoice | null;
  proposed_journal_entry: JournalEntry | null;
  catalog_items: Array<Record<string, unknown>>;
};
