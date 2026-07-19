---
name: swift-macos-menubar
description: "Use when working on Swift, SwiftUI, AppKit, MenuBarExtra, packaging, or macOS menubar app behavior in this repository or similar native macOS utilities."
---

# Swift macOS Menubar

## Overview

Use this skill for native Swift/macOS work where SwiftUI and AppKit meet. It is tuned for small menu bar apps that need reliable redraws, careful state handling, and predictable build and packaging workflows.

## When to Use

- Changing `MenuBarExtra`, popover, or status item behavior
- Adding SwiftUI views that depend on `@Published` model state
- Bridging between SwiftUI and AppKit
- Touching account switching, auth snapshots, or actor-isolated engine logic
- Updating app bundle packaging, icons, or release scripts

## Core Rules

- Prefer simple SwiftUI data flow first, then add AppKit escape hatches only where SwiftUI is unreliable.
- Keep concurrency boundaries explicit. Actor-owned state stays inside the actor; UI models translate it for the main thread.
- Treat menu bar UI as fragile: redraw and caching issues are common, so verify behavior in the built app, not only `swift run`.
- Keep `MenuBarExtra` labels visually minimal. Use template-style icons or very compact text.
- For repo changes, run `swift build` at minimum. Run `swift test` when logic or model code changes.

## Repo Patterns

- App entry and menubar wiring live in `Sources/CodexSwitcherApp.swift`.
- User-facing panel layout lives in `Sources/ContentView.swift`.
- Actor-based switching and snapshot logic live in `Sources/SwitcherEngine.swift`.
- Bundle creation and deployment live in `scripts/build_app.sh` and `scripts/deploy_app.sh`.

## Tooling

- Format with `scripts/swift-format.sh`.
- Lint with `scripts/swift-lint.sh`.
- Build with `swift build -c release --product CodexSwitcher`.
- Deploy app bundle with `scripts/deploy_app.sh`.

## Common Mistakes

- Assuming a menu bar label updates because model state changed. Verify the rendered label path directly.
- Mixing UI concerns into `SwitcherEngine`. Keep business logic in the actor and presentation logic in the app/view layer.
- Using full-color app artwork in the menubar. Native status items want small, simple template glyphs.
- Relying on debug-only behavior for launch/login/session issues. Confirm with the bundled `.app`.
