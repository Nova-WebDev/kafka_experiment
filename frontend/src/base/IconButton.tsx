import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import type { ButtonHTMLAttributes } from "react";
import { toneText, type Tone } from "./tone";

interface IconButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "children"> {
  icon: IconDefinition;
  label: string;
  tone?: Tone;
  size?: "sm" | "md";
}

const sizeClasses = {
  sm: "size-7 text-[11px]",
  md: "size-8 text-[13px]",
};

export function IconButton({ icon, label, tone = "neutral", size = "md", className = "", ...props }: IconButtonProps) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      className={`inline-flex shrink-0 items-center justify-center rounded-md border border-border bg-surface-raised transition-colors duration-150 hover:border-accent/60 hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40 ${sizeClasses[size]} ${toneText[tone]} ${className}`}
      {...props}
    >
      <FontAwesomeIcon icon={icon} />
    </button>
  );
}
