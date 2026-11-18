import { faPaperPlane } from "@fortawesome/free-solid-svg-icons";
import { useState, type FormEvent } from "react";
import { Button } from "../../base/Button";
import { TextInput } from "../../base/TextInput";
import { apiClient } from "../../share/apiClient";
import { usePendingAction } from "../../share/usePendingAction";

export function SendForm() {
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");
  const [sending, run] = usePendingAction();

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!value.trim()) {
      return;
    }
    await run(async () => {
      await apiClient.sendMessage(key.trim() || null, value);
      setValue("");
    });
  };

  return (
    <form onSubmit={submit} className="flex min-w-0 flex-1 items-center gap-2">
      <TextInput
        value={key}
        onChange={(event) => setKey(event.target.value)}
        placeholder="key"
        aria-label="Message key"
        className="numeric w-16"
      />
      <TextInput
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="value"
        aria-label="Message value"
        className="numeric flex-1"
      />
      <Button type="submit" variant="primary" icon={faPaperPlane} disabled={sending || !value.trim()}>
        Send
      </Button>
    </form>
  );
}
