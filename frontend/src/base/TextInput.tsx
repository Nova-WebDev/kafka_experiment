import type { InputHTMLAttributes } from "react";

interface TextInputProps extends InputHTMLAttributes<HTMLInputElement> {
  compact?: boolean;
}

export function TextInput({ compact = false, className = "", ...props }: TextInputProps) {
  const sizing = compact ? "h-7 px-1.5 text-[13px]" : "h-8 px-2.5 text-sm";
  return (
    <input
      className={`min-w-0 rounded-md border border-border bg-background text-foreground transition-colors duration-150 placeholder:text-muted focus:border-accent focus:outline-none ${sizing} ${className}`}
      {...props}
    />
  );
}
