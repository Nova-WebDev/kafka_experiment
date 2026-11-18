export const CONSUMER_DELAY_MS = { initial: 500, max: 5000, step: 100 } as const;

export const AUTO_PRODUCER_RATE = { initial: 2, min: 0.5, max: 50, step: 0.5 } as const;

export function isValidDelay(delayMs: number): boolean {
  return Number.isInteger(delayMs) && delayMs >= 0 && delayMs <= CONSUMER_DELAY_MS.max;
}

export function isValidRate(ratePerSec: number): boolean {
  return Number.isFinite(ratePerSec) && ratePerSec > 0 && ratePerSec <= AUTO_PRODUCER_RATE.max;
}
