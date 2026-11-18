interface SwitchProps {
  checked: boolean;
  label: string;
  disabled?: boolean;
  onChange: (checked: boolean) => void;
}

export function Switch({ checked, label, disabled = false, onChange }: SwitchProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      title={label}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-5 w-9 shrink-0 items-center rounded-full border transition-colors duration-200 disabled:opacity-40 ${checked ? "border-accent bg-accent" : "border-border bg-surface-raised"}`}
    >
      <span
        className={`inline-block size-3.5 rounded-full shadow-sm transition-transform duration-200 ${checked ? "translate-x-[18px] bg-on-accent" : "translate-x-[2px] bg-muted"}`}
      />
    </button>
  );
}
