import {
  faBolt,
  faHand,
  faTriangleExclamation,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { KeyBadge } from "../../base/KeyBadge";
import { useStore } from "../../share/store";
import type { SendEvent } from "../../share/types";

export function RecentSends() {
  const { sends } = useStore();

  return (
    <ol className="min-h-0 flex-1 divide-y divide-border overflow-y-auto">
      {sends.map((send) => (
        <SendRow key={send.id} send={send} />
      ))}
    </ol>
  );
}

function SendRow({ send }: { send: SendEvent }) {
  const failed = send.type === "producer.failed";

  return (
    <li
      className={`flex h-10 animate-fade-in items-center gap-3 px-4 ${failed ? "bg-danger/8" : ""}`}
    >
      <FontAwesomeIcon
        icon={
          failed
            ? faTriangleExclamation
            : send.payload.source === "auto"
              ? faBolt
              : faHand
        }
        title={send.payload.source === "auto" ? "Auto-producer" : "Manual send"}
        className={`w-3.5 text-[12px] ${failed ? "text-danger" : "text-muted"}`}
      />
      <KeyBadge value={send.payload.key} />
      {send.type === "producer.sent" ? (
        <span className="numeric text-[14px]">
          <span className="font-semibold text-accent">
            P{send.payload.partition}
          </span>
          <span className="text-muted">@</span>
          <span className="font-semibold">{send.payload.offset}</span>
        </span>
      ) : (
        <span className="numeric truncate text-[13px] font-semibold text-danger">
          {send.payload.error}
        </span>
      )}
      <span
        className={`numeric ml-auto text-[13px] ${failed ? "text-danger" : "text-muted"}`}
      >
        {Math.round(send.payload.latency_ms)} ms
      </span>
    </li>
  );
}
