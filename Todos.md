# TODOs

## Project Maintenance
- [ ] Using npm as the preferred package manager. Found multiple lockfiles. Delete the lockfiles that don't match npm (`package-lock.json`).

  **Context for Discussion:**
  - **Lockfile Differences:**
    - npm uses `package-lock.json`
    - pnpm uses `pnpm-lock.yaml`
    - Only one lockfile should exist in your project root to avoid conflicts.
  - **Dependency Management:**
    - npm: Flat `node_modules`, can duplicate packages, slower for large projects, widely supported.
    - pnpm: Uses a global content-addressable store, deduplicates dependencies, faster installs, strict dependency enforcement, smaller disk usage.
  - **Project Maintenance Implications:**
    - Consistency: Only one lockfile ensures consistent installs. Mixing lockfiles can cause bugs.
    - Speed & Efficiency: pnpm is faster and more space-efficient.
    - Compatibility: npm is default and most widely supported; some tools expect `package-lock.json`.
    - Strictness: pnpm enforces stricter dependency rules.
  - **How to Switch:**
    - To npm: Delete `pnpm-lock.yaml`, keep `package-lock.json`, run `npm install`.
    - To pnpm: Delete `package-lock.json`, keep `pnpm-lock.yaml`, run `pnpm install`.
  - **Summary Table:**

    | Feature         | npm                  | pnpm                        |
    |-----------------|----------------------|-----------------------------|
    | Lockfile        | package-lock.json    | pnpm-lock.yaml              |
    | Speed           | Moderate             | Fast                        |
    | Disk Usage      | Higher               | Lower (deduped, symlinked)  |
    | Strictness      | Moderate             | High                        |
    | Monorepo Support| Basic                | Excellent                   |
    | Default         | Yes                  | No (must install pnpm)      |

  - **Recommendation:**
    - Use npm for maximum compatibility and simplicity.
    - Use pnpm for speed, disk efficiency, and stricter dependency management (especially for large projects or monorepos).

## Codebase TODOs
- [ ] api/agents/agent.py: Add back the annotation in `business_context = get_info(connection_id)  #TODO add back the annotation`
- [ ] api/agents/agent.py: Make user_table and event_table dynamic (`#TODO: make these dynamic`) 