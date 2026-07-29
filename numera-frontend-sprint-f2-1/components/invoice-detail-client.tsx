"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, FileText } from "lucide-react";
import { apiFetch } from "@/lib/api";
import type { DocumentItem, Invoice } from "@/lib/types";
import { BackendError } from "@/components/backend-error";
import { StatusBadge } from "@/components/status-badge";

const money = new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" });

export function InvoiceDetailClient({ id }: { id: string }) {
  const query = useQuery({
    queryKey: ["invoice-detail", id],
    queryFn: async () => {
      const [invoices, documents] = await Promise.all([
        apiFetch<Invoice[]>("/invoices/"),
        apiFetch<DocumentItem[]>("/documents/")
      ]);
      const invoice = invoices.find((item) => item.id === id);
      if (!invoice) throw new Error("Factura no encontrada.");
      const document = documents.find((item) => item.id === invoice.source_document_id);
      return { invoice, document };
    }
  });

  if (query.isLoading) return <div className="rounded-3xl border bg-card p-10">Cargando factura…</div>;
  if (query.isError) return <BackendError message={query.error.message} retry={() => query.refetch()} />;

  const { invoice, document } = query.data!;
  let extracted: Record<string, unknown> = {};
  try {
    extracted = document?.extracted_fields_json ? JSON.parse(document.extracted_fields_json) : {};
  } catch {}

  return (
    <div className="space-y-7">
      <Link href="/invoices" className="inline-flex items-center gap-2 text-sm font-medium text-primary"><ArrowLeft size={17} />Volver a facturas</Link>

      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <p className="text-sm text-slate-500">Factura</p>
          <h1 className="mt-1 text-3xl font-semibold">{invoice.invoice_number}</h1>
        </div>
        <StatusBadge status={invoice.status} />
      </div>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border bg-card p-6 shadow-soft">
          <h2 className="text-lg font-semibold">Importes y datos</h2>
          <dl className="mt-5 grid grid-cols-2 gap-4 text-sm">
            <div><dt className="text-slate-500">Fecha</dt><dd className="mt-1 font-medium">{invoice.issue_date}</dd></div>
            <div><dt className="text-slate-500">Proveedor ID</dt><dd className="mt-1 break-all font-medium">{invoice.supplier_id ?? "Sin proveedor"}</dd></div>
            <div><dt className="text-slate-500">Base</dt><dd className="mt-1 font-medium">{money.format(invoice.base_amount)}</dd></div>
            <div><dt className="text-slate-500">IVA</dt><dd className="mt-1 font-medium">{money.format(invoice.tax_amount)}</dd></div>
            <div className="col-span-2 rounded-2xl bg-muted p-4"><dt className="text-slate-500">Total</dt><dd className="mt-1 text-2xl font-semibold">{money.format(invoice.total_amount)}</dd></div>
          </dl>
        </div>

        <div className="rounded-3xl border bg-card p-6 shadow-soft">
          <div className="flex items-center gap-3">
            <FileText size={21} />
            <h2 className="text-lg font-semibold">Documento y OCR</h2>
          </div>
          {document ? (
            <div className="mt-5 space-y-4 text-sm">
              <div><p className="text-slate-500">Archivo</p><p className="mt-1 font-medium">{document.filename}</p></div>
              <div><p className="text-slate-500">Vista previa OCR</p><p className="mt-1 max-h-40 overflow-auto rounded-2xl bg-muted p-4 whitespace-pre-wrap">{document.extracted_text_preview || "Sin vista previa"}</p></div>
            </div>
          ) : <p className="mt-5 text-sm text-slate-500">No se encontró el documento de origen.</p>}
        </div>
      </section>

      <section className="rounded-3xl border bg-card p-6 shadow-soft">
        <h2 className="text-lg font-semibold">Campos extraídos</h2>
        <pre className="mt-5 max-h-[420px] overflow-auto rounded-2xl bg-slate-950 p-5 text-xs text-slate-100">{JSON.stringify(extracted, null, 2)}</pre>
      </section>
    </div>
  );
}
