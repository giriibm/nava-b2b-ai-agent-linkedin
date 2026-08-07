import { LabelHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export const Label = ({ className, ...props }: LabelHTMLAttributes<HTMLLabelElement>) => (
  <label className={cn("text-sm font-medium text-gray-700 mb-1 block", className)} {...props} />
);
