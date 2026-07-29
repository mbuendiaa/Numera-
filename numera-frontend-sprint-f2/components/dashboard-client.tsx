"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Boxes, FileText, ReceiptText, ShoppingCart, Truck } from "lucide-react";
import { apiFetch } from "@/lib/api";
import type { Dashboard } from "@/lib/types";
import { BackendError } from "@/components/backend-error";
import { MetricCard } from "@/components/metric-card";
import { StatusBadge } from "@/components/status-badge";

const money = new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" });

export function DashboardClient() {
  const query = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => apiFetch<Dashboard>("/intelligence/dashboard")
  });

  if (query.isLoading) return <div className="rounded-3xl border bg-card p-10">Cargando datos reales del backend…</div>;
  if (query.isError) return <BackendError message={query.error.message} retry={() => query.refetch()} />;

  const data = query.data!;

  return (
    <div className="space-y-7">
      <div>
        <p className="text-sm text-slate-500 dark:text-slate-400">Datos de tu empresa activa</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight">Dashboard</h1>
        <p className="mt-2 text-slate-500 dark:text-slate-400">Resumen obtenido en tiempo real desde FastAPI.</p>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Documentos procesados" value={String(data.documents_processed)} change="Total" icon={FileText} />
        <MetricCard title="Compras este mes" value={money.format(data.purchase_volume_month)} change="Mes actual" icon={ShoppingCart} />
        <MetricCard title="IVA soportado" value={money.format(data.vat_supported_month)} change="Mes actual" icon={ReceiptText} />
        <MetricCard title="Pendientes de revisión" value={String(data.pending_review)} change="Centro de revisión" icon={AlertTriangle} />
        <MetricCard title="Proveedores" value={String(data.suppliers)} change="Registrados" icon={Truck} />
        <MetricCard title="Productos" value={String(data.products)} change="Registrados" icon={Boxes} />
        <MetricCard title="Asientos propuestos" value={String(data.proposed_entries)} change="Pendientes" icon={FileText} />
        <MetricCard title="Asientos contabilizados" value={String(data.posted_entries)} change={`${data.approved_entries} aprobados`} icon={ReceiptText} />
      </section>

      <section className="rounded-3xl border bg-card p-6 shadow-soft">
        <div className="mb-5">
          <h2 className="text-lg font-semibold">Últimos documentos</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">Los diez documentos más recientes.</p>
        </div>

        {data.latest_documents.length === 0 ? (
          <div className="rounded-2xl bg-muted p-6 text-sm text-slate-500">Todavía no hay documentos. Sube la primera factura desde Facturas.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px] text-left text-sm">
              <thead className="text-slate-500 dark:text-slate-400">
                <tr className="border-b">
                  <th className="pb-3 font-medium">Archivo</th>
                  <th className="pb-3 font-medium">Tipo</th>
                  <th className="pb-3 font-medium">Fecha</th>
                  <th className="pb-3 font-medium">Estado</th>
                </tr>
              </thead>
              <tbody>
                {data.latest_documents.map((doc) => (
                  <tr key={doc.id} className="border-b last:border-0">
                    <td className="py-4 font-medium">{doc.filename}</td>
                    <td className="py-4">{doc.document_type}</td>
                    <td className="py-4">{new Date(doc.created_at).toLocaleString("es-ES")}</td>
                    <td className="py-4"><StatusBadge status={doc.status} /></td>
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
