import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function abbreviateStarStatus(name: string): string {
  return name.replace(/\(([^)]+)\)/, (_, status: string) => `(${status[0] ?? ''})`);
}
