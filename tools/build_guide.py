"""Construit une page guide combien-net.fr à partir d'un brouillon (TITLE/DESCRIPTION/H1/LEAD + sections HTML)."""
import sys, re, html, pathlib

TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://combien-net.fr/{slug}/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="wrap">

<header>
  <span class="tag">Guide gratuit · micro-entreprise 2026</span>
  <h1>{h1}</h1>
  <p class="lead">{lead}</p>
</header>

{body}

<section>
  <h2>Autres simulateurs</h2>
  <div class="more">
    <a href="../tarif-journalier-freelance/"><strong>Tarif journalier freelance</strong><span>Le TJM et le taux horaire à facturer pour atteindre votre revenu net.</span></a>
    <a href="../revenu-net-micro-entrepreneur/"><strong>Revenu net micro-entrepreneur</strong><span>Ce qu'il vous reste après cotisations, impôt et frais.</span></a>
    <a href="../"><strong>ARE ou ARCE</strong><span>Capital ou maintien mensuel de vos allocations chômage.</span></a>
  </div>
</section>

<div class="cta">
  <h2>Le bon calcul ne sert à rien sans clients.</h2>
  <p>Le Kit 5 Premiers Clients rassemble les messages de prospection et le tableau de suivi pour décrocher vos premières missions en freelance.</p>
  <a class="btn" href="https://bouzidi837.gumroad.com/l/kit-premiers-clients" target="_blank" rel="noopener">Voir le kit</a>
</div>

<footer>
  <span>Sources : <a href="https://www.autoentrepreneur.urssaf.fr/" target="_blank" rel="noopener">Urssaf auto-entrepreneur</a>, <a href="https://entreprendre.service-public.gouv.fr/" target="_blank" rel="noopener">Service-Public Entreprendre</a>. Barèmes 2026.</span>
  <span>Ce guide ne remplace pas un conseil personnalisé.</span>
</footer>
</div>
</body>
</html>
"""

def build(draft_path, slug, root="."):
    txt = pathlib.Path(draft_path).read_text(encoding="utf-8")
    txt = re.sub(r"```\w*", "", txt)
    meta = {}
    for k in ("TITLE", "DESCRIPTION", "H1", "LEAD"):
        m = re.search(rf"^\**{k}\**\s*:\s*(.+)$", txt, re.M)
        meta[k] = m.group(1).strip() if m else ""
    body = "\n\n".join(s.strip() for s in re.findall(r"<section>.*?</section>", txt, re.S))
    out = pathlib.Path(root) / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(TEMPLATE.format(title=html.escape(meta["TITLE"]), desc=html.escape(meta["DESCRIPTION"]),
                                   slug=slug, h1=meta["H1"], lead=meta["LEAD"], body=body), encoding="utf-8")
    return out

if __name__ == "__main__":
    print(build(sys.argv[1], sys.argv[2]))
