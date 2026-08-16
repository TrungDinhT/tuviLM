/**
 * Join class names, dropping anything falsy.
 *
 * Deliberately not `tailwind-merge`: the design's utilities rarely conflict,
 * and pulling in a merge pass would invite components to be written as
 * override chains. If conflicts start appearing, that is a signal the variant
 * is missing, not that a merger is missing.
 */
export function cn(...values: Array<string | false | null | undefined>): string {
  return values.filter(Boolean).join(" ");
}
