import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

/**
 * Colour values belong in `src/app/globals.css` and nowhere else. A rule that
 * only lives in AGENTS.md gets violated within a few screens, so it is
 * enforced here instead.
 *
 * The escape hatch is a `// eslint-disable-next-line no-restricted-syntax`
 * with a comment saying why — there is exactly one legitimate case today
 * (the `theme-color` meta tag, which cannot read a CSS variable).
 */
const COLOUR_LITERAL = String.raw`#[0-9a-fA-F]{3,8}\b`;
const COLOUR_FUNCTION = String.raw`\b(?:rgba?|hsla?|oklch|lab|lch|color-mix)\(`;

const noColourLiterals = {
  files: ["src/**/*.{ts,tsx}"],
  rules: {
    "no-restricted-syntax": [
      "error",
      {
        selector: `Literal[value=/${COLOUR_LITERAL}/]`,
        message:
          "Colour literals belong in src/app/globals.css. Use a token-backed Tailwind utility or a CSS custom property.",
      },
      {
        selector: `Literal[value=/${COLOUR_FUNCTION}/]`,
        message:
          "Colour functions belong in src/app/globals.css. Use a token-backed Tailwind utility or a CSS custom property.",
      },
      {
        selector: `TemplateElement[value.raw=/${COLOUR_LITERAL}/]`,
        message:
          "Colour literals belong in src/app/globals.css. Use a token-backed Tailwind utility or a CSS custom property.",
      },
      {
        selector: `TemplateElement[value.raw=/${COLOUR_FUNCTION}/]`,
        message:
          "Colour functions belong in src/app/globals.css. Use a token-backed Tailwind utility or a CSS custom property.",
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
