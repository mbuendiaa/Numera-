"use client";

import Link from "next/link";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2 } from "lucide-react";
import { apiFetch } from "@/lib/api";
import type { Invoice, UploadResponse } from "@/lib/types";
import { BackendError } from "@/components/backend-error";
import { InvoiceUpload } from "@/components/invoice-upload";
import { StatusBadge } from "@/components/status-badge";

const money = new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" });

export function InvoicesClient() {
  const client = useQueryClient();
  const invoices = useQuery({
    queryKey: ["invoices"],
    queryFn: () => apiFetch<Invoice[]>("/invoices/")
  });

  function uploaded(result: UploadResponse) {
    client.invalidateQueries({ queryKey: ["invoices"] });
    client.invalidateQueries({ queryKey: ["dashboard"] });
    const text = result.duplicate
      ? `La factura ya existía (${result.existing_invoice_id ?? "sin ID"}).`
      : `Factura ${result.created_invoice?.invoice_number ?? result.document.filename} procesada correctamente.`;
    window.alert(text);
  }

  return (
    <div className="space-y-7">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Facturas</h1>
        <p className="mt-2 text-slate-500 dark:text-slate-400">Datos reales del backend y carga completa de facturas PDF.</p>
      </div>

      <InvoiceUpload onSuccess={uploaded} />

      <section className="rounded-3xl border bg-card p-6 shadow-soft">
        <div className="mb-5 flex items-end justify-between">
          <div>
            <h2 className="text-lg font-semibold">Facturas registradas</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Pulsa una factura para abrir su detalle.</p>
          </div>
          {!invoices.isLoading && !invoices.isError && <span className="rounded-full bg-muted px-3 py-1 text-xs">{invoices.data?.length ?? 0} facturas</span>}
        </div>

        {invoices.isLoading && <div className="rounded-2xl bg-muted p-6 text-sm">Cargando facturas…</div>}
        {invoices.isError && <BackendError message={invoices.error.message} retry={() => invoices.refetch()} />}

        {invoices.data && invoices.data.length === 0 && (
          <div className="rounded-2xl bg-muted p-8 text-center">
            <CheckCircle2 className="mx-auto text-slate-400" size={34} />
            <p className="mt-3 font-medium">Todavía no hay facturas</p>
            <p className="mt-1 text-sm text-slate-500">Sube el primer PDF en el bloque superior.</p>
          </div>
        )}

        {invoices.data && invoices.data.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[850px] text-left text-sm">
              <thead className="text-slate-500 dark:text-slate-400">
                <tr className="border-b">
                  <th className="pb-3 font-medium">Número</th>
                  <th className="pb-3 font-medium">Fecha</th>
                  <th className="pb-3 font-medium">Base</th>
                  <th className="pb-3 font-medium">IVA</th>
                  <th className="pb-3 font-medium">Total</th>
                  <th className="pb-3 font-medium">Estado</th>
                  <th className="pb-3 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {invoices.data.map((invoice) => (
                  <tr key={invoice.id} className="border-b last:border-0">
                    <td className="py-4 font-medium">{invoice.invoice_number}</td>
                    <td className="py-4">{invoice.issue_date}</td>
                    <td className="py-4">{money.format(invoice.base_amount)}</td>
                    <td className="py-4">{money.format(invoice.tax_amount)}</td>
                    <td className="py-4 font-medium">{money.format(invoice.total_amount)}</td>
                    <td className="py-4"><StatusBadge status={invoice.status} /></td>
                    <td className="py-4 text-right"><Link href={`/invoices/${invoice.id}`} className="font-medium text-primary">Ver detalle</Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
