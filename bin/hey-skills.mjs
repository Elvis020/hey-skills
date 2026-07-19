#!/usr/bin/env node

import { access, cp, mkdir, readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const catalog = JSON.parse(await readFile(resolve(root, "catalog.json"), "utf8"));
const published = catalog.skills.filter((skill) => skill.provenance !== "reference-only");
const args = process.argv.slice(2);

function valueAfter(flag) {
  const index = args.indexOf(flag);
  return index === -1 ? null : args[index + 1];
}

function printHelp() {
  console.log(`Hey Skills

Usage:
  hey-skills list
  hey-skills add <skill-name> [--to <directory>]
  hey-skills add --all [--to <directory>]

Examples:
  npx github:Elvis020/hey-skills list
  npx github:Elvis020/hey-skills add skill-name --to ./skills
  npx github:Elvis020/hey-skills add --all --to ./skills

The destination defaults to ./skills.`);
}

function fail(message) {
  console.error(`Error: ${message}`);
  process.exit(1);
}

async function install(skill, destination) {
  const source = resolve(root, skill.path);
  const target = resolve(destination, skill.name);

  try {
    await access(resolve(source, "SKILL.md"));
  } catch {
    fail(`${skill.name} is listed but its SKILL.md file is missing.`);
  }

  try {
    await access(target);
    fail(`${target} already exists. Remove it before installing again.`);
  } catch (error) {
    if (error?.code !== "ENOENT") throw error;
  }

  await cp(source, target, { recursive: true, errorOnExist: true });
  console.log(`Installed ${skill.name} → ${target}`);
}

const command = args[0];

if (!command || command === "help" || args.includes("--help") || args.includes("-h")) {
  printHelp();
  process.exit(0);
}

if (command === "list") {
  if (!catalog.skills.length) {
    console.log("No skills have been published yet.");
    process.exit(0);
  }

  for (const skill of catalog.skills) {
    const availability = skill.provenance === "reference-only" ? "source only" : "installable";
    console.log(`${skill.name.padEnd(32)} ${skill.category} · ${availability}`);
  }
  process.exit(0);
}

if (command !== "add") fail(`Unknown command: ${command}`);

const destinationValue = valueAfter("--to");
if (args.includes("--to") && !destinationValue) fail("--to requires a directory.");
const destination = resolve(process.cwd(), destinationValue || "skills");
await mkdir(destination, { recursive: true });

if (args.includes("--all")) {
  if (!published.length) fail("No downloadable skills have been published yet.");
  for (const skill of published) await install(skill, destination);
  console.log(`Done. Installed ${published.length} skill${published.length === 1 ? "" : "s"}.`);
  process.exit(0);
}

const name = args[1];
if (!name || name.startsWith("--")) fail("Provide a skill name or use --all.");
if (!/^[a-z0-9-]+$/.test(name)) fail("Skill names use lowercase letters, numbers, and hyphens.");

const skill = catalog.skills.find((entry) => entry.name === name);
if (!skill) fail(`Unknown skill: ${name}. Run \"hey-skills list\" to browse names.`);
if (skill.provenance === "reference-only") {
  fail(`${name} is reference-only. Get it from ${skill.source}`);
}

await install(skill, destination);
