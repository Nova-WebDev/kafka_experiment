import { faRotateRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Button } from "../../base/Button";
import { Pill } from "../../base/Pill";
import { apiClient } from "../../share/apiClient";
import type { PendingReconnect } from "../../share/types";
import { useNow } from "../../share/useNow";
import { usePendingAction } from "../../share/usePendingAction";

export function ReconnectStatus({ reconnects }: { reconnects: PendingReconnect[] }) {
  const now = useNow(reconnects.length > 0);
  const [requesting, run] = usePendingAction();

  if (reconnects.length === 0) {
    return null;
  }

  const next = reconnects.reduce((soonest, candidate) => (candidate.deadline < soonest.deadline ? candidate : soonest));
  const secondsLeft = Math.max(0, Math.ceil((next.deadline - now) / 1000));

  return (
    <div className="flex items-center gap-2">
      <Pill tone="warn" title={`Attempt ${next.attempt}`}>
        <FontAwesomeIcon icon={faRotateRight} spin />
        Reconnecting
        <span className="numeric font-semibold">{secondsLeft}s</span>
      </Pill>
      <Button variant="primary" disabled={requesting} onClick={() => run(apiClient.retryNow)}>
        Retry now
      </Button>
    </div>
  );
}
