import { faStopwatch, faUserPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState, type FormEvent } from "react";
import { Button } from "../../base/Button";
import { TextInput } from "../../base/TextInput";
import { apiClient } from "../../share/apiClient";
import { CONSUMER_DELAY_MS, isValidDelay } from "../../share/limits";
import { usePendingAction } from "../../share/usePendingAction";

const NEW_GROUP = "";

export function AddConsumerControl({ groupIds }: { groupIds: string[] }) {
  const [groupId, setGroupId] = useState(NEW_GROUP);
  const [delayMs, setDelayMs] = useState(String(CONSUMER_DELAY_MS.initial));
  const [creating, run] = usePendingAction();

  const selectedGroup = groupIds.includes(groupId) ? groupId : NEW_GROUP;
  const parsedDelay = Number(delayMs);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    await run(() => apiClient.createConsumer(selectedGroup || null, parsedDelay));
  };

  return (
    <form onSubmit={submit} className="flex items-center gap-2">
      <select
        value={selectedGroup}
        onChange={(event) => setGroupId(event.target.value)}
        aria-label="Consumer group"
        className="numeric h-8 rounded-md border border-border bg-background px-2 text-[13px] text-foreground focus:border-accent focus:outline-none"
      >
        <option value={NEW_GROUP}>new group</option>
        {groupIds.map((id) => (
          <option key={id} value={id}>
            join {id}
          </option>
        ))}
      </select>
      <FontAwesomeIcon icon={faStopwatch} title="Processing delay" className="text-[13px] text-muted" />
      <TextInput
        type="number"
        min={0}
        max={CONSUMER_DELAY_MS.max}
        step={CONSUMER_DELAY_MS.step}
        value={delayMs}
        onChange={(event) => setDelayMs(event.target.value)}
        aria-label="Processing delay in milliseconds"
        className="numeric w-20 text-right"
      />
      <span className="text-[13px] text-muted">ms</span>
      <Button type="submit" variant="primary" icon={faUserPlus} disabled={creating || !isValidDelay(parsedDelay)}>
        Add consumer
      </Button>
    </form>
  );
}
