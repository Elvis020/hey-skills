#!/usr/bin/env node

import { cp, lstat, mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const installedRoots = [
  join(homedir(), ".codex", "skills"),
  join(homedir(), ".agents", "skills"),
];
const lockPath = join(homedir(), ".agents", ".skill-lock.json");
const force = process.argv.includes("--force");

const excludedNames = new Set([
  "codex-caveman",
  "commit",
  "g-commit",
  "gcommit",
  "security-scan",
  "token-efficiency",
]);

const categoryGroups = {
  "Frontend & Design": [
    "animation-vocabulary", "apple-accessibility-audit", "apple-ui-design",
    "design-with-taste", "emil-design-eng", "frontend-design", "frontend-patterns",
    "gpt-taste", "impeccable", "interaction-design", "make-interfaces-feel-better",
    "review-animations", "shadcn", "skeleton-loader-fidelity", "stitch-loop",
    "stitch-ui-design", "svg-animations", "tailwindcss-advanced-layouts",
    "ui-animations", "ui-design-system", "ui-ux-pro-max", "userinterface-wiki",
    "vercel-react-best-practices", "web-design-guidelines",
  ],
  "Backend & Data": [
    "java-coding-standards", "logging-best-practices", "pattern-fit-architecture",
    "supabase-postgres-best-practices",
  ],
  "Cloud & Infrastructure": [
    "agents-sdk", "cloudflare", "cloudflare-email-service", "cloudflare-one",
    "cloudflare-one-migrations", "deployment-drift-investigator", "durable-objects",
    "sandbox-sdk", "workers-best-practices", "wrangler",
  ],
  "Native & Mobile": [
    "swift-macos-menubar", "swiftui-ui-patterns", "thumb-first",
    "thumb-first-design", "thumb-first-platform",
  ],
  "Debugging & Quality": [
    "diagnose", "evidence-first-debugging", "qa", "web-perf",
  ],
  Security: [
    "security-review", "sentinel-scan", "turnstile-spin",
  ],
  "Engineering Workflow": [
    "codebase-indexer", "design-an-interface", "find-skills",
    "improve-codebase-architecture", "planning-with-files", "scaffold-exercises",
    "to-issues", "understand-dashboard-lite", "understand-lite",
    "understand-lite-diff", "writing-skills",
  ],
  "Planning & Learning": [
    "grill-me", "mece", "system-design-tutor", "teach",
    "technical-decision-framework",
  ],
  "Communication & Productivity": [
    "caveman", "prompt-improver", "prompt-lint", "session-handoff-brief",
    "token-efficiency",
  ],
};

const categoryByName = new Map(
  Object.entries(categoryGroups).flatMap(([category, names]) =>
    names.map((name) => [name, category]),
  ),
);

const cloudflareSkills = new Set([
  "agents-sdk", "cloudflare", "cloudflare-email-service", "cloudflare-one",
  "cloudflare-one-migrations", "durable-objects", "sandbox-sdk", "web-perf",
  "workers-best-practices", "wrangler",
]);
const neutralizedThirdParty = new Set([
  "cloudflare-email-service", "frontend-design", "thumb-first-design",
  "thumb-first-platform", "writing-skills",
]);

const sourceOverrides = {
  "codebase-indexer": {
    provenance: "original",
    author: "Elvis020",
    source: "https://github.com/Elvis020/codebase-indexer",
    license: "Unlicensed",
  },
  "evidence-first-debugging": {
    provenance: "third-party",
    author: "Augani",
    source: "https://github.com/Augani/evidence-first-debugging",
    license: "MIT",
  },
  "frontend-design": {
    provenance: "third-party",
    author: "Anthropic",
    source: "https://github.com/anthropics/skills/tree/main/skills/frontend-design",
    license: "Apache-2.0",
  },
  "planning-with-files": {
    provenance: "third-party",
    author: "OthmanAdi",
    source: "https://github.com/OthmanAdi/planning-with-files",
    license: "MIT",
  },
};

for (const name of cloudflareSkills) {
  sourceOverrides[name] = {
    provenance: "third-party",
    author: "Cloudflare",
    source: "https://github.com/cloudflare/skills",
    license: "Apache-2.0",
  };
}

const ignoredDirectories = new Set([
  ".claude", ".git", ".github", ".minimax", "_tmp_code-review-graph",
  "agents", "evals", "stats", "tests", "__pycache__",
]);
const ignoredFiles = new Set([
  ".DS_Store", "AGENTS.md", "BENCHMARK.md", "CLAUDE.md", "README.md",
  "skill-report.json",
]);

function cleanScalar(value) {
  const trimmed = value.trim();
  if ((trimmed.startsWith('"') && trimmed.endsWith('"')) ||
      (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function parseSkill(content, fallbackName) {
  if (!content.startsWith("---")) return null;
  const end = content.indexOf("\n---", 3);
  if (end === -1) return null;

  const frontmatter = content.slice(4, end).split("\n");
  let name = fallbackName;
  let description = "";

  for (let index = 0; index < frontmatter.length; index += 1) {
    const line = frontmatter[index];
    if (line.startsWith("name:")) name = cleanScalar(line.slice(5));
    if (line.startsWith("description:")) {
      const value = line.slice(12).trim();
      if (value === ">" || value === "|") {
        const parts = [];
        while (frontmatter[index + 1]?.match(/^\s+/)) {
          parts.push(frontmatter[index + 1].trim());
          index += 1;
        }
        description = parts.join(" ");
      } else {
        description = cleanScalar(value);
      }
    }
  }

  if (!name || !description) return null;
  const body = content.slice(end + 4).replace(/^\s+/, "");
  return { name, description: description.replace(/\s+/g, " "), body };
}

function summaryFrom(description) {
  const firstSentence = description.match(/^.*?[.!?](?:\s|$)/)?.[0]?.trim();
  const summary = firstSentence || description;
  return summary.length > 190 ? `${summary.slice(0, 187).trim()}…` : summary;
}

function neutralizeSkill(name, parsed) {
  let { description, body } = parsed;

  if (name === "codebase-indexer") {
    description = description.replace("so Claude does not", "so the agent does not");
    body = body
      .replaceAll("~/.claude/skills/codebase-indexer/", "<agent-skills-directory>/codebase-indexer/")
      .replaceAll("CLAUDE.md", "AGENTS.md or equivalent project instructions");
  }
  if (name === "prompt-lint" || name === "frontend-design") {
    body = body.replaceAll("Claude", "the agent");
  }
  if (name === "turnstile-spin") {
    body = body.replaceAll(
      ".claude/skills/turnstile-spin/SKILL.md",
      "<agent-skills-directory>/turnstile-spin/SKILL.md",
    );
  }
  if (name === "cloudflare-email-service") {
    body = body.replace(
      "(Claude Code, Cursor, Copilot, etc.)",
      "(any supported coding agent)",
    );
  }
  if (name === "thumb-first-design" || name === "thumb-first-platform") {
    body = body
      .replaceAll("~/.claude/skills/", "<agent-skills-directory>/")
      .replaceAll("Claude", "the agent");
  }
  if (name === "writing-skills") {
    body = body
      .replaceAll("~/.claude/skills", "<agent-skills-directory>")
      .replaceAll("~/.agents/skills/", "<agent-skills-directory>/")
      .replaceAll("CLAUDE.md", "project instruction files")
      .replaceAll("Claude Code", "an agent")
      .replaceAll("Codex", "another agent")
      .replaceAll("Claude", "the agent");
  }
  if (name === "understand-lite") {
    body = body.replace('     "$HOME/.codex/understand-anything/understand-anything-plugin" \\\n', "");
  }

  return { ...parsed, description, body };
}

async function readLock() {
  try {
    return JSON.parse(await readFile(lockPath, "utf8")).skills || {};
  } catch {
    return {};
  }
}

async function findCandidates(lock) {
  const candidates = new Map();

  for (const installedRoot of installedRoots) {
    let folders = [];
    try {
      folders = await readdir(installedRoot);
    } catch {
      continue;
    }

    for (const folder of folders.sort()) {
      if (folder === ".system") continue;
      const directory = join(installedRoot, folder);
      let skillFile = join(directory, "SKILL.md");
      try {
        await lstat(skillFile);
      } catch {
        skillFile = join(directory, "skill.md");
        try {
          await lstat(skillFile);
        } catch {
          continue;
        }
      }

      const content = await readFile(skillFile, "utf8");
      const parsed = parseSkill(content, folder);
      if (!parsed || excludedNames.has(parsed.name)) continue;

      const current = candidates.get(parsed.name);
      const isLockedSource = Boolean(lock[parsed.name]) && installedRoot.includes(".agents");
      if (!current || isLockedSource) {
        candidates.set(parsed.name, { directory, skillFile, parsed, folder });
      }
    }
  }

  return candidates;
}

function sourceDetails(name, lock) {
  if (sourceOverrides[name]) {
    const details = { ...sourceOverrides[name] };
    if (neutralizedThirdParty.has(name)) details.provenance = "adapted";
    return details;
  }
  const locked = lock[name];
  if (locked) {
    const repository = locked.sourceUrl.replace(/\.git$/, "");
    return {
      provenance: neutralizedThirdParty.has(name) ? "adapted" : "third-party",
      author: locked.source.split("/")[0],
      source: repository,
      license: "See upstream repository",
    };
  }
  return {
    provenance: "local",
    author: "Local collection — attribution pending",
    source: null,
    license: "Unverified",
  };
}

function shouldCopy(source, sourceRoot) {
  const relative = source.slice(sourceRoot.length).replace(/^\//, "");
  if (!relative) return true;
  const parts = relative.split("/");
  if (parts.some((part) => ignoredDirectories.has(part))) return false;
  const file = basename(source);
  if (ignoredFiles.has(file)) return false;
  if (file.toLowerCase() === "skill.md") return false;
  if (/\.(pdf|pyc)$/i.test(file)) return false;
  return !file.startsWith(".");
}

async function importSkill(candidate, entry) {
  const target = resolve(root, entry.path);
  try {
    await lstat(target);
    if (!force) throw new Error(`${entry.name} already exists; rerun with --force to replace it.`);
    await rm(target, { recursive: true, force: true });
  } catch (error) {
    if (error?.code !== "ENOENT") throw error;
  }

  await mkdir(target, { recursive: true });
  await cp(candidate.directory, target, {
    recursive: true,
    dereference: true,
    filter: (source) => shouldCopy(source, candidate.directory),
  });

  let body = candidate.parsed.body;
  if (entry.name === "technical-decision-framework") {
    body = body.replace(/\n- Original source PDF:[^\n]*/g, "");
  }
  const normalized = `---\nname: ${entry.name}\ndescription: ${JSON.stringify(candidate.parsed.description)}\n---\n\n${body.trim()}\n`;
  await writeFile(join(target, "SKILL.md"), normalized);
}

function artworkFor(category) {
  if (category === "Frontend & Design" || category === "Native & Mobile") {
    return "assets/showcase/design.svg";
  }
  if (["Debugging & Quality", "Security"].includes(category)) {
    return "assets/showcase/debug.svg";
  }
  return "assets/showcase/handoff.svg";
}

function buildAttribution(entries) {
  const sourced = new Map();
  const local = [];

  for (const entry of entries) {
    if (!entry.source) {
      local.push(entry);
      continue;
    }
    const key = entry.source;
    if (!sourced.has(key)) sourced.set(key, []);
    sourced.get(key).push(entry);
  }

  const lines = [
    "# Attribution",
    "",
    "Hey Skills includes original work and skills collected from other creators. Upstream ownership and license terms remain with their respective creators.",
    "",
    "## Credited sources",
    "",
  ];

  for (const [source, skills] of [...sourced].sort(([a], [b]) => a.localeCompare(b))) {
    const first = skills[0];
    lines.push(
      `### [${first.author}](${source})`,
      "",
      `- Skills: ${skills.map((skill) => `\`${skill.name}\``).sort().join(", ")}`,
      `- License: ${first.license}`,
      `- Source: ${source}`,
      "",
    );
  }

  if (local.length) {
    lines.push(
      "## Attribution pending",
      "",
      "These skills were found in the local collection without installation-source metadata. They are included for review and should not be described as original work until their provenance is confirmed.",
      "",
      ...local.map((skill) => `- \`${skill.name}\``).sort(),
      "",
    );
  }

  lines.push(
    "## Policy",
    "",
    "Existing license notices are preserved inside imported skill folders. If a source or license is corrected later, update both `catalog.json` and this file.",
    "",
  );
  return lines.join("\n");
}

const lock = await readLock();
const candidates = await findCandidates(lock);
const entries = [];

for (const [name, candidate] of [...candidates].sort(([a], [b]) => a.localeCompare(b))) {
  candidate.parsed = neutralizeSkill(name, candidate.parsed);
  const category = categoryByName.get(name) || "Other";
  const provenance = sourceDetails(name, lock);
  const entry = {
    name,
    summary: summaryFrom(candidate.parsed.description),
    category,
    path: `skills/${name}`,
    ...provenance,
    showcase: {
      featured: false,
      artwork: artworkFor(category),
    },
  };
  await importSkill(candidate, entry);
  entries.push(entry);
}

await writeFile(
  resolve(root, "catalog.json"),
  `${JSON.stringify({ $schema: "./catalog.schema.json", skills: entries }, null, 2)}\n`,
);
await writeFile(resolve(root, "ATTRIBUTION.md"), buildAttribution(entries));
console.log(`Imported ${entries.length} deduplicated skill(s).`);
