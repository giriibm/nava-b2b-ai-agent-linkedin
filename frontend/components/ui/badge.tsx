import { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const colorForStatus: Record<string, string> = {
  discovered: "bg-gray-100 text-gray-700",
  researched: "bg-blue-100 text-blue-700",
  scored: "bg-purple-100 text-purple-700",
  approved: "bg-green-100 text-green-700",
  contacted: "bg-amber-100 text-amber-700",
  replied: "bg-teal-100 text-teal-700",
  converted: "bg-emerald-100 text-emerald-700",
  draft: "bg-gray-100 text-gray-700",
  edited: "bg-blue-100 text-blue-700",
  rejected: "bg-red-100 text-red-700",
  sent: "bg-green-100 text-green-700",
};

export function Badge({ className, status, children, ...props }: HTMLAttributes<HTMLSpanElement> & { status?: string }) {
  return (
    <span
      className={cn(
        "inline-block rounded-full px-2 py-0.5 text-xs font-medium",
        status ? colorForStatus[status] || "bg-gray-100 text-gray-700" : "bg-gray-100 text-gray-700",
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
