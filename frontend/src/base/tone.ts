export type Tone = "neutral" | "accent" | "ok" | "warn" | "danger";

export const toneText: Record<Tone, string> = {
  neutral: "text-muted",
  accent: "text-accent",
  ok: "text-success",
  warn: "text-warning",
  danger: "text-danger",
};

export const toneSurface: Record<Tone, string> = {
  neutral: "border-border bg-surface-raised text-foreground",
  accent: "border-accent/35 bg-accent/10 text-accent",
  ok: "border-success/35 bg-success/10 text-success",
  warn: "border-warning/40 bg-warning/10 text-warning",
  danger: "border-danger/40 bg-danger/10 text-danger",
};

export const toneFill: Record<Tone, string> = {
  neutral: "bg-muted text-muted",
  accent: "bg-accent text-accent",
  ok: "bg-success text-success",
  warn: "bg-warning text-warning",
  danger: "bg-danger text-danger",
};
