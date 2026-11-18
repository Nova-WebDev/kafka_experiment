interface OrderSummary {
  orderId?: unknown;
  product?: unknown;
  amount?: unknown;
  currency?: unknown;
}

export function summarizeValue(value: string): string {
  try {
    const order = JSON.parse(value) as OrderSummary;
    if (typeof order.orderId === "string") {
      return `${order.orderId} · ${order.product} · ${order.amount} ${order.currency}`;
    }
  } catch {
    return value;
  }
  return value;
}
