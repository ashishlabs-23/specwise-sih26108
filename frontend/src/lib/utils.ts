import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDecisionLabel(decision: string): string {
  switch (decision) {
    case "RECOMMEND":
      return "RECOMMEND";
    case "REVIEW":
      return "REVIEW NEEDED";
    case "ABSTAIN":
      return "INSUFFICIENT DATA (ABSTAIN)";
    case "OUT_OF_CORPUS":
      return "OUT OF SCOPE / CORPUS";
    default:
      return decision;
  }
}

export function getDecisionTheme(decision: string) {
  switch (decision) {
    case "RECOMMEND":
      return {
        bg: "bg-[#EAF8F0]",
        border: "border-[#A3E6C0]",
        text: "text-[#0F7642]",
        badgeBg: "bg-[#16A34A]",
        badgeText: "text-white",
        lightBadge: "bg-[#D1F2DF] text-[#0E6238]",
        iconColor: "text-[#16A34A]",
      };
    case "REVIEW":
      return {
        bg: "bg-[#FFFBEB]",
        border: "border-[#FDE68A]",
        text: "text-[#B45309]",
        badgeBg: "bg-[#D97706]",
        badgeText: "text-white",
        lightBadge: "bg-[#FEF3C7] text-[#92400E]",
        iconColor: "text-[#D97706]",
      };
    case "ABSTAIN":
      return {
        bg: "bg-[#F8FAFC]",
        border: "border-[#CBD5E1]",
        text: "text-[#475569]",
        badgeBg: "bg-[#64748B]",
        badgeText: "text-white",
        lightBadge: "bg-[#E2E8F0] text-[#334155]",
        iconColor: "text-[#64748B]",
      };
    case "OUT_OF_CORPUS":
      return {
        bg: "bg-[#FAF5FF]",
        border: "border-[#E9D5FF]",
        text: "text-[#7E22CE]",
        badgeBg: "bg-[#9333EA]",
        badgeText: "text-white",
        lightBadge: "bg-[#F3E8FF] text-[#6B21A8]",
        iconColor: "text-[#9333EA]",
      };
    default:
      return {
        bg: "bg-gray-50",
        border: "border-gray-200",
        text: "text-gray-800",
        badgeBg: "bg-gray-600",
        badgeText: "text-white",
        lightBadge: "bg-gray-100 text-gray-800",
        iconColor: "text-gray-600",
      };
  }
}
