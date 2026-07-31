"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  CircleAlert,
  FileSearch,
  Loader2,
  RefreshCw,
  Search,
  ShieldCheck,
  XCircle
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { JournalEntry, ReviewCenter, ReviewItem } from "@/lib/types";
import { BackendError } from "@/components/backend-error";
import { MetricCard } from "@/components/metric-card";
import { StatusBadge } from "@/components/status-badge";

const itemLabels: Record<string, string> = {
  document: "Documento",
  invoice: "Factura",
  journal: "Asiento"
};

function reasonTone(reason: string) {
  const normalized = reason.toLowerCase();
  if (normalized.includes("duplicate")) return "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300";
  if (normalized.includes("ocr")) return "bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300";
  if (normalized.includes("balanced")) return "bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300";
  return "bg-sky-100 text-sky-700 dark:bg-sky-950/50 dark:text-sky-300";
}

function confidenceLabel(value?: number | null) {
  if (value == null) return "—";
  return `${Math.round(value * 100)} %`;
}

function detailHref(item: ReviewItem) {
  if (item.item_type === "invoice") return `/invoices/${item.id}`;
  return null;
}

export function ReviewCenterClient() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<"all" | "invoice" | "document" | "journal">("all");
  const [search, setSearch] = useState("");
  const [selectedJournal, setSelectedJournal] = useState<JournalEntry | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const review = useQuery({
    queryKey: ["review-center"],
    queryFn: () => apiFetch<ReviewCenter>("/intelligence/review")
  });

  const journalDetail = useMutation({
    mutationFn: (id: string) => apiFetch<JournalEntry>(`/journal/${id}`),
    onSuccess: (entry) => setSelectedJournal(entry),
    onError: (error: Error) => setMessage(error.message)
  });

  const transition = useMutation({
    mutationFn: ({ id, action }: { id: string; action: "approve" | "reject" }) =>
      apiFetch<JournalEntry>(`/journal/${id}/${action}`, { method: "POST" }),
    onSuccess: (entry, variables) => {
      setSelectedJournal(entry);
      setMessage(variables.action === "approve" ? "Asiento aprobado correctamente." : "Asiento rechazado correctamente.");
      queryClient.invalidateQueries({ queryKey: ["review-center"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
    onError: (error: Error) => setMessage(error.message)
  });

  const items = useMemo(() => {
    const query = search.trim().toLowerCase();
    return (review.data?.items ?? []).filter((item) => {
      if (tab !== "all" && item.item_type !== tab) return false;
      if (!query) return true;
      return [item.reference, item.reason, item.status, item.item_type]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query));
    });
  }, [review.data, search, tab]);

  if (review.isLoading) {
    return <div className="rounded-3xl border bg-card p-10 shadow-soft"><Loader2 className="mx-auto animate-spin text-primary" size={32} /><p className="mt-4 text-center text-sm text-slate-500">Analizando elementos pendientes…</p></div>;
  }

  if (review.isError) return <BackendError message={review.error.message} retry={() => review.refetch()} />;

  const data = review.data!;

  return (
    <div className="space-y-7">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Centro de revisión</h1>
          <p className="mt-2 text-slate-500 dark:text-slate-400">Prioriza incidencias de OCR, duplicados y propuestas contables que necesitan validación.</p>
        </div>
        <button onClick={() => review.refetch()} className="inline-flex items-center justify-center gap-2 rounded-xl border bg-card px-4 py-2.5 text-sm font-medium hover:bg-muted">
          <RefreshCw size={16} /> Actualizar
        </button>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard title="Pendientes" value={String(data.total_pending)} change="Cola total" icon={CircleAlert} />
        <MetricCard title="Baja confianza" value={String(data.low_confidence)} change="Clasificación" icon={FileSearch} />
        <MetricCard title="Errores OCR" value={String(data.ocr_errors)} change="Extracción" icon={AlertTriangle} />
        <MetricCard title="Descuadres" value={String(data.accounting_errors)} change="Contabilidad" icon={XCircle} />
        <MetricCard title="Duplicados" value={String(data.duplicate_candidates)} change="Detección" icon={ShieldCheck} />
      </section>

      {message && (
        <div className="flex items-center justify-between rounded-2xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm">
          <span>{message}</span>
          <button onClick={() => setMessage(null)} className="font-medium text-primary">Cerrar</button>
        </div>
      )}

      <section className="rounded-3xl border bg-card p-6 shadow-soft">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex flex-wrap gap-2">
            {([
              ["all", "Todos"],
              ["invoice", "Facturas"],
              ["document", "Documentos"],
              ["journal", "Asientos"]
            ] as const).map(([value, label]) => (
              <button key={value} onClick={() => setTab(value)} className={`rounded-full px-4 py-2 text-sm font-medium transition ${tab === value ? "bg-primary text-primary-foreground" : "bg-muted hover:bg-muted/70"}`}>
                {label}
              </button>
            ))}
          </div>
          <label className="relative block w-full xl:w-80">
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar incidencia…" className="w-full rounded-xl border bg-background py-2.5 pl-10 pr-4 text-sm outline-none ring-primary focus:ring-2" />
          </label>
        </div>

        {items.length === 0 ? (
          <div className="mt-6 rounded-2xl bg-muted p-10 text-center">
            <CheckCircle2 className="mx-auto text-emerald-500" size={38} />
            <p className="mt-3 font-semibold">No hay elementos en esta vista</p>
            <p className="mt-1 text-sm text-slate-500">La cola está limpia o ningún resultado coincide con la búsqueda.</p>
          </div>
        ) : (
          <div className="mt-6 overflow-x-auto">
            <table className="w-full min-w-[980px] text-left text-sm">
              <thead className="text-slate-500 dark:text-slate-400">
                <tr className="border-b">
                  <th className="pb-3 font-medium">Referencia</th>
                  <th className="pb-3 font-medium">Tipo</th>
                  <th className="pb-3 font-medium">Motivo</th>
                  <th className="pb-3 font-medium">Confianza</th>
                  <th className="pb-3 font-medium">Fecha</th>
                  <th className="pb-3 font-medium">Estado</th>
                  <th className="pb-3 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, index) => {
                  const href = detailHref(item);
                  return (
                    <tr key={`${item.item_type}-${item.id}-${index}`} className="border-b last:border-0">
                      <td className="py-4 font-medium">{item.reference || item.id}</td>
                      <td className="py-4"><span className="rounded-full bg-muted px-2.5 py-1 text-xs font-medium">{itemLabels[item.item_type] ?? item.item_type}</span></td>
                      <td className="py-4"><span className={`inline-flex max-w-[360px] rounded-full px-2.5 py-1 text-xs font-medium ${reasonTone(item.reason)}`}>{item.reason}</span></td>
                      <td className="py-4">{confidenceLabel(item.confidence)}</td>
                      <td className="py-4">{formatDate(item.created_at)}</td>
                      <td className="py-4"><StatusBadge status={item.status} /></td>
                      <td className="py-4 text-right">
                        {item.item_type === "journal" ? (
                          <button onClick={() => journalDetail.mutate(item.id)} disabled={journalDetail.isPending} className="inline-flex items-center gap-1 font-medium text-primary disabled:opacity-50">Revisar <ChevronRight size={16} /></button>
                        ) : href ? (
                          <Link href={href} className="inline-flex items-center gap-1 font-medium text-primary">Ver detalle <ChevronRight size={16} /></Link>
                        ) : (
                          <span className="text-xs text-slate-400">Sin detalle disponible</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedJournal && (
        <section className="rounded-3xl border bg-card p-6 shadow-soft">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Propuesta contable</p>
              <h2 className="mt-2 text-xl font-semibold">{selectedJournal.description}</h2>
              <p className="mt-1 text-sm text-slate-500">Fecha: {formatDate(selectedJournal.entry_date)} · Estado: {selectedJournal.status}</p>
            </div>
            <button onClick={() => setSelectedJournal(null)} className="rounded-xl border px-3 py-2 text-sm font-medium hover:bg-muted">Cerrar detalle</button>
          </div>

          <div className="mt-6 overflow-x-auto rounded-2xl border">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="bg-muted/60 text-slate-500 dark:text-slate-400">
                <tr><th className="px-4 py-3 font-medium">Cuenta</th><th className="px-4 py-3 font-medium">Descripción</th><th className="px-4 py-3 text-right font-medium">Debe</th><th className="px-4 py-3 text-right font-medium">Haber</th></tr>
              </thead>
              <tbody>
                {selectedJournal.lines.map((line, index) => (
                  <tr key={`${line.account_code}-${index}`} className="border-t">
                    <td className="px-4 py-3 font-medium">{line.account_code} {line.account_name ? `· ${line.account_name}` : ""}</td>
                    <td className="px-4 py-3">{line.description}</td>
                    <td className="px-4 py-3 text-right">{line.debit.toLocaleString("es-ES", { style: "currency", currency: "EUR" })}</td>
                    <td className="px-4 py-3 text-right">{line.credit.toLocaleString("es-ES", { style: "currency", currency: "EUR" })}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="border-t bg-muted/40 font-semibold">
                <tr><td className="px-4 py-3" colSpan={2}>Totales</td><td className="px-4 py-3 text-right">{selectedJournal.total_debit.toLocaleString("es-ES", { style: "currency", currency: "EUR" })}</td><td className="px-4 py-3 text-right">{selectedJournal.total_credit.toLocaleString("es-ES", { style: "currency", currency: "EUR" })}</td></tr>
              </tfoot>
            </table>
          </div>

          <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
            <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium ${selectedJournal.is_balanced ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300" : "bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300"}`}>
              {selectedJournal.is_balanced ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
              {selectedJournal.is_balanced ? "Asiento cuadrado" : "Asiento descuadrado"}
            </div>
            {selectedJournal.status === "proposed" && (
              <div className="flex gap-3">
                <button onClick={() => transition.mutate({ id: selectedJournal.id!, action: "reject" })} disabled={transition.isPending} className="rounded-xl border border-rose-200 px-4 py-2.5 text-sm font-semibold text-rose-600 hover:bg-rose-50 disabled:opacity-50">Rechazar</button>
                <button onClick={() => transition.mutate({ id: selectedJournal.id!, action: "approve" })} disabled={transition.isPending || !selectedJournal.is_balanced} className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground disabled:opacity-50">{transition.isPending && <Loader2 className="animate-spin" size={16} />} Aprobar asiento</button>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
