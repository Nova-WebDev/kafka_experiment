import type { ReactNode } from "react";
import { toneSurface, type Tone } from "./tone";

interface PillProps {
  tone?: Tone;
  title?: string;
  children: ReactNode;
}

export function Pill({ tone = "neutral", title, children }: PillProps) {
  return (
    <span
      title={title}
      className={`inline-flex h-7 items-center gap-1.5 rounded-full border px-2.5 text-[13px] font-medium whitespace-nowrap transition-colors duration-200 ${toneSurface[tone]}`}
    >
      {children}
    </span>
  );
}
