# Web React (Vite / Next.js) — ESLint Plugin Reference

> Last updated: 2026-03-20
> Sources: npm trends, GitHub, shadcn-ui, cal.com, trpc, formbricks, supabase/studio

## Baseline (most React web projects should have these)

| Plugin | Weekly DL | Stars | Maintainer | Notes |
|---|---|---|---|---|
| `typescript-eslint` | Very high | 15K+ | typescript-eslint org | 100% adoption. Use `recommendedTypeChecked` |
| `eslint-plugin-react` | Very high | React ecosystem | eslint-community | Standard React rules |
| `eslint-plugin-react-hooks` | Very high | React monorepo | Meta | **v6+ includes React Compiler rules** |
| `eslint-plugin-jsx-a11y` | High | — | jsx-eslint org | Web accessibility. Used by supabase, formbricks |
| `eslint-plugin-react-refresh` | High | — | ArnaudBarre | **Vite-only.** Ensures correct HMR. All Vite templates include it |
| `eslint-config-prettier` | Very high | — | Community | Universal |
| `simple-import-sort` | High | — | Community | Import ordering |
| `unused-imports` | High | — | Community | Auto-removes unused imports |

## MUST-HAVE additions

| Plugin | Weekly DL | Stars | Why |
|---|---|---|---|
| `prettier-plugin-tailwindcss` | 1.7M | 7K | **Tailwind Labs official.** Auto-sorts Tailwind classes. Tailwind v4 ready. trpc, shadcn pattern |
| `eslint-plugin-testing-library` | 4.5M | 1.3K+ | Testing Library org. Prevents wrong queries, waitFor misuse. Scope to test files |
| `@vitest/eslint-plugin` | 589K | — | **Official Vitest plugin** (renamed from eslint-plugin-vitest). Formbricks uses. Scope to test files |
| `@typescript-eslint/no-deprecated` | bundled | — | Replaces archived `eslint-plugin-deprecation` |

## NICE-TO-HAVE

| Plugin | Weekly DL | Stars | When |
|---|---|---|---|
| `eslint-plugin-sonarjs` | 1.7M | 1.2K | SonarSource. `cognitive-complexity` for complex components. Selective rules |
| `eslint-plugin-unicorn` | 5.7M | 4.9K | trpc uses. Requires ~5-10 rule overrides for React (no-null, prevent-abbreviations, filename-case) |
| `@tanstack/eslint-plugin-query` | 1.7M | 45.8K (mono) | Supabase Studio uses. Only if using TanStack Query |
| `eslint-plugin-jest` | 12.6M | 1.2K | If using Jest instead of Vitest |
| `eslint-config-next` | High | Vercel | **Next.js only.** Includes core-web-vitals rules. shadcn, formbricks, supabase use |
| `eslint-config-turbo` | Moderate | Vercel | **Turborepo only.** shadcn, formbricks, supabase all use |

## SKIP

| Plugin | Reason |
|---|---|
| ~~`eslint-plugin-react-compiler`~~ (standalone) | **Deprecated.** Merged into `eslint-plugin-react-hooks@latest` |
| ~~`eslint-plugin-tailwindcss`~~ | **Broken on Tailwind v4.** Use `prettier-plugin-tailwindcss` instead |
| ~~`eslint-plugin-react-hook-form`~~ | 3.4K/week, crash bugs, not official |
| ~~`eslint-plugin-security`~~ | Designed for Node.js server-side. High false positives in React client code |
| ~~`eslint-plugin-deprecation`~~ | **Archived.** Use `@typescript-eslint/no-deprecated` |

## Key Config Patterns from Real Projects

### trpc (ESLint 9, flat config)
- All three TS presets: `recommended` + `recommendedTypeChecked` + `stylisticTypeChecked`
- `eslint-plugin-unicorn` with `filename-case: camelCase`
- `react-hooks/react-compiler: error` — enforcing compiler compat
- `@typescript-eslint/naming-convention` for type parameters
- `prettier-plugin-tailwindcss` + `@ianvs/prettier-plugin-sort-imports`

### shadcn/ui (ESLint 8, legacy)
- `eslint-config-next` (core-web-vitals)
- `eslint-plugin-tailwindcss` with `classnames-order: error`
- Settings: `callees: ["cn", "cva"]` for clsx/cva support
- `eslint-config-turbo`

### supabase/studio (ESLint 9, flat config)
- `@tanstack/eslint-plugin-query` — TanStack Query rules
- `eslint-plugin-barrel-files` — forbids re-export-all barrel files
- Custom ESLint rule: `supabase/no-await-before-copy-to-clipboard`
- `jsx-a11y/role-has-required-aria-props: error`

### cal.com — MIGRATED TO BIOME
- Fully dropped ESLint + Prettier for Biome 2.x
- Import organization via Biome's built-in with custom groups
- Migration signal for future trend

### twenty — MIGRATED TO OXLINT
- Custom OXLint plugin package (`packages/twenty-oxlint-rules`)
- `consistent-type-imports` with inline-type-imports
- `func-style: declaration` with allowArrowFunctions

## Tailwind CSS Tooling Landscape

| Tool | Type | Tailwind v4 | Verdict |
|---|---|---|---|
| `prettier-plugin-tailwindcss` | Prettier (official) | Full support | **MUST-HAVE** |
| `eslint-plugin-tailwindcss` | ESLint (community) | Broken (WIP) | SKIP until fixed |
| `eslint-plugin-better-tailwindcss` | ESLint (community) | Supported | Optional (readability focus) |

## Emerging Alternative: eslint-react

`@eslint-react/eslint-plugin` (Rel1cx) — 4-7x faster than eslint-plugin-react, React 19 native,
TypeScript-first. Not yet displacing incumbent but gaining ground. Worth watching.
