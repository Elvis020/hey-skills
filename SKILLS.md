# Skills

A working shelf of playbooks for agents that need to build, debug, design, and ship.

> **70 skills. 9 shelves. One command to take the lot.**

```sh
npx github:Elvis020/hey-skills add --all --to ./skills
```

## Pick a shelf

<table width="100%">
<thead>
<tr><th align="left">Shelf</th><th align="left">What lives here</th><th align="right">Skills</th></tr>
</thead>
<tbody>
<tr><td>🧱 <a href="#backend-and-data"><strong>Backend &amp; Data</strong></a></td><td>Services, persistence, and the parts that have to stay correct.</td><td align="right">4</td></tr>
<tr><td>☁️ <a href="#cloud-and-infrastructure"><strong>Cloud &amp; Infrastructure</strong></a></td><td>Platforms, deployments, and life beyond localhost.</td><td align="right">10</td></tr>
<tr><td>✍️ <a href="#communication-and-productivity"><strong>Communication &amp; Productivity</strong></a></td><td>Say more with less, then hand the work over cleanly.</td><td align="right">4</td></tr>
<tr><td>🧭 <a href="#debugging-and-quality"><strong>Debugging &amp; Quality</strong></a></td><td>Follow the evidence, find the fault, and verify the fix.</td><td align="right">4</td></tr>
<tr><td>🛠️ <a href="#engineering-workflow"><strong>Engineering Workflow</strong></a></td><td>Understand the codebase and keep useful work moving.</td><td align="right">11</td></tr>
<tr><td>✦ <a href="#frontend-and-design"><strong>Frontend &amp; Design</strong></a></td><td>Interfaces with taste, motion, accessibility, and sharp edges.</td><td align="right">24</td></tr>
<tr><td>📱 <a href="#native-and-mobile"><strong>Native &amp; Mobile</strong></a></td><td>Small screens, native conventions, and thumb-friendly decisions.</td><td align="right">5</td></tr>
<tr><td>🧠 <a href="#planning-and-learning"><strong>Planning &amp; Learning</strong></a></td><td>Think clearly before the expensive part begins.</td><td align="right">5</td></tr>
<tr><td>🛡️ <a href="#security"><strong>Security</strong></a></td><td>Catch secrets, harden boundaries, and reduce avoidable risk.</td><td align="right">3</td></tr>
</tbody>
</table>

Pick a shelf, then open a skill to reveal its details and copy the install command.

<a id="backend-and-data"></a>

## 🧱 Backend & Data

*Services, persistence, and the parts that have to stay correct.*

<p><a href="catalog/java-coding-standards.md"><strong>Java Coding Standards</strong></a> — Java coding standards for Spring Boot services: naming, immutability, Optional usage, streams, exceptions…</p>
<p><a href="catalog/logging-best-practices.md"><strong>Logging Best Practices</strong></a> — Design and review application logging using wide events/canonical log lines, high-cardinality structured…</p>
<p><a href="catalog/pattern-fit-architecture.md"><strong>Pattern Fit Architecture</strong></a> — Use when designing, implementing, or reviewing code that touches persistence boundaries, caching or…</p>
<p><a href="catalog/supabase-postgres-best-practices.md"><strong>Supabase Postgres Best Practices</strong></a> — Postgres performance optimization and best practices from Supabase.</p>

<a id="cloud-and-infrastructure"></a>

## ☁️ Cloud & Infrastructure

*Platforms, deployments, and life beyond localhost.*

<p><a href="catalog/agents-sdk.md"><strong>Agents SDK</strong></a> — Build AI agents on Cloudflare Workers using the Agents SDK.</p>
<p><a href="catalog/cloudflare.md"><strong>Cloudflare</strong></a> — Comprehensive Cloudflare platform skill covering Workers, Pages, storage (KV, D1, R2), AI (Workers AI…</p>
<p><a href="catalog/cloudflare-email-service.md"><strong>Cloudflare Email Service</strong></a> — Send and receive transactional emails with Cloudflare Email Service (Email Sending + Email Routing).</p>
<p><a href="catalog/cloudflare-one.md"><strong>Cloudflare One</strong></a> — Guides Cloudflare One Zero Trust and SASE work across Access, Gateway, WARP, Tunnel, Cloudflare WAN, DLP…</p>
<p><a href="catalog/cloudflare-one-migrations.md"><strong>Cloudflare One Migrations</strong></a> — Plans migrations from Zscaler ZIA/ZPA, Palo Alto, legacy VPN, SWG, or SASE stacks to Cloudflare One.</p>
<p><a href="catalog/deployment-drift-investigator.md"><strong>Deployment Drift Investigator</strong></a> — Investigate why a deployed app, cluster, or environment no longer matches expected behavior.</p>
<p><a href="catalog/durable-objects.md"><strong>Durable Objects</strong></a> — Create and review Cloudflare Durable Objects.</p>
<p><a href="catalog/sandbox-sdk.md"><strong>Sandbox SDK</strong></a> — Build sandboxed applications for secure code execution.</p>
<p><a href="catalog/workers-best-practices.md"><strong>Workers Best Practices</strong></a> — Reviews and authors Cloudflare Workers code against production best practices.</p>
<p><a href="catalog/wrangler.md"><strong>Wrangler</strong></a> — Cloudflare Workers CLI for deploying, developing, and managing Workers, KV, R2, D1, Vectorize, Hyperdrive…</p>

<a id="communication-and-productivity"></a>

## ✍️ Communication & Productivity

*Say more with less, then hand the work over cleanly.*

<p><a href="catalog/caveman.md"><strong>Caveman</strong></a> — Ultra-compressed communication mode.</p>
<p><a href="catalog/prompt-improver.md"><strong>Prompt Improver</strong></a> — This skill enriches vague prompts with targeted research and clarification before execution.</p>
<p><a href="catalog/prompt-lint.md"><strong>Prompt Lint</strong></a> — Audit a prompt for token waste and suggest a leaner rewrite.</p>
<p><a href="catalog/session-handoff-brief.md"><strong>Session Handoff Brief</strong></a> — Turn current work into a concise next-session handoff.</p>

<a id="debugging-and-quality"></a>

## 🧭 Debugging & Quality

*Follow the evidence, find the fault, and verify the fix.*

<p><a href="catalog/diagnose.md"><strong>Diagnose</strong></a> — Disciplined diagnosis loop for hard bugs and performance regressions.</p>
<p><a href="catalog/evidence-first-debugging.md"><strong>Evidence First Debugging</strong></a> — Use when debugging any bug, error, or unexpected behavior.</p>
<p><a href="catalog/qa.md"><strong>QA</strong></a> — Interactive QA session where user reports bugs or issues conversationally, and the agent files GitHub issues.</p>
<p><a href="catalog/web-perf.md"><strong>Web Perf</strong></a> — Analyzes web performance using Chrome DevTools MCP.</p>

<a id="engineering-workflow"></a>

## 🛠️ Engineering Workflow

*Understand the codebase and keep useful work moving.*

<p><a href="catalog/codebase-indexer.md"><strong>Codebase Indexer</strong></a> — Use when opening an existing codebase for the first time, or after completing a feature or bugfix…</p>
<p><a href="catalog/design-an-interface.md"><strong>Design An Interface</strong></a> — Generate multiple radically different interface designs for a module using parallel sub-agents.</p>
<p><a href="catalog/find-skills.md"><strong>Find Skills</strong></a> — Helps users discover and install agent skills when they ask questions like &quot;how do I do X&quot;, &quot;find a skill…</p>
<p><a href="catalog/improve-codebase-architecture.md"><strong>Improve Codebase Architecture</strong></a> — Explore a codebase to find opportunities for architectural improvement, focusing on making the codebase more…</p>
<p><a href="catalog/planning-with-files.md"><strong>Planning With Files</strong></a> — Transforms workflow to use Manus-style persistent markdown files for planning, progress tracking, and…</p>
<p><a href="catalog/scaffold-exercises.md"><strong>Scaffold Exercises</strong></a> — Create exercise directory structures with sections, problems, solutions, and explainers that pass linting.</p>
<p><a href="catalog/to-issues.md"><strong>To Issues</strong></a> — Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using…</p>
<p><a href="catalog/understand-dashboard-lite.md"><strong>Understand Dashboard Lite</strong></a> — Launch the existing Understand Anything dashboard for a lite-generated graph without duplicating the…</p>
<p><a href="catalog/understand-lite.md"><strong>Understand Lite</strong></a> — Build a low-token, deterministic structural knowledge graph for a repo using cheap scanning and import…</p>
<p><a href="catalog/understand-lite-diff.md"><strong>Understand Lite Diff</strong></a> — Build a cheap diff overlay for a lite-generated graph so the shared dashboard can highlight changed and…</p>
<p><a href="catalog/writing-skills.md"><strong>Writing Skills</strong></a> — Use when creating new skills, editing existing skills, or verifying skills work before deployment</p>

<a id="frontend-and-design"></a>

## ✦ Frontend & Design

*Interfaces with taste, motion, accessibility, and sharp edges.*

<p><a href="catalog/animation-vocabulary.md"><strong>Animation Vocabulary</strong></a> — Reverse-lookup glossary that turns a vague description of a web animation or motion effect into its exact…</p>
<p><a href="catalog/apple-accessibility-audit.md"><strong>Apple Accessibility Audit</strong></a> — Perform Apple-style accessibility audits of UI designs, screenshots, prototypes, web/app pages, or design…</p>
<p><a href="catalog/apple-ui-design.md"><strong>Apple UI Design</strong></a> — Apple-inspired clean, minimal, premium UI design.</p>
<p><a href="catalog/design-with-taste.md"><strong>Design With Taste</strong></a> — Apply the &quot;Family Values&quot; design philosophy to every UI you build.</p>
<p><a href="catalog/emil-design-eng.md"><strong>Emil Design Eng</strong></a> — This skill encodes Emil Kowalski's philosophy on UI polish, component design, animation decisions, and the…</p>
<p><a href="catalog/frontend-design.md"><strong>Frontend Design</strong></a> — Create distinctive, production-grade frontend interfaces with high design quality.</p>
<p><a href="catalog/frontend-patterns.md"><strong>Frontend Patterns</strong></a> — Frontend development patterns for React, Next.js, state management, performance optimization, and UI best…</p>
<p><a href="catalog/gpt-taste.md"><strong>GPT Taste</strong></a> — Elite UX/UI &amp; Advanced GSAP Motion Engineer.</p>
<p><a href="catalog/impeccable.md"><strong>Impeccable</strong></a> — Use when the user wants to design, redesign, shape, critique, audit, polish, clarify, distill, harden…</p>
<p><a href="catalog/interaction-design.md"><strong>Interaction Design</strong></a> — Design and implement microinteractions, motion design, transitions, and user feedback patterns.</p>
<p><a href="catalog/make-interfaces-feel-better.md"><strong>Make Interfaces Feel Better</strong></a> — Design engineering principles for making interfaces feel polished.</p>
<p><a href="catalog/review-animations.md"><strong>Review Animations</strong></a> — Reviews animation and motion code against a high craft bar derived from Emil Kowalski's design engineering…</p>
<p><a href="catalog/shadcn.md"><strong>Shadcn</strong></a> — Manages shadcn components and projects — adding, searching, fixing, debugging, styling, and composing UI.</p>
<p><a href="catalog/skeleton-loader-fidelity.md"><strong>Skeleton Loader Fidelity</strong></a> — Audit, design, and fix skeleton loaders so loading states preserve the real content footprint, avoid…</p>
<p><a href="catalog/stitch-loop.md"><strong>Stitch Loop</strong></a> — Teaches agents to iteratively build websites using Stitch with an autonomous baton-passing loop pattern</p>
<p><a href="catalog/stitch-ui-design.md"><strong>Stitch UI Design</strong></a> — Expert guide for creating effective prompts for Google Stitch AI UI design tool.</p>
<p><a href="catalog/svg-animations.md"><strong>SVG Animations</strong></a> — Create beautiful, performant SVG animations and illustrations.</p>
<p><a href="catalog/tailwindcss-advanced-layouts.md"><strong>Tailwindcss Advanced Layouts</strong></a> — Tailwind CSS advanced layout techniques including CSS Grid and Flexbox patterns</p>
<p><a href="catalog/ui-animations.md"><strong>UI Animations</strong></a> — Use when implementing animations in any UI (SwiftUI, CSS, React).</p>
<p><a href="catalog/ui-design-system.md"><strong>UI Design System</strong></a> — UI design system toolkit for Senior UI Designer including design token generation, component documentation…</p>
<p><a href="catalog/ui-ux-pro-max.md"><strong>UI UX Pro Max</strong></a> — UI/UX design intelligence for web and mobile.</p>
<p><a href="catalog/userinterface-wiki.md"><strong>Userinterface Wiki</strong></a> — UI/UX best practices for web interfaces.</p>
<p><a href="catalog/vercel-react-best-practices.md"><strong>Vercel React Best Practices</strong></a> — React and Next.js performance optimization guidelines from Vercel Engineering.</p>
<p><a href="catalog/web-design-guidelines.md"><strong>Web Design Guidelines</strong></a> — Review UI code for Web Interface Guidelines compliance.</p>

<a id="native-and-mobile"></a>

## 📱 Native & Mobile

*Small screens, native conventions, and thumb-friendly decisions.*

<p><a href="catalog/swift-macos-menubar.md"><strong>Swift Macos Menubar</strong></a> — Use when working on Swift, SwiftUI, AppKit, MenuBarExtra, packaging, or macOS menubar app behavior in this…</p>
<p><a href="catalog/swiftui-ui-patterns.md"><strong>Swiftui UI Patterns</strong></a> — Best practices and example-driven guidance for building SwiftUI views and components, including navigation…</p>
<p><a href="catalog/thumb-first.md"><strong>Thumb First</strong></a> — One-stop mobile review — the umbrella for the thumb-first suite.</p>
<p><a href="catalog/thumb-first-design.md"><strong>Thumb First Design</strong></a> — The design-judgment layer of the thumb-first mobile suite — decides WHAT the right mobile pattern is and…</p>
<p><a href="catalog/thumb-first-platform.md"><strong>Thumb First Platform</strong></a> — The technical-verification layer of the thumb-first mobile suite — finds and fixes objective platform…</p>

<a id="planning-and-learning"></a>

## 🧠 Planning & Learning

*Think clearly before the expensive part begins.*

<p><a href="catalog/grill-me.md"><strong>Grill Me</strong></a> — Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each…</p>
<p><a href="catalog/mece.md"><strong>Mece</strong></a> — Validate or decompose any specification, plan, or requirement list using the MECE framework (Mutually…</p>
<p><a href="catalog/system-design-tutor.md"><strong>System Design Tutor</strong></a> — An expert system design tutor that quizzes the user on system design concepts drawn from a database of top…</p>
<p><a href="catalog/teach.md"><strong>Teach</strong></a> — Teach the user a new skill or concept, within this workspace.</p>
<p><a href="catalog/technical-decision-framework.md"><strong>Technical Decision Framework</strong></a> — Guide technical tradeoff decisions for build, stack, and scope</p>

<a id="security"></a>

## 🛡️ Security

*Catch secrets, harden boundaries, and reduce avoidable risk.*

<p><a href="catalog/security-review.md"><strong>Security Review</strong></a> — Use this skill when adding authentication, handling user input, working with secrets, creating API…</p>
<p><a href="catalog/sentinel-scan.md"><strong>Sentinel Scan</strong></a> — Scan codebase for leaked secrets, API keys, and sensitive data.</p>
<p><a href="catalog/turnstile-spin.md"><strong>Turnstile Spin</strong></a> — Set up Cloudflare Turnstile end-to-end in a project — scan the codebase, create the widget via the…</p>

---

Built as a personal shelf, shared so useful instructions do not stay trapped on one machine.

See [ATTRIBUTION.md](ATTRIBUTION.md) for creator and license details.
