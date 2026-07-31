"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Building2, ChevronRight, PackageSearch, ReceiptText, Search, ShoppingCart } from "lucide-react";
import { apiFetch } from "@/lib/api";
import type { Supplier, SupplierAnalytics, User } from "@/lib/types";
import { BackendError } from "@/components/backend-error";
import { MetricCard } from "@/components/metric-card";

const money = new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" });
const date = new Intl.DateTimeFormat("es-ES");

type SupplierRow = { supplier: Supplier; analytics: SupplierAnalytics };

export function SuppliersClient() {
  const [search, setSearch] = useState("");

  const suppliers = useQuery({
    queryKey: ["suppliers-with-analytics"],
    queryFn: async (): Promise<SupplierRow[]> => {
      const user = await apiFetch<User>("/auth/me");
      const query = user.company_id ? `?company_id=${encodeURIComponent(user.company_id)}` : "";
      const rows = await apiFetch<Supplier[]>(`/suppliers/${query}`);
      return Promise.all(
        rows.map(async (supplier) => ({
          supplier,
          analytics: await apiFetch<SupplierAnalytics>(`/intelligence/suppliers/${supplier.id}/analytics`)
        }))
      );
    }
  });

  const filtered = useMemo(() => {
    const value = search.trim().toLocaleLowerCase("es");
    if (!value) return suppliers.data ?? [];
    return (suppliers.data ?? []).filter(({ supplier }) =>
      [supplier.name, supplier.tax_id, supplier.default_account]
        .filter(Boolean)
        .some((field) => field!.toLocaleLowerCase("es").includes(value))
    );
  }, [search, suppliers.data]);

  const totals = useMemo(() => {
    const rows = suppliers.data ?? [];
    return {
      suppliers: rows.length,
      invoices: rows.reduce((sum, row) => sum + row.analytics.invoice_count, 0),
      purchased: rows.reduce((sum, row) => sum + row.analytics.total_purchased, 0),
      products: rows.reduce((sum, row) => sum + row.analytics.products_supplied, 0)
    };
  }, [suppliers.data]);

  return (
    <div className="space-y-7">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Proveedores</h1>
        <p className="mt-2 text-slate-500 dark:text-slate-400">
          Compras, facturas y catálogo de productos agrupados por proveedor.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Proveedores" value={String(totals.suppliers)} change="registrados" icon={Building2} />
        <MetricCard title="Facturas" value={String(totals.invoices)} change="procesadas" icon={ReceiptText} />
        <MetricCard title="Compras acumuladas" value={money.format(totals.purchased)} change="volumen total" icon={ShoppingCart} />
        <MetricCard title="Productos asociados" value={String(totals.products)} change="relaciones de catálogo" icon={PackageSearch} />
      </div>

      <section className="rounded-3xl border bg-card p-6 shadow-soft">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold">Directorio de proveedores</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Abre un proveedor para consultar su ficha completa.</p>
          </div>
          <label className="relative block w-full md:w-80">
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Buscar nombre, NIF o cuenta…"
              className="w-full rounded-xl border bg-background py-2.5 pl-10 pr-3 text-sm outline-none transition focus:border-primary"
            />
          </label>
        </div>

        <div className="mt-6">
          {suppliers.isLoading && <div className="rounded-2xl bg-muted p-6 text-sm">Cargando proveedores y métricas…</div>}
          {suppliers.isError && <BackendError message={suppliers.error.message} retry={() => suppliers.refetch()} />}

          {suppliers.data && suppliers.data.length === 0 && (
            <div className="rounded-2xl border border-dashed p-10 text-center">
              <Building2 className="mx-auto text-slate-400" size={36} />
              <p className="mt-3 font-medium">Todavía no hay proveedores</p>
              <p className="mt-1 text-sm text-slate-500">Se crearán automáticamente al procesar facturas.</p>
            </div>
          )}

          {suppliers.data && suppliers.data.length > 0 && filtered.length === 0 && (
            <div className="rounded-2xl bg-muted p-8 text-center text-sm text-slate-500">No hay resultados para “{search}”.</div>
          )}

          {filtered.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[980px] text-left text-sm">
                <thead className="text-slate-500 dark:text-slate-400">
                  <tr className="border-b">
                    <th className="pb-3 font-medium">Proveedor</th>
                    <th className="pb-3 font-medium">NIF</th>
                    <th className="pb-3 font-medium">Facturas</th>
                    <th className="pb-3 font-medium">Compras</th>
                    <th className="pb-3 font-medium">Ticket medio</th>
                    <th className="pb-3 font-medium">Productos</th>
                    <th className="pb-3 font-medium">Última factura</th>
                    <th className="pb-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(({ supplier, analytics }) => (
                    <tr key={supplier.id} className="border-b last:border-0 hover:bg-muted/40">
                      <td className="py-4">
                        <div className="font-medium">{supplier.name}</div>
                        <div className="mt-1 text-xs text-slate-500">{supplier.country} · Cuenta {supplier.default_account ?? "sin asignar"}</div>
                      </td>
                      <td className="py-4">{supplier.tax_id ?? "—"}</td>
                      <td className="py-4">{analytics.invoice_count}</td>
                      <td className="py-4 font-medium">{money.format(analytics.total_purchased)}</td>
                      <td className="py-4">{money.format(analytics.average_invoice)}</td>
                      <td className="py-4">{analytics.products_supplied}</td>
                      <td className="py-4">{analytics.latest_invoice_date ? date.format(new Date(`${analytics.latest_invoice_date}T00:00:00`)) : "—"}</td>
                      <td className="py-4 text-right">
                        <Link href={`/suppliers/${supplier.id}`} className="inline-flex items-center gap-1 font-medium text-primary">
                          Ver ficha <ChevronRight size={16} />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
