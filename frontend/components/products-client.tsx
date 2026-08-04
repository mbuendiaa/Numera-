"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Boxes, RefreshCw, Search } from "lucide-react";
import { apiFetch } from "@/lib/api";
import type { ProductCatalogItem } from "@/lib/types";

const money = new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR", minimumFractionDigits: 2 });
const dateFormat = new Intl.DateTimeFormat("es-ES");

function safeDate(value: string | null) {
  if (!value || value === "unknown") return "—";
  const parsed = new Date(`${value.slice(0, 10)}T00:00:00`);
  return Number.isNaN(parsed.getTime()) ? value : dateFormat.format(parsed);
}

function unitLabel(value: string | null | undefined) {
  const labels: Record<string, string> = { kg: "Kg", g: "g", unit: "Unidad", box: "Caja", litre: "Litro", pack: "Pack", other: "Otro" };
  return value ? labels[value] ?? value : "—";
}

export function ProductsClient() {
  const [search, setSearch] = useState("");
  const catalog = useQuery({
    queryKey: ["products", "catalog"],
    queryFn: () => apiFetch<ProductCatalogItem[]>("/products/catalog"),
  });

  const rows = useMemo(() => {
    const term = search.trim().toLocaleLowerCase("es");
    if (!term) return catalog.data ?? [];
    return (catalog.data ?? []).filter((row) =>
      [row.product_name, row.supplier_description, row.supplier_reference, row.supplier_name]
        .filter(Boolean)
        .some((value) => String(value).toLocaleLowerCase("es").includes(term))
    );
  }, [catalog.data, search]);

  return (
    <main className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary">Product Intelligence</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight">Product Master</h1>
          <p className="mt-2 text-muted-foreground">Productos reales detectados en las líneas de tus facturas.</p>
        </div>
        <button onClick={() => catalog.refetch()} className="inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-sm font-medium hover:bg-muted">
          <RefreshCw size={16} className={catalog.isFetching ? "animate-spin" : ""} /> Actualizar
        </button>
      </div>

      <section className="rounded-2xl border bg-card p-5 shadow-sm">
        <div className="relative max-w-xl">
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar producto, referencia o proveedor..." className="h-11 w-full rounded-xl border bg-background pl-10 pr-4 outline-none focus:ring-2 focus:ring-primary/30" />
        </div>

        {catalog.isLoading ? (
          <div className="py-16 text-center text-muted-foreground">Cargando catálogo real…</div>
        ) : catalog.isError ? (
          <div className="mt-5 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-destructive">{catalog.error instanceof Error ? catalog.error.message : "No se pudo cargar el catálogo"}</div>
        ) : rows.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-16 text-center">
            <div className="rounded-2xl bg-muted p-4"><Boxes size={28} /></div>
            <h2 className="text-lg font-semibold">{search ? "No hay coincidencias" : "Todavía no hay productos detectados"}</h2>
            <p className="max-w-md text-sm text-muted-foreground">{search ? "Prueba con otro término." : "Sube una factura con líneas de producto. Numera creará aquí el producto, el proveedor y su precio real."}</p>
          </div>
        ) : (
          <div className="mt-5 overflow-x-auto">
            <table className="w-full min-w-[900px] text-sm">
              <thead className="border-b text-left text-muted-foreground">
                <tr>
                  <th className="py-3 pr-4 font-medium">Producto</th>
                  <th className="py-3 pr-4 font-medium">Referencia</th>
                  <th className="py-3 pr-4 font-medium">Proveedor</th>
                  <th className="py-3 pr-4 text-right font-medium">Último precio</th>
                  <th className="py-3 pr-4 font-medium">Unidad</th>
                  <th className="py-3 font-medium">Última compra</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {rows.map((row) => (
                  <tr key={row.id} className="hover:bg-muted/40">
                    <td className="py-4 pr-4">
                      <div className="font-semibold">{row.product_name ?? row.supplier_description}</div>
                      {row.product_name && row.product_name !== row.supplier_description ? <div className="mt-1 text-xs text-muted-foreground">{row.supplier_description}</div> : null}
                    </td>
                    <td className="py-4 pr-4 font-mono text-xs">{row.supplier_reference}</td>
                    <td className="py-4 pr-4">{row.supplier_name ?? "—"}</td>
                    <td className="py-4 pr-4 text-right font-semibold">{row.latest_price == null ? "—" : money.format(Number(row.latest_price))}</td>
                    <td className="py-4 pr-4">{unitLabel(row.purchase_unit)}</td>
                    <td className="py-4">{safeDate(row.latest_price_date)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
