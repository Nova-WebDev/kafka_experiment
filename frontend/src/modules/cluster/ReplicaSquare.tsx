export type ReplicaRole = "leader" | "in-sync" | "out-of-sync" | "none";

interface ReplicaSquareProps {
  brokerId: number;
  role: ReplicaRole;
  alive: boolean;
}

const roleTitle: Record<ReplicaRole, string> = {
  leader: "leader",
  "in-sync": "in sync",
  "out-of-sync": "out of sync",
  none: "not a replica",
};

function squareClasses(role: ReplicaRole, alive: boolean): string {
  switch (role) {
    case "leader":
      return alive
        ? "border-accent bg-accent text-on-accent ring-2 ring-accent/40 ring-offset-2 ring-offset-surface"
        : "border-danger bg-accent text-on-accent ring-2 ring-danger/50 ring-offset-2 ring-offset-surface";
    case "in-sync":
      return alive ? "border-transparent bg-foreground/15 text-foreground" : "border-warning/60 bg-warning/15 text-warning";
    case "out-of-sync":
      return "border-danger/80 bg-transparent text-danger";
    case "none":
      return "border-dashed border-border bg-transparent text-muted";
  }
}

export function ReplicaSquare({ brokerId, role, alive }: ReplicaSquareProps) {
  return (
    <span
      title={`Broker ${brokerId}: ${roleTitle[role]}`}
      className={`numeric flex size-7 items-center justify-center rounded-md border text-[13px] font-semibold transition-all duration-200 ${squareClasses(role, alive)}`}
    >
      {brokerId}
    </span>
  );
}
