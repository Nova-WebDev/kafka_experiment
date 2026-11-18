import { faStopwatch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";
import { TextInput } from "../../base/TextInput";
import { apiClient } from "../../share/apiClient";
import { CONSUMER_DELAY_MS, isValidDelay } from "../../share/limits";

export function DelayControl({ consumerId, delayMs }: { consumerId: string; delayMs: number }) {
  const [draft, setDraft] = useState<string | null>(null);
  const shown = draft ?? String(delayMs);

  const commit = () => {
    const parsed = Number(shown);
    setDraft(null);
    if (isValidDelay(parsed) && parsed !== delayMs) {
      void apiClient.setConsumerDelay(consumerId, parsed);
    }
  };

  return (
    <label className="ml-auto flex shrink-0 items-center gap-1.5 text-[12px] text-muted">
      <FontAwesomeIcon icon={faStopwatch} title="Processing delay" />
      <TextInput
        compact
        type="number"
        min={0}
        max={CONSUMER_DELAY_MS.max}
        step={CONSUMER_DELAY_MS.step}
        value={shown}
        onChange={(event) => setDraft(event.target.value)}
        onBlur={commit}
        onKeyDown={(event) => event.key === "Enter" && commit()}
        aria-label="Processing delay in milliseconds"
        className="numeric w-16 text-right"
      />
      ms
    </label>
  );
}
