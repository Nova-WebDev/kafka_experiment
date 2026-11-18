import { toneFill, type Tone } from "./tone";

interface StatusDotProps {
  tone: Tone;
  pulse?: boolean;
}

export function StatusDot({ tone, pulse = false }: StatusDotProps) {
  return (
    <span className="relative inline-flex size-2.5 shrink-0">
      {pulse && <span className={`absolute inset-0 animate-ping rounded-full opacity-60 ${toneFill[tone]}`} />}
      <span
        className={`relative inline-flex size-2.5 rounded-full transition-colors duration-200 dark:shadow-[0_0_8px_currentColor] ${toneFill[tone]}`}
      />
    </span>
  );
}
