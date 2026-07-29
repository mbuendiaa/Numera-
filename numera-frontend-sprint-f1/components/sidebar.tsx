"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3, BookOpen, Boxes, Building2, FileText,
  LayoutDashboard, Settings, ShieldAlert, X
} from "lucide-react";
import { cn } from "@/lib/utils";

const items = [
  ["/dashboard", "Dashboard", LayoutDashboard],
  ["/invoices", "Facturas", FileText],
  ["/products", "Productos", Boxes],
  ["/suppliers", "Proveedores", Building2],
  ["/accounting", "Contabilidad", BookOpen],
  ["/review", "Centro de revisión", ShieldAlert],
  ["/analytics", "Analytics", BarChart3],
  ["/settings", "Configuración", Settings]
] as const;

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const pathname = usePathname();

  return (
    <>
      {open && <button aria-label="Cerrar menú" className="fixed inset-0 z-40 bg-black/40 lg:hidden" onClick={onClose} />}
      <aside className={cn(
        "fixed inset-y-0 left-0 z-50 w-72 border-r bg-card p-5 transition-transform lg:translate-x-0",
        open ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-2xl bg-primary font-bold text-white">N</span>
            <div>
              <p className="text-lg font-semibold">Numera</p>
              <p className="text-xs text-slate-400">Accounting Intelligence</p>
            </div>
          </Link>
          <button className="lg:hidden" onClick={onClose}><X size={20} /></button>
        </div>

        <nav className="mt-9 space-y-1.5">
          {items.map(([href, label, Icon]) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                onClick={onClose}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition",
                  active ? "bg-primary text-white" : "text-slate-600 hover:bg-muted dark:text-slate-300"
                )}
              >
                <Icon size={19} />
                {label}
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
