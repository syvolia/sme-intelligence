import { Box } from "@mui/material";

type Tone = "healthy" | "low" | "critical" | "info" | "neutral";

const TONES: Record<Tone, { bg: string; fg: string; dot: string }> = {
  healthy: { bg: "#DCFCE7", fg: "#166534", dot: "#16A34A" },
  low: { bg: "#FEF3C7", fg: "#92400E", dot: "#D97706" },
  critical: { bg: "#FEE2E2", fg: "#991B1B", dot: "#DC2626" },
  info: { bg: "#E0E7FF", fg: "#3730A3", dot: "#4F46E5" },
  neutral: { bg: "#F1F5F9", fg: "#334155", dot: "#64748B" },
};

interface Props {
  tone?: Tone;
  label: string;
  size?: "sm" | "md";
}

export function StatusPill({ tone = "neutral", label, size = "sm" }: Props) {
  const t = TONES[tone];
  return (
    <Box
      component="span"
      sx={{
        display: "inline-flex",
        alignItems: "center",
        gap: 0.75,
        px: size === "sm" ? 1 : 1.25,
        py: size === "sm" ? 0.25 : 0.5,
        borderRadius: 999,
        backgroundColor: t.bg,
        color: t.fg,
        fontSize: size === "sm" ? 11 : 12,
        fontWeight: 600,
        letterSpacing: "0.02em",
        textTransform: "uppercase",
      }}
    >
      <Box
        component="span"
        sx={{
          width: 6,
          height: 6,
          borderRadius: "50%",
          backgroundColor: t.dot,
        }}
      />
      {label}
    </Box>
  );
}

export function riskTone(risk: string): Tone {
  if (risk === "HIGH") return "critical";
  if (risk === "MEDIUM") return "low";
  if (risk === "LOW") return "healthy";
  return "neutral";
}

export function priorityTone(priority: string): Tone {
  if (priority === "high") return "critical";
  if (priority === "medium") return "low";
  return "info";
}

export function inventoryRiskTone(risk: string): Tone {
  if (risk === "CRITICAL") return "critical";
  if (risk === "LOW") return "low";
  if (risk === "HEALTHY") return "healthy";
  return "neutral";
}

export function inventoryRiskLabel(risk: string): string {
  if (risk === "CRITICAL") return "Critical";
  if (risk === "LOW") return "Low";
  if (risk === "HEALTHY") return "Healthy";
  return risk;
}
