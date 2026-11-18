export function KeyBadge({ value }: { value: string | null }) {
  return (
    <span className="numeric inline-flex h-5 min-w-12 shrink-0 items-center justify-center rounded border border-border bg-background px-1.5 text-[12px] font-medium text-foreground">
      {value ?? "—"}
    </span>
  );
}
