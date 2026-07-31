import { cn } from "@/lib/utils";

const styles: Record<string, string> = {
  proposed: "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300",
  approved: "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300",
  posted: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
  completed: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
  rejected: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300",
  failed: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300"
};

export function StatusBadge({ status }: { status: string }) {
  return <span className={cn("rounded-full px-3 py-1 text-xs font-medium", styles[status.toLowerCase()] ?? "bg-muted")}>{status}</span>;
}
