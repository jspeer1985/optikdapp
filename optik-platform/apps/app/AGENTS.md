# Repository Guidelines

## Project Structure & Module Organization
- This directory is a Next.js App Router app. Top-level route folders (`auth/`, `checkout/`, `dashboard/`, `dapps/`, `store-preview/`, etc.) map directly to URL paths and usually contain `page.tsx` plus route-local helpers.
- Shared code lives in `components/` (UI), `context/` (React providers), `hooks/`, `lib/` (API/Solana helpers), `models/`, `utils/`, and root `providers.tsx`.
- Global shell and styling live in `layout.tsx`, `page.tsx`, and `globals.css`.

## Build, Test, and Development Commands
- `npm run dev`: start the Next.js dev server on `http://localhost:3003`.
- `npm run build`: create the production build and run framework checks.
- `npm run start`: serve the built app.
- `npm run start:prod`: run with `NODE_ENV=production` and optional `PORT`.
- `npm run lint`: run Next/ESLint checks (first run may ask to initialize ESLint).
- `npx tsc --noEmit --incremental false`: strict TypeScript validation without output files.

## Coding Style & Naming Conventions
- Use TypeScript and React function components.
- Follow 2-space indentation and group imports from external packages first, internal modules second.
- Use PascalCase for components/files (for example `ConnectWallet.tsx`), camelCase for hooks/utilities (for example `useWalletBalance.ts`), and Next.js route file names (`page.tsx`, `layout.tsx`).
- Prefer the `@/*` path alias from `tsconfig.json` over deep relative imports.

## Testing Guidelines
- There is no formal automated test suite in this app yet.
- Minimum validation before PR: `npm run build`, `npm run lint`, and manual checks for every changed route (for example `/auth`, `/dashboard/*`, `/dapps/[id]`).
- If you add tests, colocate them near implementation as `<module>.test.ts(x)`.

## Commit & Pull Request Guidelines
- Git history is minimal (`first commit`), so no strong legacy convention exists yet.
- Use Conventional Commit prefixes (`feat:`, `fix:`, `chore:`) with present-tense, scoped summaries.
- PRs should include: change summary, linked issue/ticket, validation steps/results, and screenshots for UI changes.

## Security & Configuration Tips
- Keep secrets in `.env.local` only; do not commit private keys or tokens.
- Use `NEXT_PUBLIC_RPC_ENDPOINT` and `NEXT_PUBLIC_SOLANA_NETWORK` consistently for wallet/network behavior.
- Respect security headers in `../next.config.js` when adding external scripts or network origins.
