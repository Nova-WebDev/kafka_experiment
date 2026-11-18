import { NumberTicker } from "../../base/NumberTicker";
import type { PartitionProgress } from "../../share/types";
import { RewindControls } from "./RewindControls";

const NOTABLE_LAG = 10;

function lagColor(lag: number | null): string {
  if (lag === null || lag === 0) {
    return "text-success";
  }
  return lag >= NOTABLE_LAG ? "text-warning" : "text-foreground";
}

function progressRatio({ position, high_watermark: highWatermark }: PartitionProgress): number {
  if (highWatermark === null || position === null) {
    return 0;
  }
  if (highWatermark === 0) {
    return 1;
  }
  return Math.min(1, position / highWatermark);
}

function progressTooltip(progress: PartitionProgress): string {
  const show = (value: number | null) => (value === null ? "—" : String(value));
  return `Committed ${show(progress.committed)} · High watermark ${show(progress.high_watermark)}`;
}

export function PartitionProgressRow({ consumerId, progress }: { consumerId: string; progress: PartitionProgress }) {
  return (
    <div className="group relative flex h-11 items-center gap-3 px-3">
      <span className="numeric w-7 text-[14px] font-bold text-accent">P{progress.partition}</span>
      <NumberTicker value={progress.position} className="w-16 text-right text-xl font-semibold" />
      <div className="flex-1 py-2" title={progressTooltip(progress)}>
        <div className="h-1.5 overflow-hidden rounded-full bg-border">
          <div
            className="h-full rounded-full bg-accent transition-[width] duration-200 ease-out"
            style={{ width: `${progressRatio(progress) * 100}%` }}
          />
        </div>
      </div>
      <span className="flex w-16 items-baseline justify-end gap-1.5 text-[12px] text-muted">
        lag
        <NumberTicker value={progress.lag} className={`text-[15px] font-semibold ${lagColor(progress.lag)}`} />
      </span>
      <RewindControls consumerId={consumerId} partition={progress.partition} position={progress.position} />
    </div>
  );
}
