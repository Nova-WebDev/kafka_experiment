import { useCallback, useState } from "react";

export function usePendingAction(): [boolean, (action: () => Promise<unknown>) => Promise<void>] {
  const [pending, setPending] = useState(false);

  const run = useCallback(async (action: () => Promise<unknown>) => {
    setPending(true);
    try {
      await action();
    } finally {
      setPending(false);
    }
  }, []);

  return [pending, run];
}
