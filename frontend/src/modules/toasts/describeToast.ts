import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { faArrowDown, faArrowUp, faCrown, faLock, faLockOpen, faShuffle } from "@fortawesome/free-solid-svg-icons";
import type { Tone } from "../../base/tone";
import type { ToastEvent } from "../../share/types";

interface ToastDescription {
  icon: IconDefinition;
  tone: Tone;
  text: string;
}

export function describeToast(event: ToastEvent): ToastDescription {
  switch (event.type) {
    case "broker.down":
      return { icon: faArrowDown, tone: "danger", text: `Broker ${event.payload.broker_id} down` };
    case "broker.up":
      return { icon: faArrowUp, tone: "ok", text: `Broker ${event.payload.broker_id} up` };
    case "leader.changed": {
      const { partition, previous_leader: previous, leader } = event.payload;
      if (leader === null) {
        return { icon: faShuffle, tone: "danger", text: `P${partition} has no leader` };
      }
      return { icon: faShuffle, tone: "accent", text: `P${partition} leader ${previous ?? "—"} → ${leader}` };
    }
    case "controller.changed": {
      const { previous_controller_id: previous, controller_id: current } = event.payload;
      if (current === null) {
        return { icon: faCrown, tone: "danger", text: `Controller #${previous} lost` };
      }
      return {
        icon: faCrown,
        tone: "accent",
        text: previous === null ? `Controller #${current} elected` : `Controller #${previous} → #${current}`,
      };
    }
    case "writes.blocked":
      return { icon: faLock, tone: "danger", text: "Writes blocked" };
    case "writes.restored":
      return { icon: faLockOpen, tone: "ok", text: "Writes restored" };
  }
}
