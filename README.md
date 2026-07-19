<p align="center">
  <img src="assets/hey-skills-hero.svg" alt="Hey Skills — portable skills for capable agents" width="100%">
</p>

<p align="center">
  A personal library of reusable skills for capable agents.<br>
  Browse what you need, then install one skill or the complete collection.
</p>

<p align="center">
  <a href="SKILLS.md"><strong>Browse skills</strong></a> ·
  <a href="https://github.com/Elvis020/hey-skills/archive/refs/heads/main.zip">Download all</a> ·
  <a href="ATTRIBUTION.md">Credits</a>
</p>

<table>
  <tr>
    <td width="33%" valign="top">
      <img src="assets/showcase/debug.svg" alt="Debugging illustration" width="100%">
      <h3>Debug with evidence</h3>
      <p>Trace unexpected behavior from what the system actually shows.</p>
    </td>
    <td width="33%" valign="top">
      <img src="assets/showcase/design.svg" alt="Design illustration" width="100%">
      <h3>Design with clarity</h3>
      <p>Turn rough product ideas into focused interface decisions.</p>
    </td>
    <td width="33%" valign="top">
      <img src="assets/showcase/handoff.svg" alt="Handoff illustration" width="100%">
      <h3>Work with continuity</h3>
      <p>Carry useful context cleanly between people and sessions.</p>
    </td>
  </tr>
</table>

## Install from your terminal

Install one skill into a folder you choose:

```sh
npx github:Elvis020/hey-skills add <skill-name> --to ./skills
```

Install every published skill:

```sh
npx github:Elvis020/hey-skills add --all --to ./skills
```

Use `--to` to point at any agent's skills directory. The collection itself is not tied to Claude, Codex, or another provider.

The complete categorized list lives in **[SKILLS.md](SKILLS.md)**. Skills adapted or collected from other creators retain clear source and license credits in **[ATTRIBUTION.md](ATTRIBUTION.md)**.

