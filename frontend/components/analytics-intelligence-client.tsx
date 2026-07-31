"use client";

import { useMemo, useState } from "react";
import { useQueries, useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  BarChart3,
  Boxes,
  Building2,
  FileText,
  Loader2,
  RefreshCw,
  TrendingDown,
  TrendingUp,
  WalletCards
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { apiFetch } from "@/lib/api";
import type {
  AccountingStatistics,
  Dashboard,
  Invoice,
  PriceAlert,
  Supplier,
  SupplierAnalytics
} from "@/lib/types";
import { BackendError } from "@/components/backend-error";
import { MetricCard } from "@/components/metric-card";

const money = new Intl.NumberFormat("es-ES", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 2
});
const integer = new Intl.NumberFormat("es-ES", { maximumFractionDigits: 0 });
const percent = new Intl.NumberFormat("es-ES", { style: "percent", maximumFractionDigits: 1 });

const monthFormatter = new Intl.DateTimeFormat("es-ES", { month: "short", year: "2-digit" });

function safeNumber(value: unknown): number {
  const parsed = typeof value === "number" ? value : Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function safeDate(value?: string | null): Date | null {
  if (!value) return null;
  const date = new Date(value.length === 10 ? `${value}T00:00:00` : value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function monthKey(date: Date): string {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

function lastMonths(count: number) {
  const now = new Date();
  return Array.from({ length: count }, (_, index) => {
    const date = new Date(now.getFullYear(), now.getMonth() - (count - 1 - index), 1);
    return { key: monthKey(date), label: monthFormatter.format(date) };
  });
}

function compactCurrency(value: number) {
  return new Intl.NumberFormat("es-ES", {
    notation: "compact",
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 1
  }).format(value);
}

function ChartEmpty({ text }: { text: string }) {
  return (
    <div className="flex h-[280px] items-center justify-center rounded-2xl border border-dashed bg-muted/20 px-6 text-center text-sm text-slate-500">
      {text}
    </div>
  );
}

export function AnalyticsIntelligenceClient() {
  const [period, setPeriod] = useState<6 | 12>(6);

  const dashboard = useQuery({
    queryKey: ["analytics-dashboard"],
    queryFn: () => apiFetch<Dashboard>("/intelligence/dashboard")
  });
  const invoices = useQuery({
    queryKey: ["analytics-invoices"],
    queryFn: () => apiFetch<Invoice[]>("/invoices/")
  });
  const suppliers = useQuery({
    queryKey: ["analytics-suppliers"],
    queryFn: () => apiFetch<Supplier[]>("/suppliers/")
  });
  const accounting = useQuery({
    queryKey: ["analytics-accounting"],
    queryFn: () => apiFetch<AccountingStatistics>("/accounting/statistics")
  });
  const alerts = useQuery({
    queryKey: ["analytics-price-alerts"],
    queryFn: () => apiFetch<PriceAlert[]>("/products/price-alerts")
  });

  const supplierAnalytics = useQueries({
    queries: (suppliers.data ?? []).map((supplier) => ({
      queryKey: ["analytics-supplier", supplier.id],
      queryFn: () => apiFetch<SupplierAnalytics>(`/intelligence/suppliers/${supplier.id}/analytics`),
      staleTime: 60_000
    }))
  });

  const isLoading = dashboard.isLoading || invoices.isLoading || suppliers.isLoading || accounting.isLoading;
  const firstError = [dashboard.error, invoices.error, suppliers.error, accounting.error].find(Boolean) as Error | undefined;

  const monthly = useMemo(() => {
    const months = lastMonths(period);
    const data = new Map(months.map((item) => [item.key, { ...item, compras: 0, iva: 0, facturas: 0 }]));
    for (const invoice of invoices.data ?? []) {
      const date = safeDate(invoice.issue_date);
      if (!date) continue;
      const row = data.get(monthKey(date));
      if (!row) continue;
      row.compras += safeNumber(invoice.total_amount);
      row.iva += safeNumber(invoice.tax_amount);
      row.facturas += 1;
    }
    return [...data.values()].map((row) => ({ ...row, compras: Number(row.compras.toFixed(2)), iva: Number(row.iva.toFixed(2)) }));
  }, [invoices.data, period]);

  const supplierRows = useMemo(() => {
    return supplierAnalytics
      .map((query) => query.data)
      .filter((item): item is SupplierAnalytics => Boolean(item))
      .sort((a, b) => safeNumber(b.total_purchased) - safeNumber(a.total_purchased));
  }, [supplierAnalytics]);

  const topSuppliers = supplierRows.slice(0, 6).map((item) => ({
    name: item.supplier_name.length > 22 ? `${item.supplier_name.slice(0, 22)}…` : item.supplier_name,
    compras: safeNumber(item.total_purchased),
    facturas: safeNumber(item.invoice_count)
  }));

  const totalPurchases = safeNumber(accounting.data?.purchase_volume) || (invoices.data ?? []).reduce((sum, invoice) => sum + safeNumber(invoice.total_amount), 0);
  const totalVat = (invoices.data ?? []).reduce((sum, invoice) => sum + safeNumber(invoice.tax_amount), 0);
  const averageInvoice = invoices.data?.length ? totalPurchases / invoices.data.length : 0;
  const postedRate = accounting.data?.journal_entries ? safeNumber(accounting.data.posted) / safeNumber(accounting.data.journal_entries) : 0;

  const statusData = [
    { name: "Propuestos", value: safeNumber(accounting.data?.proposed) },
    { name: "Aprobados", value: safeNumber(accounting.data?.approved) },
    { name: "Contabilizados", value: safeNumber(accounting.data?.posted) },
    { name: "Rechazados", value: safeNumber(accounting.data?.rejected) }
  ].filter((item) => item.value > 0);

  const priceAlerts = [...(alerts.data ?? [])].sort((a, b) => Math.abs(safeNumber(b.change_percent)) - Math.abs(safeNumber(a.change_percent)));
  const currentMonth = monthly.at(-1);
  const previousMonth = monthly.at(-2);
  const monthlyChange = previousMonth?.compras ? (safeNumber(currentMonth?.compras) - previousMonth.compras) / previousMonth.compras : 0;

  const refresh = () => {
    void dashboard.refetch();
    void invoices.refetch();
    void suppliers.refetch();
    void accounting.refetch();
    void alerts.refetch();
    supplierAnalytics.forEach((query) => void query.refetch());
  };

  if (isLoading) {
    return <div className="flex min-h-[420px] items-center justify-center"><Loader2 className="animate-spin text-primary" size={34} /></div>;
  }

  if (firstError) {
    return <BackendError message={firstError.message} retry={refresh} />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">Financial Intelligence Center</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="mt-2 text-slate-500">Compras, proveedores, alertas de precio y rendimiento contable en una sola vista.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="rounded-xl border bg-card p-1">
            {[6, 12].map((months) => (
              <button key={months} onClick={() => setPeriod(months as 6 | 12)} className={`rounded-lg px-4 py-2 text-sm font-medium ${period === months ? "bg-primary text-primary-foreground" : "text-slate-500 hover:bg-muted"}`}>
                {months} meses
              </button>
            ))}
          </div>
          <button onClick={refresh} className="inline-flex items-center gap-2 rounded-xl border bg-card px-4 py-2.5 text-sm font-medium hover:bg-muted">
            <RefreshCw size={16} /> Actualizar
          </button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Volumen de compras" value={money.format(totalPurchases)} change={`${integer.format(invoices.data?.length ?? 0)} facturas`} icon={WalletCards} />
        <MetricCard title="IVA soportado" value={money.format(totalVat)} change="Acumulado de facturas" icon={FileText} />
        <MetricCard title="Ticket medio" value={money.format(averageInvoice)} change={`${integer.format(dashboard.data?.suppliers ?? suppliers.data?.length ?? 0)} proveedores`} icon={Building2} />
        <MetricCard title="Tasa contabilizada" value={percent.format(postedRate)} change={`${integer.format(accounting.data?.posted ?? 0)} de ${integer.format(accounting.data?.journal_entries ?? 0)} asientos`} icon={BarChart3} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.55fr_1fr]">
        <section className="rounded-3xl border bg-card p-6 shadow-soft">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
            <div><h2 className="text-xl font-semibold">Evolución mensual</h2><p className="mt-1 text-sm text-slate-500">Volumen total de compras e IVA soportado.</p></div>
            <div className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-sm font-medium ${monthlyChange > 0 ? "bg-amber-50 text-amber-700" : "bg-emerald-50 text-emerald-700"}`}>
              {monthlyChange > 0 ? <TrendingUp size={15} /> : <TrendingDown size={15} />}
              {previousMonth?.compras ? `${monthlyChange >= 0 ? "+" : ""}${percent.format(monthlyChange)} vs. mes anterior` : "Sin comparativa"}
            </div>
          </div>
          <div className="mt-6 h-[320px]">
            {monthly.some((item) => item.compras > 0 || item.iva > 0) ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={monthly} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="label" tickLine={false} axisLine={false} />
                  <YAxis tickFormatter={compactCurrency} tickLine={false} axisLine={false} width={72} />
                  <Tooltip formatter={(value: number, name: string) => [money.format(value), name === "compras" ? "Compras" : "IVA"]} />
                  <Line type="monotone" dataKey="compras" stroke="currentColor" strokeWidth={3} dot={{ r: 3 }} activeDot={{ r: 5 }} />
                  <Line type="monotone" dataKey="iva" stroke="currentColor" strokeDasharray="5 5" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            ) : <ChartEmpty text="Todavía no hay facturas con fecha e importe para construir la evolución mensual." />}
          </div>
        </section>

        <section className="rounded-3xl border bg-card p-6 shadow-soft">
          <h2 className="text-xl font-semibold">Estado contable</h2>
          <p className="mt-1 text-sm text-slate-500">Distribución del ciclo de aprobación.</p>
          <div className="mt-5 h-[245px]">
            {statusData.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart><Pie data={statusData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={4}>{statusData.map((_, index) => <Cell key={index} fill={`hsl(var(--primary) / ${1 - index * 0.17})`} />)}</Pie><Tooltip formatter={(value: number) => integer.format(value)} /></PieChart>
              </ResponsiveContainer>
            ) : <ChartEmpty text="Todavía no hay asientos contables." />}
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {statusData.map((item) => <div key={item.name} className="rounded-xl bg-muted/50 p-3"><p className="text-slate-500">{item.name}</p><p className="mt-1 text-lg font-semibold">{integer.format(item.value)}</p></div>)}
          </div>
        </section>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.25fr_1fr]">
        <section className="rounded-3xl border bg-card p-6 shadow-soft">
          <div className="flex items-center justify-between"><div><h2 className="text-xl font-semibold">Top proveedores</h2><p className="mt-1 text-sm text-slate-500">Ranking por importe total comprado.</p></div><Building2 className="text-primary" /></div>
          <div className="mt-6 h-[320px]">
            {topSuppliers.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topSuppliers} layout="vertical" margin={{ top: 0, right: 20, left: 30, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" tickFormatter={compactCurrency} tickLine={false} axisLine={false} />
                  <YAxis type="category" dataKey="name" width={120} tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value: number) => money.format(value)} />
                  <Bar dataKey="compras" radius={[0, 8, 8, 0]} fill="currentColor" />
                </BarChart>
              </ResponsiveContainer>
            ) : <ChartEmpty text="No hay compras vinculadas a proveedores todavía." />}
          </div>
        </section>

        <section className="rounded-3xl border bg-card p-6 shadow-soft">
          <div className="flex items-center justify-between"><div><h2 className="text-xl font-semibold">Alertas de precio</h2><p className="mt-1 text-sm text-slate-500">Cambios detectados en las últimas compras.</p></div><AlertTriangle className="text-amber-500" /></div>
          <div className="mt-5 space-y-3">
            {alerts.isLoading ? <Loader2 className="mx-auto animate-spin text-primary" /> : priceAlerts.length ? priceAlerts.slice(0, 7).map((alert) => {
              const increase = alert.direction === "increase";
              return <div key={`${alert.product_id}-${alert.supplier_id}-${alert.latest_date}`} className="flex items-start justify-between gap-4 rounded-2xl border p-4"><div className="min-w-0"><p className="truncate font-medium">{alert.product_name}</p><p className="mt-1 truncate text-sm text-slate-500">{alert.supplier_name} · {money.format(safeNumber(alert.latest_price))}</p></div><span className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2.5 py-1 text-sm font-semibold ${increase ? "bg-rose-50 text-rose-700" : "bg-emerald-50 text-emerald-700"}`}>{increase ? <TrendingUp size={14}/> : <TrendingDown size={14}/>} {safeNumber(alert.change_percent) >= 0 ? "+" : ""}{safeNumber(alert.change_percent).toFixed(1)}%</span></div>;
            }) : <ChartEmpty text="No se han detectado variaciones de precio con histórico suficiente." />}
          </div>
        </section>
      </div>

      <section className="rounded-3xl border bg-card p-6 shadow-soft">
        <div className="flex items-center justify-between"><div><h2 className="text-xl font-semibold">Resumen de proveedores</h2><p className="mt-1 text-sm text-slate-500">Volumen, frecuencia y ticket medio por proveedor.</p></div><Boxes className="text-primary" /></div>
        <div className="mt-6 overflow-x-auto">
          <table className="w-full min-w-[820px] text-left text-sm">
            <thead className="text-slate-500"><tr className="border-b"><th className="pb-3">Proveedor</th><th className="pb-3 text-right">Facturas</th><th className="pb-3 text-right">Compras</th><th className="pb-3 text-right">Ticket medio</th><th className="pb-3 text-right">Productos</th><th className="pb-3">Última factura</th></tr></thead>
            <tbody>{supplierRows.slice(0, 10).map((row) => <tr key={row.supplier_id} className="border-b last:border-0"><td className="py-4 font-medium">{row.supplier_name}</td><td className="py-4 text-right">{integer.format(row.invoice_count)}</td><td className="py-4 text-right font-medium">{money.format(safeNumber(row.total_purchased))}</td><td className="py-4 text-right">{money.format(safeNumber(row.average_invoice))}</td><td className="py-4 text-right">{integer.format(row.products_supplied)}</td><td className="py-4">{safeDate(row.latest_invoice_date)?.toLocaleDateString("es-ES") ?? "—"}</td></tr>)}</tbody>
          </table>
          {!supplierRows.length && <div className="py-12 text-center text-sm text-slate-500">No hay datos de proveedores para mostrar.</div>}
        </div>
      </section>
    </div>
  );
}
