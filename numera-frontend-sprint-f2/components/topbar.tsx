"use client";

import { LogOut, Menu, Moon, Search, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearTokens } from "@/lib/auth";

export function Topbar({ onMenu }: { onMenu: () => void }) {
  const { resolvedTheme, setTheme } = useTheme();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  function logout() {
    clearTokens();
    router.replace("/login");
  }

  return (
    <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b bg-background/90 px-4 backdrop-blur sm:px-6 lg:px-8">
      <div className="flex items-center gap-3">
        <button className="rounded-xl border p-2 lg:hidden" onClick={onMenu}><Menu size={20} /></button>
        <div className="hidden items-center gap-2 rounded-xl border bg-card px-3 py-2 md:flex">
          <Search size={18} className="text-slate-400" />
          <input className="w-64 bg-transparent text-sm outline-none" placeholder="Buscar en Numera..." />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button aria-label="Cambiar tema" className="rounded-xl border bg-card p-2.5" onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}>
          {mounted && resolvedTheme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button aria-label="Cerrar sesión" title="Cerrar sesión" className="rounded-xl border bg-card p-2.5" onClick={logout}>
          <LogOut size={18} />
        </button>
        <div className="grid h-10 w-10 place-items-center rounded-full bg-slate-900 text-sm font-semibold text-white dark:bg-white dark:text-slate-900">MB</div>
      </div>
    </header>
  );
}
