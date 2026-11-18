interface NumberTickerProps {
  value: number | null;
  className?: string;
}

export function NumberTicker({ value, className = "" }: NumberTickerProps) {
  return (
    <span key={value ?? "none"} className={`numeric inline-block animate-flash rounded px-0.5 ${className}`}>
      {value ?? "—"}
    </span>
  );
}
