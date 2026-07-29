export function PlaceholderPage({
  title, description, action
}: {
  title: string; description: string; action?: React.ReactNode
}) {
  return (
    <div className="space-y-7">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
          <p className="mt-2 text-slate-500 dark:text-slate-400">{description}</p>
        </div>
        {action}
      </div>

      <section className="grid min-h-[420px] place-items-center rounded-3xl border border-dashed bg-card p-8 text-center shadow-soft">
        <div>
          <div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-muted font-semibold">N</div>
          <h2 className="mt-5 text-lg font-semibold">Pantalla preparada</h2>
          <p className="mx-auto mt-2 max-w-md text-sm text-slate-500 dark:text-slate-400">
            La navegación y el diseño base ya están listos. La funcionalidad completa se conectará al backend en los siguientes sprints.
          </p>
        </div>
      </section>
    </div>
  );
}
