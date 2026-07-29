"use client";

import { Building2, CheckCircle2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import type { Company, User } from "@/lib/types";

export default function OnboardingPage() {
  const router = useRouter();
  const [companyName, setCompanyName] = useState("");
  const [country, setCountry] = useState("ES");
  const [currency, setCurrency] = useState("EUR");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (!getAccessToken()) {
      router.replace("/login");
      return;
    }

    const prepare = async () => {
      try {
        const user = await apiFetch<User>("/auth/me");
        if (user.company_id) {
          router.replace("/dashboard");
          return;
        }
        setCompanyName(sessionStorage.getItem("numera_pending_company_name") ?? "");
      } catch (err) {
        setError(err instanceof Error ? err.message : "No se pudo comprobar la sesión");
      } finally {
        setLoading(false);
      }
    };
    void prepare();
  }, [router]);

  async function createCompany(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setCreating(true);
    try {
      await apiFetch<Company>("/companies/", {
        method: "POST",
        body: JSON.stringify({ name: companyName, country, currency })
      });
      sessionStorage.removeItem("numera_pending_company_name");
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo crear la empresa");
    } finally {
      setCreating(false);
    }
  }

  if (loading) return <main className="grid min-h-screen place-items-center">Preparando tu cuenta…</main>;

  return (
    <main className="grid min-h-screen place-items-center px-4 py-10">
      <section className="w-full max-w-xl rounded-3xl border bg-card p-8 shadow-soft">
        <div className="grid h-14 w-14 place-items-center rounded-2xl bg-primary text-white"><Building2 /></div>
        <h1 className="mt-6 text-3xl font-semibold">Configura tu empresa</h1>
        <p className="mt-2 text-slate-500 dark:text-slate-400">
          Este paso vincula tu usuario con la empresa. Quedarás como <strong>propietaria y administradora principal</strong>.
        </p>

        <div className="mt-6 rounded-2xl bg-muted p-4 text-sm">
          <div className="flex gap-3"><CheckCircle2 size={19} className="shrink-0 text-primary" />
            <p>Podrás subir facturas, gestionar usuarios y acceder a toda la contabilidad.</p>
          </div>
        </div>

        <form className="mt-7 grid gap-5" onSubmit={createCompany}>
          <label className="text-sm font-medium">
            Nombre de la empresa
            <input required value={companyName} onChange={(e) => setCompanyName(e.target.value)}
              className="mt-2 w-full rounded-xl border bg-transparent px-4 py-3 outline-none focus:ring-2 focus:ring-primary" />
          </label>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="text-sm font-medium">
              País
              <select value={country} onChange={(e) => setCountry(e.target.value)}
                className="mt-2 w-full rounded-xl border bg-card px-4 py-3">
                <option value="ES">España</option>
              </select>
            </label>
            <label className="text-sm font-medium">
              Moneda
              <select value={currency} onChange={(e) => setCurrency(e.target.value)}
                className="mt-2 w-full rounded-xl border bg-card px-4 py-3">
                <option value="EUR">EUR — Euro</option>
              </select>
            </label>
          </div>

          {error && <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">{error}</div>}

          <button className="rounded-xl bg-primary px-4 py-3 font-semibold text-white disabled:opacity-60" disabled={creating}>
            {creating ? "Creando empresa…" : "Entrar en Numera"}
          </button>
        </form>
      </section>
    </main>
  );
}
