import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEffect } from "react";
import { toneSurface, toneText } from "../../base/tone";
import { useStore, useToastDismissal } from "../../share/store";
import type { ToastEvent } from "../../share/types";
import { describeToast } from "./describeToast";

const TOAST_LIFETIME_MS = 4000;

const timeFormat = new Intl.DateTimeFormat(undefined, {
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
});

export function ToastStack() {
  const { toasts } = useStore();

  return (
    <div className="pointer-events-none fixed right-4 bottom-4 z-30 flex w-80 flex-col gap-2">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} />
      ))}
    </div>
  );
}

function Toast({ toast }: { toast: ToastEvent }) {
  const dismiss = useToastDismissal();
  const { icon, tone, text } = describeToast(toast);

  useEffect(() => {
    const timer = window.setTimeout(() => dismiss(toast.id), TOAST_LIFETIME_MS);
    return () => window.clearTimeout(timer);
  }, [dismiss, toast.id]);

  return (
    <div className="pointer-events-auto flex animate-fade-in items-center gap-3 rounded-lg border border-border bg-surface-raised px-3 py-2.5 shadow-card">
      <span className={`flex size-7 shrink-0 items-center justify-center rounded-md border ${toneSurface[tone]}`}>
        <FontAwesomeIcon icon={icon} className="text-[12px]" />
      </span>
      <span className={`flex-1 text-[14px] font-medium ${tone === "accent" ? "text-foreground" : toneText[tone]}`}>
        {text}
      </span>
      <span className="numeric text-[12px] text-muted">{timeFormat.format(new Date(toast.at))}</span>
    </div>
  );
}
