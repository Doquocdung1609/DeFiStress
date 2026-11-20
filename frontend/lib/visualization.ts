export type WarningLevel = "NORMAL" | "WATCH" | "HIGH" | "ABSTAIN";

const warningPresentation: Record<WarningLevel, { description: string; tone: string }> = {
  NORMAL: { description: "Chưa ghi nhận tín hiệu vượt ngưỡng.", tone: "normal" },
  WATCH: { description: "Có dấu hiệu căng thẳng cần theo dõi.", tone: "watch" },
  HIGH: { description: "Tín hiệu đã vượt ngưỡng rủi ro cao.", tone: "high" },
  ABSTAIN: { description: "Chưa đủ dữ liệu để đưa ra đánh giá.", tone: "abstain" },
};

export function warningStatus(level: string): { label: string; description: string; tone: string } {
  if (Object.hasOwn(warningPresentation, level)) {
    return { label: level, ...warningPresentation[level as WarningLevel] };
  }
  return { label: level || "UNKNOWN", description: "Trạng thái do API trả về chưa được nhận diện.", tone: "unknown" };
}

export function formatHealthFactor(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value) || value < 0) return "—";
  const scaled = value < 1 ? Math.floor(value * 1000) / 1000 : value;
  return scaled.toFixed(3);
}

export function healthFactorStatus(value: number | null | undefined): "liquidation-threshold" | "low-buffer" | "relative-buffer" | "unknown" {
  if (value == null || !Number.isFinite(value) || value < 0) return "unknown";
  if (value <= 1) return "liquidation-threshold";
  if (value < 1.2) return "low-buffer";
  return "relative-buffer";
}

export function parseFiniteAmount(value: string | number | null | undefined): number | null {
  if (value == null || (typeof value === "string" && value.trim() === "")) return null;
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
}

export function formatFinancial(value: string | number | null | undefined, currency = "USD"): string {
  if (value == null || value === "") return "—";
  const amount = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(amount)) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 6,
  }).format(amount);
}

export function exitFillPercent(filled: string | number | null | undefined, unfilled: string | number | null | undefined): number | null {
  const filledAmount = parseFiniteAmount(filled);
  const unfilledAmount = parseFiniteAmount(unfilled);
  if (filledAmount == null || unfilledAmount == null) return null;
  const total = filledAmount + unfilledAmount;
  if (total <= 0) return null;
  return (filledAmount / total) * 100;
}
