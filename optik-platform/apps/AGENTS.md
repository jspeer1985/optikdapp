# Repository Guidelines

## Project Structure & Module Organization
- `app/` is the Next.js 14 App Router: route segments live in their own folders (`page.tsx`, `layout.tsx`, helpers), shared UI lives in `components/`, shared logic in `hooks/`, `lib/`, `models/`, `context/`, and `providers.tsx`.
- Static assets live in `public/`, operational helpers live in `scripts/`, and automation metadata is contained under `agents/`, `audit/`, `managed_context/`, and `mcp_servers.json` so runtime bundles stay focused on `app/` and `optik-coin/`, `payments/`, or `dashboard/` features that map directly to their routes.

## Build, Test, and Development Commands
- `npm run dev`: Next dev server on port 3003 with Fast Refresh.
- `npm run lint`: runs `next lint` (Next/React/TypeScript ESLint rules); fix issues before commits.
- `npm run build`: compiles and type-checks the production bundle.
- `npm run start` / `npm run start:prod`: serve the built app (`start:prod` enforces `NODE_ENV=production` and respects `PORT`).
- `npm run start:pm2`: launches PM2 via `ecosystem.config.js` for PM2-managed deployments.
- `./scripts/start-prod.sh`: helper that builds and runs `next start` (set `PORT` as needed).

## Coding Style & Naming Conventions
This TypeScript + React + Tailwind project uses strict compiler settings; prefer PascalCase for components, camelCase for hooks/utilities, and keep hook names prefixed with `use`. Use the `@/*` alias defined in `tsconfig.json` instead of long relative paths. Run `npm run lint` before pushing so ESLint, Tailwind-aware rules, and Next conventions stay satisfied.

## Testing Guidelines
There is no automated test suite yet; rely on `npm run lint` and manual QA notes stored in `test_suite_analysis/metadata.json`. If you add tests, place them next to the module under `<module>.test.ts(x)` so future runners can discover them.

## Commit & Pull Request Guidelines
Because the repo currently lacks history, follow a conventional-commit format (`feat:`, `fix:`, `chore:`) with a short present-tense summary, linked issue or ticket, and a testing note. PR descriptions should outline what changed, how to run the app locally, and include relevant screenshots for UI work or new toggles.

## Security & Configuration Tips
Respect the CSP and other security headers configured in `next.config.js` by avoiding inline scripts and minimizing `unsafe-*` directives. Copy `.env.example` to `.env.local` for secrets (`NEXT_PUBLIC_*`, RPC endpoints, Stripe keys) and keep `.env.local` out of Git. For production, prefer `npm run start:prod` or `./scripts/start-prod.sh` with `NODE_ENV=production`; use `npm run start:pm2` only when the deployment target runs PM2.
