"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  Building2,
  Check,
  ChevronDown,
  FileCog,
  KeyRound,
  Loader2,
  Moon,
  Plus,
  RefreshCw,
  Save,
  Settings2,
  ShieldCheck,
  Sun,
  Trash2,
  UserCog,
  Users
} from "lucide-react";
import { useTheme } from "next-themes";
import { apiFetch } from "@/lib/api";
import type { AuditLog, CompanyWithRole, CompanyMember, User } from "@/lib/types";
import { BackendError } from "@/components/backend-error";

const ROLES = ["owner", "admin", "accountant", "manager", "employee", "readonly"] as const;
type Role = (typeof ROLES)[number];
type Tab = "company" | "users" | "accounting" | "preferences" | "audit";

const roleLabels: Record<Role, string> = {
  owner: "Propietario",
  admin: "Administrador",
  accountant: "Contable",
  manager: "Responsable",
  employee: "Empleado",
  readonly: "Solo lectura"
};

const accountingDefaults = {
  chart: "PGC España",
  purchaseAccount: "600000",
  supplierAccount: "400000",
  vatAccount: "472000",
  journalPrefix: "NUM",
  approvalMode: "manual",
  autoPost: false
};

const preferenceDefaults = {
  language: "es",
  dateFormat: "DD/MM/YYYY",
  timezone: "Europe/Madrid",
  ocrThreshold: 85,
  emailNotifications: true,
  priceAlerts: true,
  reviewNotifications: true
};

function readLocal<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? { ...fallback, ...JSON.parse(raw) } : fallback;
  } catch {
    return fallback;
  }
}

function SectionCard({ title, description, icon: Icon, children }: { title: string; description: string; icon: React.ElementType; children: React.ReactNode }) {
  return (
    <section className="rounded-3xl border bg-card p-6 shadow-soft">
      <div className="flex items-start gap-3">
        <div className="rounded-2xl bg-primary/10 p-3 text-primary"><Icon size={21} /></div>
        <div><h2 className="text-xl font-semibold">{title}</h2><p className="mt-1 text-sm text-slate-500">{description}</p></div>
      </div>
      <div className="mt-6">{children}</div>
    </section>
  );
}

function Field({ label, children, hint }: { label: string; children: React.ReactNode; hint?: string }) {
  return <label className="block"><span className="mb-2 block text-sm font-medium">{label}</span>{children}{hint && <span className="mt-1.5 block text-xs text-slate-500">{hint}</span>}</label>;
}

const inputClass = "w-full rounded-xl border bg-background px-3.5 py-2.5 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/15 disabled:cursor-not-allowed disabled:bg-muted";

export function SettingsAdminClient() {
  const queryClient = useQueryClient();
  const { theme, setTheme } = useTheme();
  const [tab, setTab] = useState<Tab>("company");
  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteName, setInviteName] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [invitePassword, setInvitePassword] = useState("");
  const [inviteRole, setInviteRole] = useState<Role>("accountant");
  const [notice, setNotice] = useState<string | null>(null);
  const [accounting, setAccounting] = useState(accountingDefaults);
  const [preferences, setPreferences] = useState(preferenceDefaults);

  useEffect(() => {
    setAccounting(readLocal("numera.accounting.settings", accountingDefaults));
    setPreferences(readLocal("numera.preferences", preferenceDefaults));
  }, []);

  const me = useQuery({ queryKey: ["me"], queryFn: () => apiFetch<User>("/auth/me") });
  const companies = useQuery({ queryKey: ["companies", "my"], queryFn: () => apiFetch<CompanyWithRole[]>("/companies/my") });
  const activeCompany = useMemo(() => companies.data?.find((company) => company.selected) ?? companies.data?.[0] ?? null, [companies.data]);
  const companyId = activeCompany?.id ?? me.data?.company_id ?? "";
  const canManageUsers = me.data?.role === "owner" || me.data?.role === "admin";

  const members = useQuery({
    queryKey: ["company-members", companyId],
    queryFn: () => apiFetch<CompanyMember[]>(`/companies/${companyId}/members`),
    enabled: Boolean(companyId) && ["owner", "admin", "accountant"].includes(me.data?.role ?? "")
  });

  const audit = useQuery({
    queryKey: ["company-audit", companyId],
    queryFn: () => apiFetch<AuditLog[]>(`/companies/${companyId}/audit?limit=50`),
    enabled: Boolean(companyId) && tab === "audit" && ["owner", "admin", "accountant"].includes(me.data?.role ?? "")
  });

  const activateCompany = useMutation({
    mutationFn: (id: string) => apiFetch(`/companies/${id}/activate`, { method: "POST" }),
    onSuccess: async () => {
      await Promise.all([queryClient.invalidateQueries({ queryKey: ["companies"] }), queryClient.invalidateQueries({ queryKey: ["me"] })]);
      setNotice("Empresa activa actualizada.");
    }
  });

  const addMember = useMutation({
    mutationFn: () => apiFetch(`/companies/${companyId}/users`, { method: "POST", body: JSON.stringify({ name: inviteName, email: inviteEmail, temporary_password: invitePassword, role: inviteRole }) }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["company-members", companyId] });
      setInviteName(""); setInviteEmail(""); setInvitePassword(""); setInviteRole("accountant"); setInviteOpen(false); setNotice("Usuario creado y vinculado automáticamente a la empresa.");
    }
  });

  const updateRole = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: Role }) => apiFetch(`/companies/${companyId}/members/${userId}`, { method: "PATCH", body: JSON.stringify({ role }) }),
    onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ["company-members", companyId] }); setNotice("Rol actualizado."); }
  });

  const removeMember = useMutation({
    mutationFn: (userId: string) => apiFetch(`/companies/${companyId}/members/${userId}`, { method: "DELETE" }),
    onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ["company-members", companyId] }); setNotice("Acceso eliminado."); }
  });

  const saveAccounting = () => {
    window.localStorage.setItem("numera.accounting.settings", JSON.stringify(accounting));
    setNotice("Preferencias contables guardadas en este dispositivo.");
  };

  const savePreferences = () => {
    window.localStorage.setItem("numera.preferences", JSON.stringify(preferences));
    setNotice("Preferencias de Numera guardadas.");
  };

  const loading = me.isLoading || companies.isLoading;
  const firstError = me.error instanceof Error ? me.error : companies.error instanceof Error ? companies.error : null;
  if (loading) return <div className="flex min-h-[420px] items-center justify-center"><Loader2 className="animate-spin text-primary" size={34} /></div>;
  if (firstError) return <BackendError message={firstError.message} retry={() => { void me.refetch(); void companies.refetch(); }} />;

  const tabs: Array<{ id: Tab; label: string; icon: React.ElementType }> = [
    { id: "company", label: "Empresa", icon: Building2 },
    { id: "users", label: "Usuarios", icon: Users },
    { id: "accounting", label: "Contabilidad", icon: FileCog },
    { id: "preferences", label: "Preferencias", icon: Settings2 },
    { id: "audit", label: "Auditoría", icon: Activity }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div><p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">Administración de Numera</p><h1 className="mt-2 text-3xl font-bold tracking-tight">Configuración</h1><p className="mt-2 text-slate-500">Empresa, usuarios, contabilidad, seguridad y preferencias.</p></div>
        <button onClick={() => { void me.refetch(); void companies.refetch(); if (companyId) void members.refetch(); }} className="inline-flex items-center gap-2 self-start rounded-xl border bg-card px-4 py-2.5 text-sm font-medium hover:bg-muted"><RefreshCw size={16}/>Actualizar</button>
      </div>

      {notice && <div className="flex items-center justify-between rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"><span className="inline-flex items-center gap-2"><Check size={16}/>{notice}</span><button onClick={() => setNotice(null)}>×</button></div>}

      <div className="flex gap-2 overflow-x-auto rounded-2xl border bg-card p-2">
        {tabs.map(({ id, label, icon: Icon }) => <button key={id} onClick={() => setTab(id)} className={`inline-flex shrink-0 items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium ${tab === id ? "bg-primary text-primary-foreground" : "text-slate-500 hover:bg-muted"}`}><Icon size={16}/>{label}</button>)}
      </div>

      {tab === "company" && <div className="grid gap-6 xl:grid-cols-[1.35fr_1fr]">
        <SectionCard title="Empresa activa" description="Información principal y contexto contable actual." icon={Building2}>
          {activeCompany ? <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Nombre de la empresa"><input className={inputClass} value={activeCompany.name} disabled /></Field>
            <Field label="Identificador"><input className={inputClass} value={activeCompany.id} disabled /></Field>
            <Field label="País"><input className={inputClass} value={activeCompany.country} disabled /></Field>
            <Field label="Moneda"><input className={inputClass} value={activeCompany.currency} disabled /></Field>
            <Field label="Tu rol"><input className={inputClass} value={roleLabels[(activeCompany.role as Role) ?? "readonly"] ?? activeCompany.role} disabled /></Field>
            <Field label="Estado"><input className={inputClass} value={activeCompany.is_active ? "Activa" : "Inactiva"} disabled /></Field>
          </div> : <p className="text-sm text-slate-500">No hay una empresa activa.</p>}
          <p className="mt-4 text-xs text-slate-500">Los datos legales ampliados se habilitarán cuando el backend incorpore edición de empresa.</p>
        </SectionCard>
        <SectionCard title="Cambiar empresa" description="Selecciona el tenant sobre el que trabajará Numera." icon={ShieldCheck}>
          <div className="space-y-3">{companies.data?.map((company) => <button key={company.id} disabled={company.selected || activateCompany.isPending} onClick={() => activateCompany.mutate(company.id)} className={`flex w-full items-center justify-between rounded-2xl border p-4 text-left ${company.selected ? "border-primary bg-primary/5" : "hover:bg-muted"}`}><div><p className="font-medium">{company.name}</p><p className="mt-1 text-sm text-slate-500">{company.country} · {company.currency} · {roleLabels[company.role as Role] ?? company.role}</p></div>{company.selected ? <Check className="text-primary"/> : <ChevronDown className="-rotate-90 text-slate-400"/>}</button>)}</div>
        </SectionCard>
      </div>}

      {tab === "users" && <SectionCard title="Usuarios y permisos" description="Gestiona quién puede acceder a la empresa y qué puede hacer." icon={UserCog}>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"><div><p className="text-sm text-slate-500">{members.data?.length ?? 0} usuarios vinculados</p></div>{canManageUsers && <button onClick={() => setInviteOpen((value) => !value)} className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground"><Plus size={16}/>Añadir usuario</button>}</div>
        {inviteOpen && <form onSubmit={(event: FormEvent) => { event.preventDefault(); addMember.mutate(); }} className="mt-5 grid gap-3 rounded-2xl border bg-muted/20 p-4 md:grid-cols-2"><input required className={inputClass} placeholder="Nombre y apellidos" value={inviteName} onChange={(e) => setInviteName(e.target.value)} /><input required type="email" className={inputClass} placeholder="usuario@empresa.com" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} /><input required minLength={8} type="password" className={inputClass} placeholder="Contraseña temporal (mín. 8)" value={invitePassword} onChange={(e) => setInvitePassword(e.target.value)} /><select className={inputClass} value={inviteRole} onChange={(e) => setInviteRole(e.target.value as Role)}>{ROLES.filter((r) => r !== "owner").map((role) => <option key={role} value={role}>{roleLabels[role]}</option>)}</select><div className="md:col-span-2 flex items-center justify-between gap-4"><p className="text-xs text-slate-500">La cuenta se crea ya vinculada a <strong>{activeCompany?.name}</strong>. El usuario solo tendrá que iniciar sesión.</p><button disabled={addMember.isPending} className="shrink-0 rounded-xl bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground">{addMember.isPending ? "Creando..." : "Crear usuario"}</button></div>{addMember.error instanceof Error && <p className="md:col-span-2 text-sm text-rose-600">{addMember.error.message}</p>}</form>}
        <div className="mt-6 overflow-x-auto"><table className="w-full min-w-[760px] text-left text-sm"><thead className="text-slate-500"><tr className="border-b"><th className="pb-3">Usuario</th><th className="pb-3">Rol</th><th className="pb-3">Estado</th><th className="pb-3 text-right">Acciones</th></tr></thead><tbody>{members.data?.map((member) => <tr key={member.id} className="border-b last:border-0"><td className="py-4"><p className="font-medium">{member.name}</p><p className="text-slate-500">{member.email}</p></td><td className="py-4">{canManageUsers ? <select className="rounded-lg border bg-background px-3 py-2" value={member.role} disabled={updateRole.isPending} onChange={(e) => updateRole.mutate({ userId: member.user_id, role: e.target.value as Role })}>{ROLES.map((role) => <option key={role} value={role}>{roleLabels[role]}</option>)}</select> : roleLabels[member.role as Role] ?? member.role}</td><td className="py-4"><span className={`rounded-full px-2.5 py-1 text-xs font-medium ${member.is_active ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-600"}`}>{member.is_active ? "Activo" : "Inactivo"}</span></td><td className="py-4 text-right">{canManageUsers && member.user_id !== me.data?.id && <button onClick={() => { if (window.confirm(`¿Eliminar el acceso de ${member.email}?`)) removeMember.mutate(member.user_id); }} className="inline-flex items-center gap-1 text-rose-600 hover:underline"><Trash2 size={15}/>Eliminar</button>}</td></tr>)}</tbody></table>{members.isLoading && <Loader2 className="mx-auto my-8 animate-spin text-primary"/>}{members.error instanceof Error && <p className="py-8 text-center text-sm text-rose-600">{members.error.message}</p>}</div>
      </SectionCard>}

      {tab === "accounting" && <SectionCard title="Preferencias contables" description="Valores por defecto que utilizará el motor contable en nuevas propuestas." icon={FileCog}>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3"><Field label="Plan contable"><select className={inputClass} value={accounting.chart} onChange={(e) => setAccounting({ ...accounting, chart: e.target.value })}><option>PGC España</option><option>PGC PYMES</option></select></Field><Field label="Cuenta de compras"><input className={inputClass} value={accounting.purchaseAccount} onChange={(e) => setAccounting({ ...accounting, purchaseAccount: e.target.value })}/></Field><Field label="Cuenta de proveedores"><input className={inputClass} value={accounting.supplierAccount} onChange={(e) => setAccounting({ ...accounting, supplierAccount: e.target.value })}/></Field><Field label="Cuenta de IVA soportado"><input className={inputClass} value={accounting.vatAccount} onChange={(e) => setAccounting({ ...accounting, vatAccount: e.target.value })}/></Field><Field label="Prefijo de asientos"><input className={inputClass} value={accounting.journalPrefix} onChange={(e) => setAccounting({ ...accounting, journalPrefix: e.target.value })}/></Field><Field label="Política de aprobación"><select className={inputClass} value={accounting.approvalMode} onChange={(e) => setAccounting({ ...accounting, approvalMode: e.target.value })}><option value="manual">Revisión manual</option><option value="confidence">Automática por confianza</option></select></Field></div><label className="mt-5 flex items-center gap-3 rounded-2xl border p-4"><input type="checkbox" checked={accounting.autoPost} onChange={(e) => setAccounting({ ...accounting, autoPost: e.target.checked })}/><span><span className="block font-medium">Contabilización automática</span><span className="text-sm text-slate-500">Publicar automáticamente los asientos aprobados.</span></span></label><div className="mt-6 flex justify-end"><button onClick={saveAccounting} className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground"><Save size={16}/>Guardar configuración</button></div>
      </SectionCard>}

      {tab === "preferences" && <div className="grid gap-6 xl:grid-cols-2"><SectionCard title="Apariencia y localización" description="Personaliza cómo se muestra Numera en este dispositivo." icon={Sun}><div className="grid gap-4 sm:grid-cols-2"><Field label="Tema"><div className="grid grid-cols-2 gap-2"><button onClick={() => setTheme("light")} className={`inline-flex items-center justify-center gap-2 rounded-xl border px-3 py-2.5 ${theme === "light" ? "border-primary bg-primary/5 text-primary" : ""}`}><Sun size={16}/>Claro</button><button onClick={() => setTheme("dark")} className={`inline-flex items-center justify-center gap-2 rounded-xl border px-3 py-2.5 ${theme === "dark" ? "border-primary bg-primary/5 text-primary" : ""}`}><Moon size={16}/>Oscuro</button></div></Field><Field label="Idioma"><select className={inputClass} value={preferences.language} onChange={(e) => setPreferences({ ...preferences, language: e.target.value })}><option value="es">Español</option><option value="en">English</option></select></Field><Field label="Formato de fecha"><select className={inputClass} value={preferences.dateFormat} onChange={(e) => setPreferences({ ...preferences, dateFormat: e.target.value })}><option>DD/MM/YYYY</option><option>YYYY-MM-DD</option></select></Field><Field label="Zona horaria"><select className={inputClass} value={preferences.timezone} onChange={(e) => setPreferences({ ...preferences, timezone: e.target.value })}><option>Europe/Madrid</option><option>UTC</option></select></Field></div></SectionCard><SectionCard title="Automatización y avisos" description="Controla los umbrales y notificaciones del flujo inteligente." icon={KeyRound}><Field label={`Confianza mínima OCR: ${preferences.ocrThreshold}%`}><input className="w-full accent-primary" type="range" min="50" max="100" value={preferences.ocrThreshold} onChange={(e) => setPreferences({ ...preferences, ocrThreshold: Number(e.target.value) })}/></Field><div className="mt-5 space-y-3">{[["emailNotifications", "Notificaciones por correo"], ["priceAlerts", "Alertas de variación de precios"], ["reviewNotifications", "Avisos del centro de revisión"]].map(([key, label]) => <label key={key} className="flex items-center justify-between rounded-2xl border p-4"><span className="text-sm font-medium">{label}</span><input type="checkbox" checked={Boolean(preferences[key as keyof typeof preferences])} onChange={(e) => setPreferences({ ...preferences, [key]: e.target.checked })}/></label>)}</div></SectionCard><div className="xl:col-span-2 flex justify-end"><button onClick={savePreferences} className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground"><Save size={16}/>Guardar preferencias</button></div></div>}

      {tab === "audit" && <SectionCard title="Registro de auditoría" description="Últimas acciones realizadas dentro de la empresa." icon={Activity}>{audit.isLoading ? <Loader2 className="mx-auto my-12 animate-spin text-primary"/> : audit.error instanceof Error ? <p className="py-10 text-center text-sm text-rose-600">{audit.error.message}</p> : <div className="space-y-3">{audit.data?.map((row) => <div key={row.id} className="flex flex-col gap-2 rounded-2xl border p-4 sm:flex-row sm:items-center sm:justify-between"><div><p className="font-medium">{row.action}</p><p className="mt-1 text-sm text-slate-500">{row.entity_type}{row.entity_id ? ` · ${row.entity_id}` : ""}</p></div><p className="text-sm text-slate-500">{new Date(row.created_at).toLocaleString("es-ES")}</p></div>)}{!audit.data?.length && <p className="py-12 text-center text-sm text-slate-500">No hay actividad registrada.</p>}</div>}</SectionCard>}
    </div>
  );
}
