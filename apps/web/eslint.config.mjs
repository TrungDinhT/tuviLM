import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

/**
 * Colour values belong in CSS: `src/app/globals.css` tokens, a component's
 * co-located `*.module.css`, or a Tailwind arbitrary value in a `className`
 * (a className string *is* CSS, so `bg-[...rgba(...)...]` is fine).
 *
 * The one place they must never appear is an inline `style={{...}}` object —
 * inline styles bypass the token/utility system entirely. A rule that only
 * lives in AGENTS.md gets violated within a few screens, so it is enforced
 * here instead.
 */
const COLOUR_LITERAL = String.raw`#[0-9a-fA-F]{3,8}\b`;
const COLOUR_FUNCTION = String.raw`\b(?:rgba?|hsla?|oklch|lab|lch|color-mix)\(`;

const INLINE_STYLE = "JSXAttribute[name.name='style']";

const noColourLiterals = {
  files: ["src/**/*.{ts,tsx}"],
  rules: {
    "no-restricted-syntax": [
      "error",
      {
        selector: `${INLINE_STYLE} Literal[value=/${COLOUR_LITERAL}/]`,
        message:
          "Colour literals don't belong in an inline style prop. Use a token-backed utility, an arbitrary value in className, or a co-located *.module.css.",
      },
      {
        selector: `${INLINE_STYLE} Literal[value=/${COLOUR_FUNCTION}/]`,
        message:
          "Colour functions don't belong in an inline style prop. Use a token-backed utility, an arbitrary value in className, or a co-located *.module.css.",
      },
      {
        selector: `${INLINE_STYLE} TemplateElement[value.raw=/${COLOUR_LITERAL}/]`,
        message:
          "Colour literals don't belong in an inline style prop. Use a token-backed utility, an arbitrary value in className, or a co-located *.module.css.",
      },
      {
        selector: `${INLINE_STYLE} TemplateElement[value.raw=/${COLOUR_FUNCTION}/]`,
        message:
          "Colour functions don't belong in an inline style prop. Use a token-backed utility, an arbitrary value in className, or a co-located *.module.css.",
      },
    ],
  },
};

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  noColourLiterals,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    // Not ours: the design prototype is a reference artefact, not source.
    "docs/design/**",
  ]),
]);

export default eslintConfig;
