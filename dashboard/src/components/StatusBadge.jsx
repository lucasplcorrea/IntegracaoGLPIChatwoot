const STATUS_MAP = {
  resolved: { label: "Resolvida", cls: "badge-resolved" },
  open:     { label: "Aberta",    cls: "badge-open" },
  pending:  { label: "Pendente",  cls: "badge-pending" },
  snoozed:  { label: "Adiada",    cls: "badge-snoozed" },
};

export function StatusBadge({ status }) {
  const cfg = STATUS_MAP[status] ?? { label: status ?? "–", cls: "badge-default" };
  return <span className={`badge ${cfg.cls}`}>{cfg.label}</span>;
}
