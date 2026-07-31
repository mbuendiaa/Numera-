"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BookOpen,
  CheckCircle2,
  CircleDollarSign,
  FilePlus2,
  Loader2,
  RefreshCw,
  Search,
  Send,
  ShieldCheck,
  XCircle
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type {
  AccountLedger,
  JournalEntry,
  JournalSummary,
  ManualJournalEntryPayload,
  TrialBalance
} from "@/lib/types";
import { BackendError } from "@/components/backend-error";
import { MetricCard } from "@/components/metric-card";
import { StatusBadge } from "@/components/status-badge";

const money = new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" });
const statusTabs = ["all", "proposed", "approved", "posted", "rejected"] as const;
type StatusTab = (typeof statusTabs)[number];
type ViewTab = "journal" | "trial" | "ledger" | "manual";

const statusLabel: Record<StatusTab, string> = {
  all: "Todos",
  proposed: "Propuestos",
  approved: "Aprobados",
  posted: "Contabilizados",
  rejected: "Rechazados"
};

function safeNumber(value: unknown): number {
  const parsed = typeof value === "number" ? value : Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function emptyLine() {
  return { account_code: "", description: "", debit: 0, credit: 0 };
}

export function AccountingEngineClient() {
  const queryClient = useQueryClient();
  const [view, setView] = useState<ViewTab>("journal");
  const [status, setStatus] = useState<StatusTab>("all");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<JournalEntry | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [ledgerCode, setLedgerCode] = useState("600000");
  const [ledgerSubmitted, setLedgerSubmitted] = useState("600000");
  const [manual, setManual] = useState<ManualJournalEntryPayload>({
    entry_date: new Date().toISOString().slice(0, 10),
    description: "",
    lines: [emptyLine(), emptyLine()]
  });

  const summary = useQuery({
    queryKey: ["accounting-summary"],
    queryFn: () => apiFetch<JournalSummary>("/accounting/journal-summary")
  });

  const journal = useQuery({
    queryKey: ["accounting-journal", status],
    queryFn: () => apiFetch<JournalEntry[]>(`/accounting/journal${status === "all" ? "" : `?status=${status}`}`)
  });

  const trial = useQuery({
    queryKey: ["accounting-trial-balance"],
    queryFn: () => apiFetch<TrialBalance>("/accounting/trial-balance?status=posted"),
    enabled: view === "trial"
  });

  const ledger = useQuery({
    queryKey: ["accounting-ledger", ledgerSubmitted],
    queryFn: () => apiFetch<AccountLedger>(`/accounting/ledger/${encodeURIComponent(ledgerSubmitted)}?include_unposted=true`),
    enabled: view === "ledger" && Boolean(ledgerSubmitted)
  });

  const transition = useMutation({
    mutationFn: ({ id, action }: { id: string; action: "approve" | "post" | "reject" }) =>
      apiFetch<JournalEntry>(`/journal/${id}/${action}`, { method: "POST" }),
    onSuccess: (entry, variables) => {
      setSelected(entry);
      setMessage(
        variables.action === "approve"
          ? "Asiento aprobado correctamente."
          : variables.action === "post"
            ? "Asiento contabilizado correctamente."
            : "Asiento rechazado correctamente."
      );
      queryClient.invalidateQueries({ queryKey: ["accounting-journal"] });
      queryClient.invalidateQueries({ queryKey: ["accounting-summary"] });
      queryClient.invalidateQueries({ queryKey: ["accounting-trial-balance"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
    onError: (error: Error) => setMessage(error.message)
  });

  const createManual = useMutation({
    mutationFn: (payload: ManualJournalEntryPayload) =>
      apiFetch<JournalEntry>("/accounting/journal", { method: "POST", body: JSON.stringify(payload) }),
    onSuccess: (entry) => {
      setSelected(entry);
      setMessage("Asiento manual creado como propuesta.");
      setManual({ entry_date: new Date().toISOString().slice(0, 10), description: "", lines: [emptyLine(), emptyLine()] });
      setView("journal");
      queryClient.invalidateQueries({ queryKey: ["accounting-journal"] });
      queryClient.invalidateQueries({ queryKey: ["accounting-summary"] });
    },
    onError: (error: Error) => setMessage(error.message)
  });

  const entries = useMemo(() => {
    const query = search.trim().toLowerCase();
    return (journal.data ?? []).filter((entry) => {
      if (!query) return true;
      return [entry.description, entry.event_type, entry.entry_date, entry.status, entry.id]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query));
    });
  }, [journal.data, search]);

  const manualDebit = manual.lines.reduce((sum, line) => sum + safeNumber(line.debit), 0);
  const manualCredit = manual.lines.reduce((sum, line) => sum + safeNumber(line.credit), 0);
  const manualBalanced = manual.lines.length >= 2 && Math.abs(manualDebit - manualCredit) <= 0.02 && manualDebit > 0;

  if (summary.isLoading || journal.isLoading) {
    return <div className="rounded-3xl border bg-card p-12 shadow-soft"><Loader2 className="mx-auto animate-spin text-primary" size={34} /><p className="mt-4 text-center text-sm text-slate-500">Cargando motor contable…</p></div>;
  }
  if (summary.isError) return <BackendError message={summary.error.message} retry={() => summary.refetch()} />;
  if (journal.isError) return <BackendError message={journal.error.message} retry={() => journal.refetch()} />;

  const data = summary.data!;

  return (
    <div className="space-y-7">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Contabilidad</h1>
          <p className="mt-2 text-slate-500 dark:text-slate-400">Gestiona propuestas, aprobaciones, contabilización, libro mayor y balance de sumas y saldos.</p>
        </div>
        <button onClick={() => { summary.refetch(); journal.refetch(); }} className="inline-flex items-center justify-center gap-2 rounded-xl border bg-card px-4 py-2.5 text-sm font-medium hover:bg-muted">
          <RefreshCw size={16} /> Actualizar
        </button>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard title="Asientos" value={String(data.total_entries)} change="Total" icon={BookOpen} />
        <MetricCard title="Propuestos" value={String(data.proposed)} change="Pendientes" icon={FilePlus2} />
        <MetricCard title="Aprobados" value={String(data.approved)} change="Listos para contabilizar" icon={ShieldCheck} />
        <MetricCard title="Contabilizados" value={String(data.posted)} change="Libro oficial" icon={CheckCircle2} />
        <MetricCard title="Debe contabilizado" value={money.format(safeNumber(data.posted_debit))} change="Acumulado" icon={CircleDollarSign} />
      </section>

      {message && <div className="flex items-center justify-between rounded-2xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm"><span>{message}</span><button onClick={() => setMessage(null)} className="font-medium text-primary">Cerrar</button></div>}

      <div className="flex flex-wrap gap-2">
        {([['journal','Diario'],['trial','Balance de sumas y saldos'],['ledger','Libro mayor'],['manual','Nuevo asiento']] as const).map(([value,label]) => (
          <button key={value} onClick={() => setView(value)} className={`rounded-xl px-4 py-2.5 text-sm font-medium transition ${view === value ? "bg-primary text-primary-foreground" : "border bg-card hover:bg-muted"}`}>{label}</button>
        ))}
      </div>

      {view === "journal" && (
        <section className="rounded-3xl border bg-card p-6 shadow-soft">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div className="flex flex-wrap gap-2">
              {statusTabs.map((value) => <button key={value} onClick={() => setStatus(value)} className={`rounded-full px-3.5 py-2 text-sm font-medium ${status === value ? "bg-primary text-primary-foreground" : "bg-muted hover:bg-muted/70"}`}>{statusLabel[value]}</button>)}
            </div>
            <label className="relative block w-full xl:w-80"><Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar asiento…" className="w-full rounded-xl border bg-background py-2.5 pl-10 pr-4 text-sm outline-none ring-primary focus:ring-2" /></label>
          </div>

          {entries.length === 0 ? <div className="mt-6 rounded-2xl bg-muted p-12 text-center"><BookOpen className="mx-auto text-slate-400" size={38} /><p className="mt-3 font-semibold">No hay asientos en esta vista</p><p className="mt-1 text-sm text-slate-500">Las facturas procesadas generarán propuestas contables automáticamente.</p></div> : (
            <div className="mt-6 overflow-x-auto"><table className="w-full min-w-[900px] text-left text-sm"><thead className="text-slate-500"><tr className="border-b"><th className="pb-3 font-medium">Fecha</th><th className="pb-3 font-medium">Descripción</th><th className="pb-3 font-medium">Tipo</th><th className="pb-3 text-right font-medium">Debe</th><th className="pb-3 text-right font-medium">Haber</th><th className="pb-3 font-medium">Estado</th><th></th></tr></thead><tbody>{entries.map((entry) => <tr key={entry.id ?? `${entry.description}-${entry.entry_date}`} className="border-b last:border-0"><td className="py-4">{formatDate(entry.entry_date)}</td><td className="py-4 font-medium">{entry.description}</td><td className="py-4">{entry.event_type.replaceAll("_", " ")}</td><td className="py-4 text-right">{money.format(safeNumber(entry.total_debit))}</td><td className="py-4 text-right">{money.format(safeNumber(entry.total_credit))}</td><td className="py-4"><StatusBadge status={entry.status} /></td><td className="py-4 text-right"><button onClick={() => setSelected(entry)} className="font-medium text-primary">Ver asiento</button></td></tr>)}</tbody></table></div>
          )}
        </section>
      )}

      {view === "trial" && (
        <section className="rounded-3xl border bg-card p-6 shadow-soft">
          <h2 className="text-xl font-semibold">Balance de sumas y saldos</h2>
          <p className="mt-1 text-sm text-slate-500">Incluye exclusivamente asientos contabilizados.</p>
          {trial.isLoading ? <Loader2 className="mx-auto mt-10 animate-spin text-primary" /> : trial.isError ? <div className="mt-5"><BackendError message={trial.error.message} retry={() => trial.refetch()} /></div> : trial.data && (
            <div className="mt-6 overflow-x-auto"><table className="w-full min-w-[760px] text-left text-sm"><thead className="text-slate-500"><tr className="border-b"><th className="pb-3">Cuenta</th><th className="pb-3">Nombre</th><th className="pb-3 text-right">Debe</th><th className="pb-3 text-right">Haber</th><th className="pb-3 text-right">Saldo</th></tr></thead><tbody>{trial.data.lines.map((line) => <tr key={line.account_code} className="border-b last:border-0"><td className="py-4 font-medium">{line.account_code}</td><td className="py-4">{line.account_name}</td><td className="py-4 text-right">{money.format(line.total_debit)}</td><td className="py-4 text-right">{money.format(line.total_credit)}</td><td className="py-4 text-right font-medium">{money.format(line.balance)}</td></tr>)}</tbody><tfoot className="border-t font-semibold"><tr><td colSpan={2} className="pt-4">Totales {trial.data.is_balanced ? "· Cuadrado" : "· Descuadrado"}</td><td className="pt-4 text-right">{money.format(trial.data.total_debit)}</td><td className="pt-4 text-right">{money.format(trial.data.total_credit)}</td><td></td></tr></tfoot></table></div>
          )}
        </section>
      )}

      {view === "ledger" && (
        <section className="rounded-3xl border bg-card p-6 shadow-soft">
          <div className="flex flex-col gap-4 md:flex-row md:items-end"><label className="flex-1 text-sm font-medium">Código de cuenta<input value={ledgerCode} onChange={(e) => setLedgerCode(e.target.value.replace(/\D/g, ""))} className="mt-2 w-full rounded-xl border bg-background px-4 py-2.5 outline-none ring-primary focus:ring-2" placeholder="Ej. 600000" /></label><button onClick={() => setLedgerSubmitted(ledgerCode)} disabled={!ledgerCode} className="rounded-xl bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground disabled:opacity-50">Consultar mayor</button></div>
          {ledger.isLoading ? <Loader2 className="mx-auto mt-10 animate-spin text-primary" /> : ledger.isError ? <div className="mt-5"><BackendError message={ledger.error.message} retry={() => ledger.refetch()} /></div> : ledger.data && <div className="mt-6"><div className="rounded-2xl bg-muted p-4"><p className="font-semibold">{ledger.data.account_code} · {ledger.data.account_name}</p><p className="mt-1 text-sm text-slate-500">Saldo final: <strong>{money.format(ledger.data.closing_balance)}</strong></p></div><div className="mt-5 overflow-x-auto"><table className="w-full min-w-[800px] text-left text-sm"><thead className="text-slate-500"><tr className="border-b"><th className="pb-3">Fecha</th><th className="pb-3">Concepto</th><th className="pb-3 text-right">Debe</th><th className="pb-3 text-right">Haber</th><th className="pb-3 text-right">Saldo</th></tr></thead><tbody>{ledger.data.movements.map((movement, index) => <tr key={`${movement.journal_entry_id}-${index}`} className="border-b last:border-0"><td className="py-4">{formatDate(movement.entry_date)}</td><td className="py-4">{movement.line_description || movement.entry_description}</td><td className="py-4 text-right">{money.format(movement.debit)}</td><td className="py-4 text-right">{money.format(movement.credit)}</td><td className="py-4 text-right font-medium">{money.format(movement.running_balance)}</td></tr>)}</tbody></table></div></div>}
        </section>
      )}

      {view === "manual" && (
        <section className="rounded-3xl border bg-card p-6 shadow-soft">
          <div><h2 className="text-xl font-semibold">Nuevo asiento manual</h2><p className="mt-1 text-sm text-slate-500">Se guardará como propuesta y deberá aprobarse antes de contabilizar.</p></div>
          <div className="mt-6 grid gap-4 md:grid-cols-[220px_1fr]"><label className="text-sm font-medium">Fecha<input type="date" value={manual.entry_date} onChange={(e) => setManual({...manual, entry_date:e.target.value})} className="mt-2 w-full rounded-xl border bg-background px-4 py-2.5" /></label><label className="text-sm font-medium">Descripción<input value={manual.description} onChange={(e) => setManual({...manual, description:e.target.value})} className="mt-2 w-full rounded-xl border bg-background px-4 py-2.5" placeholder="Concepto del asiento" /></label></div>
          <div className="mt-6 space-y-3">{manual.lines.map((line,index) => <div key={index} className="grid gap-3 rounded-2xl border p-4 md:grid-cols-[140px_1fr_150px_150px_auto]"><input value={line.account_code} onChange={(e) => { const lines=[...manual.lines]; lines[index]={...line,account_code:e.target.value.replace(/\D/g,"")}; setManual({...manual,lines}); }} className="rounded-xl border bg-background px-3 py-2" placeholder="Cuenta" /><input value={line.description} onChange={(e) => { const lines=[...manual.lines]; lines[index]={...line,description:e.target.value}; setManual({...manual,lines}); }} className="rounded-xl border bg-background px-3 py-2" placeholder="Descripción" /><input type="number" min="0" step="0.01" value={line.debit || ""} onChange={(e) => { const lines=[...manual.lines]; lines[index]={...line,debit:safeNumber(e.target.value),credit:e.target.value?0:line.credit}; setManual({...manual,lines}); }} className="rounded-xl border bg-background px-3 py-2 text-right" placeholder="Debe" /><input type="number" min="0" step="0.01" value={line.credit || ""} onChange={(e) => { const lines=[...manual.lines]; lines[index]={...line,credit:safeNumber(e.target.value),debit:e.target.value?0:line.debit}; setManual({...manual,lines}); }} className="rounded-xl border bg-background px-3 py-2 text-right" placeholder="Haber" /><button onClick={() => setManual({...manual, lines:manual.lines.filter((_,i)=>i!==index)})} disabled={manual.lines.length<=2} className="rounded-xl border px-3 py-2 text-rose-600 disabled:opacity-30">Quitar</button></div>)}</div>
          <button onClick={() => setManual({...manual,lines:[...manual.lines,emptyLine()]})} className="mt-3 rounded-xl border px-4 py-2 text-sm font-medium hover:bg-muted">Añadir línea</button>
          <div className="mt-6 flex flex-col gap-4 rounded-2xl bg-muted p-4 md:flex-row md:items-center md:justify-between"><div><p className="text-sm text-slate-500">Debe {money.format(manualDebit)} · Haber {money.format(manualCredit)}</p><p className={`mt-1 font-semibold ${manualBalanced ? "text-emerald-600" : "text-rose-600"}`}>{manualBalanced ? "Asiento cuadrado" : `Descuadre: ${money.format(Math.abs(manualDebit-manualCredit))}`}</p></div><button onClick={() => createManual.mutate(manual)} disabled={!manualBalanced || !manual.description.trim() || manual.lines.some((line)=>!line.account_code) || createManual.isPending} className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground disabled:opacity-50">{createManual.isPending ? <Loader2 className="animate-spin" size={16}/> : <Send size={16}/>} Crear propuesta</button></div>
        </section>
      )}

      {selected && (
        <section className="rounded-3xl border bg-card p-6 shadow-soft">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between"><div><p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Detalle del asiento</p><h2 className="mt-2 text-xl font-semibold">{selected.description}</h2><p className="mt-1 text-sm text-slate-500">{formatDate(selected.entry_date)} · <StatusBadge status={selected.status}/></p></div><button onClick={() => setSelected(null)} className="rounded-xl border px-3 py-2 text-sm font-medium hover:bg-muted">Cerrar</button></div>
          <div className="mt-6 overflow-x-auto rounded-2xl border"><table className="w-full min-w-[720px] text-left text-sm"><thead className="bg-muted/60 text-slate-500"><tr><th className="px-4 py-3">Cuenta</th><th className="px-4 py-3">Descripción</th><th className="px-4 py-3 text-right">Debe</th><th className="px-4 py-3 text-right">Haber</th></tr></thead><tbody>{selected.lines.map((line,index)=><tr key={`${line.account_code}-${index}`} className="border-t"><td className="px-4 py-3 font-medium">{line.account_code}{line.account_name ? ` · ${line.account_name}`:""}</td><td className="px-4 py-3">{line.description}</td><td className="px-4 py-3 text-right">{money.format(safeNumber(line.debit))}</td><td className="px-4 py-3 text-right">{money.format(safeNumber(line.credit))}</td></tr>)}</tbody><tfoot className="border-t bg-muted/40 font-semibold"><tr><td colSpan={2} className="px-4 py-3">{selected.is_balanced ? "Asiento cuadrado" : "Asiento descuadrado"}</td><td className="px-4 py-3 text-right">{money.format(safeNumber(selected.total_debit))}</td><td className="px-4 py-3 text-right">{money.format(safeNumber(selected.total_credit))}</td></tr></tfoot></table></div>
          {selected.id && <div className="mt-5 flex flex-wrap justify-end gap-3">{selected.status === "proposed" && <><button onClick={()=>transition.mutate({id:selected.id!,action:"reject"})} className="inline-flex items-center gap-2 rounded-xl border border-rose-200 px-4 py-2.5 text-sm font-medium text-rose-600"><XCircle size={16}/> Rechazar</button><button onClick={()=>transition.mutate({id:selected.id!,action:"approve"})} className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground"><CheckCircle2 size={16}/> Aprobar</button></>}{selected.status === "approved" && <button onClick={()=>transition.mutate({id:selected.id!,action:"post"})} className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground"><Send size={16}/> Contabilizar</button>}</div>}
        </section>
      )}
    </div>
  );
}
