import os, json, re

SRC = "/sessions/relaxed-charming-darwin/mnt/Claude Cowork/OUTPUTS/Paper summary"

def parse_md(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    # --- frontmatter ---
    fm_match = re.match(r'^---\n(.*?)\n---\n', raw, re.DOTALL)
    if not fm_match:
        return None
    fm_text = fm_match.group(1)
    body    = raw[fm_match.end():]

    fm = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"')

    year = fm.get("year","")
    try:
        year = int(year)
    except:
        pass

    # --- summary blocks (bold-headed paragraphs) ---
    def extract(label):
        pattern = rf'\*\*{re.escape(label)}[^*]*\*\*(.*?)(?=\n\n\*\*|\Z)'
        m = re.search(pattern, body, re.DOTALL)
        return m.group(1).strip() if m else ""

    background = extract("Background to the study")
    importance  = extract("Importance to the field")
    methods     = extract("Methods")
    findings    = extract("Key findings")

    # fallback: join all body paragraphs if no structured blocks
    if not any([background, importance, findings]):
        paras = [p.strip() for p in body.split("\n\n") if p.strip() and not p.startswith("#")]
        background = paras[0] if paras else ""
        findings   = paras[-1] if len(paras) > 1 else ""

    # tags from filename
    slug = os.path.basename(path).replace("_summary.md","")

    return {
        "year":       year,
        "type":       fm.get("type","Journal Article"),
        "title":      fm.get("title",""),
        "authors":    fm.get("authors",""),
        "journal":    fm.get("journal",""),
        "volume":     fm.get("volume",""),
        "issue":      fm.get("issue",""),
        "pages":      fm.get("pages",""),
        "doi":        fm.get("doi",""),
        "slug":       slug,
        "summary": {
            "background": background,
            "importance":  importance,
            "methods":     methods,
            "findings":    findings
        }
    }

pubs = []
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith("_summary.md"):
        continue
    result = parse_md(os.path.join(SRC, fn))
    if result and result["title"]:
        pubs.append(result)

# sort newest first
pubs.sort(key=lambda p: (p["year"] if isinstance(p["year"],int) else 0), reverse=True)

out = "/sessions/relaxed-charming-darwin/mnt/outputs/publications.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(pubs, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(pubs)} publications to {out}")
