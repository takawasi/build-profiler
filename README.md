# build-profiler

Profile Next.js/Vite build times per module.

Find your slow modules.

## Quick Start

```bash
# 1. Install
pip install build-profiler

# 2. Build your project first
npx next build  # or: npx vite build

# 3. Profile
build-profiler --next ./app
```

## Features

- **Per-module breakdown**: See which modules are largest
- **Auto-detect**: Detects Next.js or Vite automatically
- **Suggestions**: Get optimization hints
- **CI-ready**: `--max-size` for quality gates

## Output Example

```
Build Profile
Total size: 2.3MB

         Slowest Modules
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ # ┃ Module                           ┃    Size ┃ % of Total          ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 1 │ node_modules/moment/moment.js    │ 287.0KB │ ██████████░░░ 24.5% │
│ 2 │ components/Chart/index.tsx       │ 156.0KB │ █████░░░░░░░░ 13.3% │
│ 3 │ node_modules/lodash/lodash.js    │  72.0KB │ ██░░░░░░░░░░░  6.1% │
│ 4 │ pages/dashboard/index.tsx        │  45.0KB │ █░░░░░░░░░░░░  3.8% │
└───┴──────────────────────────────────┴─────────┴─────────────────────┘

╭──────────────── Suggestions ─────────────────╮
│ ⚠️ moment.js: Consider date-fns or dayjs    │
│ ⚠️ lodash: Use lodash-es or import specific │
╰──────────────────────────────────────────────╯
```

## Usage

```bash
# Next.js project
build-profiler --next ./app

# Vite project
build-profiler --vite ./app

# Auto-detect (looks for config files)
build-profiler ./app

# Top N modules
build-profiler --next ./app --top 10

# JSON output
build-profiler --next ./app --format json

# CI: fail if module exceeds size
build-profiler --next ./app --max-size 500  # 500KB limit
```

## Requirements

- Project must be built first (`next build` or `vite build`)
- Analyzes `.next/` or `dist/` output directories

## More Tools

See all dev tools: https://takawasi-social.com/en/

## License

MIT
