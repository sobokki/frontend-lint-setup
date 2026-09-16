# Cross-Cutting Tools — Universal Reference

> Last updated: 2026-03-20
> Sources: npm trends, GitHub, typescript-eslint docs, 17 OSS project survey

## Universal ESLint Plugins (all frameworks)

### MUST-HAVE

| Plugin/Rule | Weekly DL | Why |
|---|---|---|
| `@typescript-eslint/no-deprecated` | bundled | Catches calls to @deprecated APIs. Replaces archived `eslint-plugin-deprecation`. Requires type-checked config |
| `@typescript-eslint/consistent-type-imports` | bundled | Enforces `import type {}`. 8/10 major projects use. Auto-fixable |

### NICE-TO-HAVE

| Plugin | Weekly DL | Stars | Why |
|---|---|---|---|
| `eslint-plugin-sonarjs` | 1.7M | 1.2K | `cognitive-complexity` (default threshold: 15) is the primary draw. SonarSource enterprise-backed. v2+ has 200+ rules — **use selective, not recommended** |
| `eslint-plugin-unicorn` | 5.7M | 4.9K | Sindre Sorhus. 140+ rules but **aggressive recommended preset**. Requires per-framework overrides. Key conflicts: no-null (React), prevent-abbreviations (NestJS req/res/ctx), no-static-only-class (NestJS services) |
| `eslint-plugin-regexp` | 1.1M | 757 | ota-meshi. ReDoS detection is the killer feature. Low config overhead — `flat/recommended` is safe to drop in |
| `eslint-plugin-no-secrets` | 150K | — | Entropy-based secret detection. Complement with gitleaks for robustness. Tune `tolerance: 4.2` |
| `eslint-plugin-boundaries` | 446K | 1.4K | Architectural import boundaries. **Check Turborepo built-in `turbo boundaries` first** (Turborepo 2.4.2+) |

## Non-ESLint Complementary Tools

### MUST-HAVE

| Tool | Stars | Why |
|---|---|---|
| **Knip** | 10.5K | Finds unused files, exports, dependencies. Replaces depcheck + ts-prune + unimported (all archived). Turborepo uses it internally. Monorepo-aware |

### NICE-TO-HAVE (Watch)

| Tool | Status | Why |
|---|---|---|
| **OXLint** | 1.0 stable (Jun 2025) | 50-100x faster than ESLint. 699+ built-in rules. Use as CI pre-pass alongside ESLint via `eslint-plugin-oxlint`. Type-aware alpha. JS plugin alpha (Mar 2026) |
| **Biome** | 2.4+ | Unified linter+formatter. 10-56x faster. cal.com and twenty migrated. **But no RN support, no custom plugins yet.** Viable as formatter-only replacement for Prettier |

### SKIP

| Tool | Reason |
|---|---|
| ~~depcheck~~ | Archived. Use Knip |
| ~~ts-prune~~ | Archived. Use Knip |
| ~~publint~~ | Only for published npm packages |

## TypeScript ESLint Config Tiers

| Config | Type info | Opinionated | Recommendation |
|---|---|---|---|
| `recommended` | No | Low | Minimum baseline only |
| `strict` | No | High | Good for strict teams |
| `recommendedTypeChecked` | Yes | Low-medium | **Recommended for most apps** |
| `strictTypeChecked` | Yes | High | Best for server/backend code |
| `stylisticTypeChecked` | Yes | Style | Add on top (trpc uses all three) |

**Strategy**: `recommendedTypeChecked` as shared base. `strictTypeChecked` for server only.
Avoid `strictTypeChecked` on mobile initially (legacy patterns trigger violations).

## Performance Optimization

| Strategy | Impact | Notes |
|---|---|---|
| ESLint caching | High | `eslint . --cache --cache-location node_modules/.cache/.eslintcache` |
| Turborepo caching | High | `pnpm turbo lint` — skips unchanged packages |
| lint-staged + Husky | High | Local dev: lint only staged files |
| `TIMING=1 npx eslint .` | Debug | Identifies slow rules |
| `import/no-cycle` CI-only | High | This rule alone can 5x lint time |
| `parserOptions.projectService` | Moderate | Default in typescript-eslint v8. Faster than project globs |
| Type-checked rules | 30x slower | As slow as `tsc --noEmit`. Worth it but plan for CI time |

## Real-World Adoption Frequency (17 projects surveyed)

```
100%   typescript-eslint, Prettier
67%+   react, react-hooks, eslint-config-prettier, import/import-x
50%    jest, react-native (in RN projects), react-native-a11y
33%    simple-import-sort, eslint-config-turbo, jsdoc
17%    unicorn (trpc), tailwindcss (shadcn), @tanstack/query (supabase)

Migration signals:
  cal.com → Biome 2.x (full migration)
  twenty → OXLint (full migration)
  ultimate-nest → OXLint (full migration)
```

## Deprecated / Archived Plugins (do NOT recommend)

| Plugin | Status | Replacement |
|---|---|---|
| `eslint-plugin-deprecation` | Archived | `@typescript-eslint/no-deprecated` |
| `eslint-plugin-react-compiler` | Deprecated (Oct 2025) | `eslint-plugin-react-hooks@latest` (recommended-latest preset) |
| `eslint-plugin-rxjs` (cartant) | Dead, no ESLint 9 | `eslint-plugin-rxjs-x` |
| `eslint-plugin-security-node` | Stale, no ESLint 9 | `eslint-plugin-security` (4 useful rules) |
| `eslint-plugin-node` | Abandoned | `eslint-plugin-n` (eslint-community fork) |
| `eslint-plugin-vitest` (old) | Stale | `@vitest/eslint-plugin` (official rename) |
| `depcheck` | Archived | Knip |
| `ts-prune` | Archived | Knip |
| `unimported` | Archived | Knip |
