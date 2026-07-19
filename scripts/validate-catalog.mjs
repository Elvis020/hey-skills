#!/usr/bin/env node

import { access, readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const catalog = JSON.parse(await readFile(resolve(root, "catalog.json"), "utf8"));
const allowedProvenance = new Set([
  "original",
  "adapted",
  "third-party",
  "reference-only",
  "local",
]);
const seen = new Set();
const errors = [];

if (!Array.isArray(catalog.skills)) {
  errors.push("catalog.skills must be an array");
} else {
  for (const [index, skill] of catalog.skills.entries()) {
    const label = skill.name || `entry ${index + 1}`;

    if (!/^[a-z0-9-]+$/.test(skill.name || "")) {
      errors.push(`${label}: name must use lowercase letters, numbers, and hyphens`);
    }
    if (seen.has(skill.name)) errors.push(`${label}: duplicate name`);
    seen.add(skill.name);

    for (const field of ["summary", "category", "author", "license"]) {
      if (typeof skill[field] !== "string" || !skill[field].trim()) {
        errors.push(`${label}: ${field} is required`);
      }
    }

    if (!allowedProvenance.has(skill.provenance)) {
      errors.push(`${label}: invalid provenance`);
    }

    if (skill.provenance === "reference-only") {
      if (skill.path) errors.push(`${label}: reference-only skills cannot have a local path`);
      if (!skill.source) errors.push(`${label}: reference-only skills require a source URL`);
    } else {
      const expectedPath = `skills/${skill.name}`;
      if (skill.path !== expectedPath) {
        errors.push(`${label}: path must be ${expectedPath}`);
      } else {
        try {
          const skillFile = resolve(root, skill.path, "SKILL.md");
          await access(skillFile);
          const content = await readFile(skillFile, "utf8");
          const frontmatter = content.match(/^---\n([\s\S]*?)\n---\n/);
          if (!frontmatter) {
            errors.push(`${label}: SKILL.md requires YAML frontmatter`);
          } else {
            const fields = frontmatter[1]
              .split("\n")
              .filter((line) => /^[a-z][a-z0-9-]*:/.test(line))
              .map((line) => line.slice(0, line.indexOf(":")));
            const unexpected = fields.filter((field) => !["name", "description"].includes(field));
            if (!fields.includes("name") || !fields.includes("description")) {
              errors.push(`${label}: SKILL.md requires name and description fields`);
            }
            if (unexpected.length) {
              errors.push(`${label}: unexpected frontmatter fields: ${unexpected.join(", ")}`);
            }
            const declaredName = frontmatter[1].match(/^name:\s*(.+)$/m)?.[1]?.trim();
            if (declaredName !== skill.name) {
              errors.push(`${label}: SKILL.md name must match the catalog and folder`);
            }
          }
        } catch {
          errors.push(`${label}: ${skill.path}/SKILL.md does not exist`);
        }
      }
    }

    if (!["original", "local"].includes(skill.provenance) && !skill.source) {
      errors.push(`${label}: non-original skills require a source URL`);
    }

    if (!skill.showcase || typeof skill.showcase.featured !== "boolean") {
      errors.push(`${label}: showcase.featured must be a boolean`);
    } else if (skill.showcase.artwork) {
      try {
        await access(resolve(root, skill.showcase.artwork));
      } catch {
        errors.push(`${label}: artwork ${skill.showcase.artwork} does not exist`);
      }
    }
  }
}

if (errors.length) {
  console.error(`Catalog validation failed:\n- ${errors.join("\n- ")}`);
  process.exit(1);
}

console.log(`Catalog valid: ${catalog.skills.length} skill(s)`);
