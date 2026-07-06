from pathlib import Path

p = Path("frontend/src/pages/CompanyProblems.jsx")
lines = p.read_text(encoding="utf-8").splitlines()
out = lines[:22] + lines[896:]
text = "\n".join(out)
text = text.replace(
    "const metadata = PROBLEM_METADATA[title];\n            if (!metadata) return null;",
    'const metadata = getProblemMetadata(title) || { topic: "Arrays", companies: DEFAULT_PROBLEM_COMPANIES };',
)
p.write_text(text + "\n", encoding="utf-8")
print("patched", len(lines), "->", len(out))
