import { KeyBadge } from "../../base/KeyBadge";
import { summarizeValue } from "../../share/summarizeValue";
import type { ConsumedMessageEvent } from "../../share/types";

export function MessageFeed({ messages }: { messages: ConsumedMessageEvent[] }) {
  return (
    <ol className="flex flex-col py-1">
      {messages.map((message) => (
        <li key={message.id} className="flex h-7 animate-fade-in items-center gap-2.5 px-3">
          <span className="numeric w-16 shrink-0 text-[13px]">
            <span className="font-semibold text-accent">P{message.payload.partition}</span>
            <span className="text-muted">@</span>
            <span className="font-semibold">{message.payload.offset}</span>
          </span>
          <KeyBadge value={message.payload.key} />
          <span className="min-w-0 flex-1 truncate text-[13px] text-muted">{summarizeValue(message.payload.value)}</span>
          {message.payload.replayed && (
            <span className="shrink-0 rounded border border-accent-secondary/40 bg-accent-secondary/10 px-1.5 text-[12px] font-medium text-accent-secondary">
              replayed
            </span>
          )}
        </li>
      ))}
    </ol>
  );
}
