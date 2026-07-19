---
name: skeleton-loader-fidelity
description: "Audit, design, and fix skeleton loaders so loading states preserve the real content footprint, avoid clipping, reduce layout shift, and show enough page structure. Use when skeleton screens, shimmer placeholders, loading cards, table placeholders, route-level loaders, or suspense fallbacks are cut off, too generic, layout-shifty, inaccessible, or visually misleading across desktop/mobile."
---

# Skeleton Loader Fidelity

Use this skill to make skeleton loaders honest first-viewport previews of the UI that will appear after data loads. Favor preserving the real layout rhythm over decorative placeholder blocks, but do not make users scroll through fake content.

## Workflow

1. Find every loading state on the route or component.
   - Search for `Skeleton`, `skeleton`, `loading`, `aria-busy`, `Suspense`, `fallback`, `animate-pulse`, and route-level conditional rendering.
   - Identify whether the loader is page-level, panel-level, table/list-level, or inline.

2. Compare loader structure to the loaded state.
   - Match the same major regions: masthead, filters, cards, table header, rows, side panels, forms, and primary actions.
   - Use fewer repeated rows if needed, but preserve the first viewport's information architecture.
   - Do not use a single generic block where the loaded UI is a table, form, or multi-section page.

3. Bound page-level loaders to the available viewport.
   - Treat `max-height`, `height`, `overflow: hidden`, `min-height: 0`, and scroll containers as suspects.
   - Page-level skeletons should not create document or app-shell scroll.
   - Show a deliberate first-viewport preview by reducing fake rows/cards, using stable `max-height`, and hiding overflow at the loading boundary.
   - Panels may keep `overflow: hidden` for rounded corners or internal table borders.
   - If content extends beyond the loading viewport, make the ending intentional: reduce repeats first, then use a subtle fade/edge, not accidental chopped rows.

4. Preserve footprint like a snapshot overlay.
   - Borrow the Boneyard principle: the skeleton should occupy the same container size and spatial rhythm as the real content.
   - For hand-built skeletons, encode stable sizes with `min-height`, grid tracks, aspect ratios, and small repeated row counts.
   - For measured skeletons, render the real fixture invisibly and overlay bones only if the framework supports it safely.

5. Make mobile explicit.
   - Verify phone heights around 667, 740, 812, and 852 px.
   - Avoid viewport math like `calc(100svh - 27rem)` unless it has a clear lower bound.
   - Keep route skeletons under fixed headers by using the same page wrapper as the loaded state.

6. Respect accessibility and motion.
   - Put `aria-busy="true"` and a concise `aria-label` on meaningful loading regions.
   - Keep skeletons non-interactive.
   - Disable shimmer/pulse under `prefers-reduced-motion: reduce`.
   - Animate opacity only; do not animate layout size while data arrives.

## Red Flags

- A skeleton renders every fake section/row and makes the loading state scroll.
- A global skeleton class clips content without budgeting rows/cards for the viewport.
- Desktop skeleton rows rely on fixed columns that overflow narrow screens.
- The loading state hides the masthead but the loaded state starts with one.
- The skeleton's first viewport has less structure than the loaded first viewport.
- A page-level loader is centered as a small spinner/card for a dense table or form.
- Skeleton CSS uses `transition: all` or repeats motion that ignores reduced-motion preferences.

## Verification

Use browser inspection when available:

- Capture or measure the skeleton route and the loaded route at one desktop and at least one phone viewport.
- Confirm page-level skeletons do not create document or app-shell scroll.
- Confirm no skeleton row/card is accidentally cut off by an ancestor; if the preview is bounded, the boundary should look intentional.
- Confirm final content does not jump more than the unavoidable difference between placeholder row counts and real data.

For CSS-only fixes, run the app build or typecheck and inspect the changed viewport manually or with Playwright.
