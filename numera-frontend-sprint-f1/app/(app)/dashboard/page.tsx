import { AlertTriangle, FileText, ReceiptText, ShoppingCart } from "lucide-react";
import { MetricCard } from "@/components/metric-card";
import { PurchasesChart } from "@/components/purchases-chart";

const invoices = [
  { supplier: "Congelados La Red 2000", number: "V1/2604047", date: "29/07/2026", total: "340,56 €", status: "Propuesta" },
  { supplier: "Distribuciones Norte", number: "F-00871", date: "28/07/2026", total: "1.842,10 €", status: "Aprobada" },
  { supplier: "Mercamadrid Foods", number: "A-10231", date: "27/07/2026", total: "987,44 €", status: "Contabilizada" }
];

export default function DashboardPage() {
  return (
    <div className="space-y-7">
      <div>
        <p className="text-sm text-slate-500 dark:text-slate-400">Miércoles, 29 de julio</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight">Buenos días, Marta</h1>
        <p className="mt-2 text-slate-500 dark:text-slate-400">Aquí tienes el resumen de actividad de Numera.</p>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Facturas este mes" value="245" change="+12,5 %" icon={FileText} />
        <MetricCard title="Compras" value="54.320 €" change="+8,1 %" icon={ShoppingCart} />
        <MetricCard title="IVA soportado" value="11.407 €" change="+6,4 %" icon={ReceiptText} />
        <MetricCard title="Pendientes de revisión" value="3" change="-2 esta semana" icon={AlertTriangle} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.7fr_1fr]">
        <div className="rounded-3xl border bg-card p-6 shadow-soft">
          <div className="mb-5">
            <h2 className="text-lg font-semibold">Compras mensuales</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Evolución de compras registradas.</p>
          </div>
          <PurchasesChart />
        </div>

        <div className="rounded-3xl border bg-card p-6 shadow-soft">
          <h2 className="text-lg font-semibold">Alertas inteligentes</h2>
          <div className="mt-5 space-y-4">
            {[
              ["Subida de precio", "Merluza 700453 ha subido un 18 %."],
              ["Posible duplicado", "Factura F-00871 coincide con una factura existente."],
              ["Revisión contable", "Una propuesta tiene confianza inferior al 80 %."]
            ].map(([title, text]) => (
              <div key={title} className="rounded-2xl bg-muted p-4">
                <p className="font-medium">{title}</p>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-3xl border bg-card p-6 shadow-soft">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Últimas facturas</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Actividad reciente de compras.</p>
          </div>
          <a href="/invoices" className="text-sm font-medium text-primary">Ver todas</a>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="text-slate-500 dark:text-slate-400">
              <tr className="border-b">
                <th className="pb-3 font-medium">Proveedor</th>
                <th className="pb-3 font-medium">Número</th>
                <th className="pb-3 font-medium">Fecha</th>
                <th className="pb-3 font-medium">Total</th>
                <th className="pb-3 font-medium">Estado</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((invoice) => (
                <tr key={invoice.number} className="border-b last:border-0">
                  <td className="py-4 font-medium">{invoice.supplier}</td>
                  <td className="py-4">{invoice.number}</td>
                  <td className="py-4">{invoice.date}</td>
                  <td className="py-4">{invoice.total}</td>
                  <td className="py-4"><span className="rounded-full bg-muted px-3 py-1 text-xs">{invoice.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
