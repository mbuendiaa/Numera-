"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Building2, CalendarDays, PackageSearch, ReceiptText, ShoppingCart } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { Invoice, Supplier, SupplierAnalytics, SupplierProduct, User } from "@/lib/types";
import { BackendError } from "@/components/backend-error";
import { MetricCard } from "@/components/metric-card";
import { StatusBadge } from "@/components/status-badge";

const money = new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" });

export function SupplierDetailClient({ supplierId }: { supplierId: string }) {
  const detail = useQuery({
    queryKey: ["supplier-detail", supplierId],
    queryFn: async () => {
      const user = await apiFetch<User>("/auth/me");
      const query = user.company_id ? `?company_id=${encodeURIComponent(user.company_id)}` : "";
      const [allSuppliers, analytics, catalog, invoices] = await Promise.all([
        apiFetch<Supplier[]>(`/suppliers/${query}`),
        apiFetch<SupplierAnalytics>(`/intelligence/suppliers/${supplierId}/analytics`),
        apiFetch<SupplierProduct[]>(`/products/suppliers/${supplierId}/catalog`),
        apiFetch<Invoice[]>("/invoices/")
      ]);
      const supplier = allSuppliers.find((row) => row.id === supplierId);
      if (!supplier) throw new Error("Proveedor no encontrado");
      return { supplier, analytics, catalog, invoices: invoices.filter((row) => row.supplier_id === supplierId) };
    }
  });

  if (detail.isLoading) return <div className="rounded-3xl border bg-card p-8">Cargando ficha del proveedor…</div>;
  if (detail.isError) return <BackendError message={detail.error.message} retry={() => detail.refetch()} />;
  if (!detail.data) return null;

  const { supplier, analytics, catalog, invoices } = detail.data;

  return (
    <div className="space-y-7">
      <div>
        <Link href="/suppliers" className="inline-flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-foreground">
          <ArrowLeft size={16} /> Volver a proveedores
        </Link>
        <div className="mt-4 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">{supplier.name}</h1>
            <p className="mt-2 text-slate-500 dark:text-slate-400">
              {supplier.tax_id ?? "NIF no disponible"} · {supplier.country} · Cuenta contable {supplier.default_account ?? "sin asignar"}
            </p>
          </div>
          <div className="inline-flex w-fit items-center gap-2 rounded-full bg-emerald-500/10 px-3 py-1.5 text-sm font-medium text-emerald-600 dark:text-emerald-400">
            <Building2 size={16} /> Proveedor activo
          </div>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Compras" value={money.format(analytics.total_purchased)} change="importe acumulado" icon={ShoppingCart} />
        <MetricCard title="Facturas" value={String(analytics.invoice_count)} change={`ticket medio ${money.format(analytics.average_invoice)}`} icon={ReceiptText} />
        <MetricCard title="Productos" value={String(analytics.products_supplied)} change="suministrados" icon={PackageSearch} />
        <MetricCard title="Última factura" value={formatDate(analytics.latest_invoice_date)} change={analytics.latest_purchase_price ? `último precio ${money.format(analytics.latest_purchase_price)}` : "sin precios"} icon={CalendarDays} />
      </div>

      <section className="rounded-3xl border bg-card p-6 shadow-soft">
        <div className="mb-5">
          <h2 className="text-lg font-semibold">Catálogo del proveedor</h2>
          <p className="text-sm text-slate-500">Productos detectados automáticamente en sus facturas.</p>
        </div>
        {catalog.length === 0 ? (
          <div className="rounded-2xl bg-muted p-8 text-center text-sm text-slate-500">No hay productos vinculados todavía.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[850px] text-left text-sm">
              <thead className="text-slate-500"><tr className="border-b"><th className="pb-3 font-medium">Producto</th><th className="pb-3 font-medium">Referencia</th><th className="pb-3 font-medium">Descripción proveedor</th><th className="pb-3 font-medium">Unidad</th><th className="pb-3 font-medium">Último precio</th><th className="pb-3 font-medium">Fecha</th></tr></thead>
              <tbody>{catalog.map((item) => <tr key={item.id} className="border-b last:border-0"><td className="py-4 font-medium">{item.product_name ?? "Producto"}</td><td className="py-4">{item.supplier_reference}</td><td className="py-4">{item.supplier_description}</td><td className="py-4 uppercase">{item.purchase_unit}</td><td className="py-4 font-medium">{item.latest_price == null ? "—" : money.format(item.latest_price)}</td><td className="py-4">{formatDate(item.latest_price_date)}</td></tr>)}</tbody>
            </table>
          </div>
        )}
      </section>

      <section className="rounded-3xl border bg-card p-6 shadow-soft">
        <div className="mb-5"><h2 className="text-lg font-semibold">Facturas del proveedor</h2><p className="text-sm text-slate-500">Histórico documental y de compras.</p></div>
        {invoices.length === 0 ? <div className="rounded-2xl bg-muted p-8 text-center text-sm text-slate-500">No hay facturas asociadas.</div> : (
          <div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-sm"><thead className="text-slate-500"><tr className="border-b"><th className="pb-3 font-medium">Número</th><th className="pb-3 font-medium">Fecha</th><th className="pb-3 font-medium">Base</th><th className="pb-3 font-medium">IVA</th><th className="pb-3 font-medium">Total</th><th className="pb-3 font-medium">Estado</th><th className="pb-3"></th></tr></thead><tbody>{invoices.map((invoice) => <tr key={invoice.id} className="border-b last:border-0"><td className="py-4 font-medium">{invoice.invoice_number}</td><td className="py-4">{formatDate(invoice.issue_date)}</td><td className="py-4">{money.format(invoice.base_amount)}</td><td className="py-4">{money.format(invoice.tax_amount)}</td><td className="py-4 font-medium">{money.format(invoice.total_amount)}</td><td className="py-4"><StatusBadge status={invoice.status} /></td><td className="py-4 text-right"><Link href={`/invoices/${invoice.id}`} className="font-medium text-primary">Abrir</Link></td></tr>)}</tbody></table></div>
        )}
      </section>
    </div>
  );
}
