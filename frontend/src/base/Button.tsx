import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import type { ButtonHTMLAttributes } from "react";

type ButtonVariant = "primary" | "secondary";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  icon?: IconDefinition;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: "border-accent bg-accent text-on-accent hover:brightness-110",
  secondary: "border-border bg-surface-raised text-foreground hover:border-accent/60",
};

export function Button({ variant = "secondary", icon, className = "", children, ...props }: ButtonProps) {
  return (
    <button
      type="button"
      className={`inline-flex h-8 shrink-0 items-center justify-center gap-1.5 rounded-md border px-3 text-[13px] font-semibold transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-40 ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {icon && <FontAwesomeIcon icon={icon} className="text-[12px]" />}
      {children}
    </button>
  );
}
