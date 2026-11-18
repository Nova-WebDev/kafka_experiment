import type { ReactNode } from "react";

interface PanelProps {
  title: ReactNode;
  actions?: ReactNode;
  className?: string;
  bodyClassName?: string;
  children: ReactNode;
}

export function Panel({ title, actions, className = "", bodyClassName = "", children }: PanelProps) {
  return (
    <section className={`flex min-h-0 flex-col rounded-xl border border-border bg-surface shadow-card ${className}`}>
      <header className="flex h-11 shrink-0 items-center justify-between gap-3 border-b border-border px-4">
        <h2 className="text-[13px] font-semibold tracking-wider text-muted uppercase">{title}</h2>
        {actions}
      </header>
      <div className={`min-h-0 flex-1 ${bodyClassName}`}>{children}</div>
    </section>
  );
}
