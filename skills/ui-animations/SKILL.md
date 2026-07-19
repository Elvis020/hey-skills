---
name: ui-animations
description: "Use when implementing animations in any UI (SwiftUI, CSS, React). Provides easing curves, timing values, spring parameters, and principles from Emil Kowalski's animation guidelines — adapted for both SwiftUI/macOS and web."
---

# UI Animation Skill

## Core Principles (Emil Kowalski)

1. **Natural Motion** — Use spring physics, not linear transitions. Animate like living elements.
2. **Speed < 300ms** — Start fast (ease-out). Users perceive fast starts as responsive.
3. **Animate purposefully** — State changes, modals, enter/exit. NOT repetitive keyboard actions.
4. **Only transform + opacity** — Never animate layout (width, height, padding). GPU compositing only.
5. **Always interruptible** — No animation should lock the UI. Mid-sequence cancellation must be smooth.
6. **Origin awareness** — Dropdowns animate from their trigger. Panels expand from their edge. Context matters.

---

## Production Easing Curves

### Spring-like (Energetic) — button press, hover, micro-interactions
```
cubic-bezier(0.34, 1.56, 0.64, 1)
```
Slight overshoot, bouncy feel. 200ms hover, 80–100ms press.

### Smooth Ease-Out (Gentle) — panel expand, modal, large elements
```
cubic-bezier(0.16, 1, 0.3, 1)
```
No overshoot, professional. 250–300ms.

### Fast Response (Snappy) — toggles, icons, tooltips
```
cubic-bezier(0.4, 0, 0.2, 1)
```
Immediate feel, no bounce. 100–150ms.

---

## Timing Reference

| Element              | Duration   | Curve        |
|----------------------|-----------|--------------|
| Button hover         | 200ms     | Spring-like  |
| Button press         | 80–100ms  | Fast response |
| Modal / panel enter  | 250–300ms | Smooth ease-out |
| Slide transition     | 300ms     | Spring-like  |
| Micro-interaction    | 150–200ms | Spring-like  |
| Tooltip appear       | 100ms     | Fast response |
| Success feedback     | 600ms     | Spring-like  |
| Dropdown menu        | 200ms     | Smooth ease-out |

---

## SwiftUI Equivalents

### Spring animation (for button press, circle pop, hover)
```swift
// Energetic spring — equivalent to cubic-bezier(0.34, 1.56, 0.64, 1)
.animation(.spring(response: 0.3, dampingFraction: 0.6, blendDuration: 0), value: isPressed)

// Snappy spring — no bounce, quick
.animation(.spring(response: 0.2, dampingFraction: 0.8), value: isExpanded)

// Smooth ease-out — panel/modal entrance
.animation(.interpolatingSpring(stiffness: 380, damping: 30), value: isShown)
// or:
.animation(.easeOut(duration: 0.25), value: isShown)
```

### NSAnimationContext (for NSPanel frame changes)
```swift
// Panel expand — smooth ease-out feel
NSAnimationContext.runAnimationGroup { ctx in
    ctx.duration = 0.28
    ctx.timingFunction = CAMediaTimingFunction(controlPoints: 0.16, 1, 0.3, 1)
    panel.animator().setFrame(targetFrame, display: true)
}

// Circle pop — spring-like energetic
NSAnimationContext.runAnimationGroup { ctx in
    ctx.duration = 0.32
    ctx.timingFunction = CAMediaTimingFunction(controlPoints: 0.34, 1.56, 0.64, 1)
    panel.animator().setFrame(targetFrame, display: true)
}
```

### Button press scale pattern
```swift
struct AnimatedButton: View {
    @State private var isPressed = false

    var body: some View {
        Circle()
            .scaleEffect(isPressed ? 0.88 : 1.0)
            .animation(
                isPressed
                    ? .easeIn(duration: 0.08)          // fast press down
                    : .spring(response: 0.3, dampingFraction: 0.6), // bouncy release
                value: isPressed
            )
            .simultaneousGesture(DragGesture(minimumDistance: 0)
                .onChanged { _ in isPressed = true }
                .onEnded { _ in isPressed = false }
            )
    }
}
```

### Appear animation (floating circle pop-in)
```swift
// On appear: scale from 0.5 + opacity 0 → 1
.onAppear {
    withAnimation(.spring(response: 0.35, dampingFraction: 0.55)) {
        scale = 1.0
        opacity = 1.0
    }
}
// Initial state: scale = 0.5, opacity = 0
```

### Hover glow (not pulsing — subtle scale + shadow)
```swift
.scaleEffect(isHovered ? 1.06 : 1.0)
.shadow(color: accentColor.opacity(isHovered ? 0.4 : 0.2), radius: isHovered ? 12 : 6)
.animation(.spring(response: 0.25, dampingFraction: 0.65), value: isHovered)
```

---

## Key Rules for This Codebase

- **Floating circle**: pop-in with spring (dampingFraction 0.5–0.6), press with scale 0.88, hover with subtle scale + glow
- **Panel expand/collapse**: `NSAnimationContext` with smooth ease-out `(0.16, 1, 0.3, 1)`, ~280ms
- **No linear animations** — always use spring or custom bezier
- **No layout property animation** — never animate `frame` without `NSAnimationContext`; never animate SwiftUI `width`/`height` directly — use `scaleEffect` + `opacity` instead
- **Reduced motion**: Check `NSWorkspace.shared.accessibilityDisplayShouldReduceMotion` and skip animations if true

---

## Checklist Before Shipping

- [ ] Duration < 300ms (unless celebration)
- [ ] Only transform/opacity/scale animated (no layout)
- [ ] Custom spring or bezier — no `linear`
- [ ] Interruptible (no `.allowsHitTesting(false)` during animation)
- [ ] Reduced motion fallback
- [ ] Origin is contextually correct (expands from where user clicked)
- [ ] Consistent with other similar animations in app
