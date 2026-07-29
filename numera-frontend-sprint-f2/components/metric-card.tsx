import type { LucideIcon } from "lucide-react";

export function MetricCard({
  title, value, change, icon: Icon
}: {
  title: string; value: string; change: string; icon: LucideIcon
}) {
  return (
    <article className="rounded-3xl border bg-card p-5 shadow-soft">
      <div className="flex items-start justify-between">
        <div className="grid h-11 w-11 place-items-center rounded-2xl bg-muted">
          <Icon size={20} />
        </div>
        <span className="text-xs font-medium text-slate-500 dark:text-slate-400">{change}</span>
      </div>
      <p className="mt-6 text-sm text-slate-500 dark:text-slate-400">{title}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </article>
  );
}
