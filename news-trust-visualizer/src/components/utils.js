import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// Utility function for combining class names
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
