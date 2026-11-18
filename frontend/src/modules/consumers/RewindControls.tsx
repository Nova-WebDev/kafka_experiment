import { faAngleLeft, faAnglesLeft, faBackwardFast, faLocationCrosshairs } from "@fortawesome/free-solid-svg-icons";
import { useState, type FormEvent } from "react";
import { IconButton } from "../../base/IconButton";
import { TextInput } from "../../base/TextInput";
import { apiClient } from "../../share/apiClient";

interface RewindControlsProps {
  consumerId: string;
  partition: number;
  position: number | null;
}

export function RewindControls({ consumerId, partition, position }: RewindControlsProps) {
  const [editing, setEditing] = useState(false);
  const [target, setTarget] = useState("");
  const disabled = position === null;

  const seek = (offset: number) => void apiClient.seekConsumer(consumerId, partition, Math.max(0, offset));

  const submitTarget = (event: FormEvent) => {
    event.preventDefault();
    const offset = Number(target);
    if (Number.isInteger(offset) && offset >= 0) {
      seek(offset);
    }
    setTarget("");
    setEditing(false);
  };

  return (
    <div
      className={`absolute inset-y-0 right-2 flex items-center gap-1 bg-surface-raised pl-2 transition-opacity duration-150 group-hover:opacity-100 focus-within:opacity-100 ${editing ? "opacity-100" : "pointer-events-none opacity-0 group-hover:pointer-events-auto"}`}
    >
      <IconButton size="sm" icon={faAngleLeft} label="Rewind 1" disabled={disabled} onClick={() => seek((position ?? 0) - 1)} />
      <IconButton
        size="sm"
        icon={faAnglesLeft}
        label="Rewind 10"
        disabled={disabled}
        onClick={() => seek((position ?? 0) - 10)}
      />
      <IconButton size="sm" icon={faBackwardFast} label="Rewind to 0" disabled={disabled} onClick={() => seek(0)} />
      {editing ? (
        <form onSubmit={submitTarget}>
          <TextInput
            compact
            autoFocus
            type="number"
            min={0}
            value={target}
            onChange={(event) => setTarget(event.target.value)}
            onBlur={() => setEditing(false)}
            onKeyDown={(event) => event.key === "Escape" && setEditing(false)}
            placeholder="offset"
            aria-label={`Seek P${partition} to offset`}
            className="numeric w-20 text-right"
          />
        </form>
      ) : (
        <IconButton
          size="sm"
          icon={faLocationCrosshairs}
          label="Seek to offset"
          disabled={disabled}
          onClick={() => setEditing(true)}
        />
      )}
    </div>
  );
}
