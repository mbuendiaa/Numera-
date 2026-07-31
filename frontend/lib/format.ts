const spanishDate = new Intl.DateTimeFormat("es-ES");

export function formatDate(value?: string | null): string {
  if (!value || typeof value !== "string") return "—";

  const normalized = value.trim();
  if (!normalized || normalized === "0000-00-00" || normalized.toLowerCase() === "none") {
    return "—";
  }

  const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(normalized);
  const parsed = dateOnly
    ? new Date(Number(dateOnly[1]), Number(dateOnly[2]) - 1, Number(dateOnly[3]))
    : new Date(normalized);

  return Number.isNaN(parsed.getTime()) ? "—" : spanishDate.format(parsed);
}
