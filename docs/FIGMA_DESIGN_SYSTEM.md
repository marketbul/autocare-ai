# AutoCare AI — Design System & Figma Architecture (FYP-1)

## 1. Overview & Design Philosophy
The AutoCare AI design system adheres strictly to the modern minimalist aesthetic benchmarks of **Linear, Raycast, Arc Browser, and Apple iOS 18**. 

Built for our Final Year Project (FYP-1) at the Department of Computer Science, University of the Punjab, the user interface spans:
1. **Web Dashboard**: Next.js / Vite + React 18 + Tailwind CSS + Framer Motion (Bento-Grid layout)
2. **Mobile App**: Cross-platform Flutter (`lib/`) & React Native Expo (`mobile/react_native/`) with frosted glass navigation, spring animations, and tactile cards.
3. **Figma Token Specification**: W3C DTCG / Token Studio compliant tokens located in [`mobile/figma_design_tokens.json`](../mobile/figma_design_tokens.json).

---

## 2. Color Palette & Token Definitions

| Token Name | Hex / RGBA | Role / Benchmark |
| :--- | :--- | :--- |
| `background.canvas` | `#09090b` | Deep slate/zinc canvas (Zinc-950) |
| `background.card` | `#18181b` | Elevated Bento card surface (Zinc-900) |
| `background.card-muted` | `#121215` | Recessed sub-card & telemetry panels |
| `background.card-hover` | `#27272a` | Card hover transition |
| `background.frosted` | `rgba(15, 15, 20, 0.75)` | Glassmorphic floating bars with `backdrop-filter: blur(20px)` |
| `border.hairline` | `rgba(255, 255, 255, 0.08)` | Ultra-subtle boundary definition (0.5px to 1px) |
| `accent.violet` | `#8b5cf6` | Electric Violet (Primary FYP brand accent) |
| `accent.emerald` | `#10b981` | Emerald green (Optimal ECU status, confidence >= 95%) |
| `accent.amber` | `#f59e0b` | Triage alert warning indicator |
| `accent.rose` | `#ef4444` | Critical diagnostic stop alert (10x Safety Penalty) |
| `text.primary` | `#f4f4f5` | High-contrast title (`letter-spacing: -0.025em`) |
| `text.secondary` | `#a1a1aa` | Muted subtitle / labels (Zinc-400) |

---

## 3. Web Bento Grid Architecture (`#/dashboard`)

The main dashboard screen implements an asynchronous 4-quadrant interactive Bento grid:

```
┌────────────────────────────────────────────────────────┐
│  Top Bar: Realtime Engine Telemetry & Active Vehicle   │
├───────────────────────────┬────────────────────────────┤
│  Card 1 (M6 Causal Graph) │  Card 2 (M2 Cost Triage)   │
│  - Multi-hop traversal    │  - 10x safety penalty      │
│  - Fault node propagation │  - Top 3 root causes       │
├───────────────────────────┼────────────────────────────┤
│  Card 3 (M8 Weibull RUL)  │  Card 4 (M9 Pakistan PKR)  │
│  - Hazard rate β/η curve  │  - Lahore / KHI OEM quotes │
│  - Remaining Useful Life  │  - Verified labour charges │
└───────────────────────────┴────────────────────────────┘
```

### Depth & Elevation:
- Specular Top Highlight: `box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.06)`
- Card Corner Radius: `rounded-2xl` (24px)
- Spacing: 16px grid gap with 24px responsive edge padding

---

## 4. Mobile Architecture (Flutter & React Native)

### 4.1 Flutter Architecture (`mobile/flutter_app`)
- **Theme**: `lib/theme/app_theme.dart` configuring dark Material 3 with Google Fonts (Plus Jakarta Sans) and Zinc-900 surface styling.
- **Frosted Tab Bar**: `lib/widgets/frosted_tab_bar.dart` featuring `BackdropFilter(ImageFilter.blur(sigmaX: 20, sigmaY: 20))`, spring tab transitions, and pill indicators.
- **Screens**:
  1. `HomeScreen`: ECU health overview, live diagnostic codes, telemetry meters, and quick actions.
  2. `DiagnosticScreen`: Multi-turn conversational copilot supporting English and Urdu (`مکینیکل خرابی`) with cited workshop manual sources.
  3. `CausalGraphScreen`: Node-edge Bayesian causal network visualizer.
  4. `PricingScreen`: Pakistan localized auto-part vendor listings with genuine OEM pricing in PKR.

### 4.2 React Native Architecture (`mobile/react_native`)
- **Framework**: Expo + NativeWind + React Native Reanimated.
- **File**: `mobile/react_native/App.tsx`.
- **Interactions**:
  - Pull-to-refresh haptic simulation.
  - Spring-animated card press states (`scale: 0.98` on touch).
  - Floating frosted tab bar with glass blur overlay.

---

## 5. How to Import Tokens into Figma
1. Install the **Tokens Studio for Figma** plugin.
2. Open your Figma project.
3. Open **Tokens Studio** -> Click **Settings** -> **Load from Local File**.
4. Select [`mobile/figma_design_tokens.json`](../mobile/figma_design_tokens.json).
5. All color styles, font families, radius tokens, and elevation shadows will auto-generate into your local Figma styles library.
