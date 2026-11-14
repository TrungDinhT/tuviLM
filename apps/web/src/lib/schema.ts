import { Result, Schema, SchemaIssue } from "effect";

/**
 * Shared Effect Schema helpers.
 *
 * Every decode in the app reports its failures in one flat shape: a path and a
 * message per issue. Forms show the first message; the API client carries the
 * whole list on its `parse` error.
 */

const formatIssues = SchemaIssue.makeFormatterStandardSchemaV1();

/** One failure: a message and the path to the value it is about. */
export type Issue = ReturnType<typeof formatIssues>["issues"][number];

/** The flat issue list of a failed decode. */
export const issuesOf = (error: Schema.SchemaError): ReadonlyArray<Issue> =>
  formatIssues(error.issue).issues;

/**
 * Decode `input`, collecting every issue rather than the first one only.
 * Use it where the caller needs the value or the issues, not an exception.
 */
export const validate = <S extends Schema.ConstraintDecoder<unknown>>(
  schema: S,
  input: unknown,
): Result.Result<S["Type"], ReadonlyArray<Issue>> =>
  Result.mapError(Schema.decodeUnknownResult(schema)(input, { errors: "all" }), issuesOf);

/** The first message of a failed decode, or `fallback` when it has none. */
export const firstMessage = (issues: ReadonlyArray<Issue>, fallback: string): string =>
  issues[0]?.message ?? fallback;

/** ISO 8601 date-time with a `Z` or `±hh:mm` offset, as the backend sends it. */
export const IsoDateTime = Schema.String.check(
  Schema.isPattern(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})$/, {
    message: "Expected an ISO 8601 date-time with an offset",
  }),
);

/** An integer in `[minimum, maximum]`. */
export const IntBetween = (minimum: number, maximum: number) =>
  Schema.Number.check(Schema.isInt(), Schema.isBetween({ minimum, maximum }));

/** A string of at least one character. */
export const NonEmpty = Schema.String.check(Schema.isMinLength(1));

/** The pattern zod used for `.email()`, kept so sign-up accepts the same addresses. */
export const EMAIL_PATTERN =
  /^(?!\.)(?!.*\.\.)([A-Za-z0-9_'+\-.]*)[A-Za-z0-9_+-]@([A-Za-z0-9][A-Za-z0-9-]*\.)+[A-Za-z]{2,}$/;
