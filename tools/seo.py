"""Passe SEO sur toutes les pages : navigation, fil d'Ariane, maillage interne et données structurées.

À relancer après build_net_pages.py ou build_guide.py :  python3 tools/seo.py
Le script est idempotent : il remplace ce qu'il a déjà inséré (entre les marqueurs <!--seo:...-->).
"""
import json
import pathlib
import re

BASE = "https://combien-net.fr/"
ROOT = pathlib.Path(__file__).resolve().parent.parent

# Pages principales : slug -> (nom court, description courte, type)
PAGES = {
    "": ("ARE ou ARCE", "Capital ARCE ou maintien de l'ARE à la création", "outil"),
    "revenu-net-micro-entrepreneur/": ("Revenu net micro-entrepreneur", "Ce qu'il reste après cotisations et impôt", "outil"),
    "tarif-journalier-freelance/": ("Tarif journalier (TJM)", "Le prix par jour à facturer pour votre revenu visé", "outil"),
    "net/": ("Net selon le chiffre d'affaires", "Tableaux de 500 € à 7 000 € par mois", "guide"),
    "brut-net-auto-entrepreneur/": ("Brut / net auto-entrepreneur", "Du chiffre d'affaires au revenu net", "guide"),
    "taux-horaire-freelance/": ("Taux horaire freelance", "Calculer son prix de l'heure", "guide"),
    "combien-facturer-freelance/": ("Combien facturer en freelance", "La méthode en 4 étapes", "guide"),
    "jours-factures-freelance/": ("Jours facturés par an", "Combien de jours facturables réellement", "guide"),
    "versement-liberatoire-micro-entreprise/": ("Versement libératoire", "Faut-il choisir cette option ?", "guide"),
}

APPS = {
    "": "Simulateur ARE ou ARCE 2026",
    "revenu-net-micro-entrepreneur/": "Simulateur de revenu net micro-entrepreneur 2026",
    "tarif-journalier-freelance/": "Calculateur de tarif journalier freelance 2026",
}


def block(name, content):
    return f"<!--seo:{name}-->{content}<!--/seo:{name}-->"


def put(html, name, content, anchor, before=True):
    """Remplace le bloc s'il existe, sinon l'insère avant/après l'ancre."""
    pat = re.compile(rf"<!--seo:{name}-->.*?<!--/seo:{name}-->", re.S)
    b = block(name, content)
    if pat.search(html):
        return pat.sub(lambda m: b, html)
    if anchor not in html:
        return html
    return html.replace(anchor, b + "\n" + anchor if before else anchor + "\n" + b, 1)


def rel(depth, slug):
    return "../" * depth + slug if slug else ("../" * depth or "./")


def crumbs(slug, title):
    """Liste (nom, slug) du fil d'Ariane pour une page."""
    items = [("Accueil", "")]
    if slug.startswith("net/") and slug != "net/":
        items.append((PAGES["net/"][0], "net/"))
    if slug:
        items.append((PAGES.get(slug, (title,))[0], slug))
    return items


def process(path):
    html = path.read_text(encoding="utf-8")
    if 'http-equiv="refresh"' in html or '<div class="wrap">' not in html:
        return False
    slug = path.parent.relative_to(ROOT).as_posix() + "/"
    slug = "" if slug == "./" else slug
    depth = slug.count("/")
    title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
    h1 = re.search(r"<h1>(.*?)</h1>", html, re.S)
    h1 = re.sub("<[^>]+>", "", h1.group(1)) if h1 else title
    h1 = h1.split(" : ")[0]  # libellé court pour le fil d'Ariane

    # 0. Pages avec CSS en ligne (accueil) : ajouter les styles de navigation
    if "assets/style.css" not in html:
        html = put(html, "css", "<style>" + CSS.replace("/*seo*/", "").replace("/*/seo*/", "") + "</style>", "</head>")

    # 1. Barre de navigation en haut de page
    nav = (f'<nav class="topnav" aria-label="Navigation principale"><a class="brand" href="{rel(depth, "")}">combien-net.fr</a>'
           f'<a href="{rel(depth, "revenu-net-micro-entrepreneur/")}">Revenu net</a>'
           f'<a href="{rel(depth, "tarif-journalier-freelance/")}">TJM</a>'
           f'<a href="{rel(depth, "net/")}">Tableaux</a>'
           f'<a href="{rel(depth, "")}">ARE / ARCE</a></nav>')
    html = put(html, "nav", nav, '<div class="wrap">', before=False)

    # 2. Fil d'Ariane visible + JSON-LD (sauf accueil)
    items = crumbs(slug, h1)
    if slug:
        vis = " › ".join(
            f'<a href="{rel(depth, s)}">{n}</a>' if i < len(items) - 1 else f'<span aria-current="page">{n if s in PAGES else h1}</span>'
            for i, (n, s) in enumerate(items))
        html = put(html, "crumbs", f'<nav class="crumbs" aria-label="Fil d\'Ariane">{vis}</nav>', "<header>")
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": (n if (s in PAGES or i < len(items) - 1) else h1), "item": BASE + s}
        for i, (n, s) in enumerate(items)]}] if slug else []

    # 3. Données structurées : site (accueil) et outils
    if not slug:
        ld.append({"@context": "https://schema.org", "@type": "WebSite", "name": "combien-net.fr", "url": BASE, "inLanguage": "fr-FR"})
    if slug in APPS:
        desc = re.search(r'<meta name="description" content="([^"]*)"', html).group(1)
        ld.append({"@context": "https://schema.org", "@type": "WebApplication", "name": APPS[slug], "url": BASE + slug,
                   "description": desc, "applicationCategory": "FinanceApplication", "operatingSystem": "Tous navigateurs",
                   "inLanguage": "fr-FR", "isAccessibleForFree": True,
                   "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}})
    if ld:
        payload = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
        html = put(html, "ld", payload, "</head>")

    # 4. Maillage : tous les outils et guides en bas de chaque page
    links = "\n".join(
        f'    <a href="{rel(depth, s)}"><strong>{n}</strong><span>{d}</span></a>'
        for s, (n, d, _) in PAGES.items() if s != slug)
    allnav = f'<section class="allnav">\n  <h2>Tous les simulateurs et guides</h2>\n  <div class="more">\n{links}\n  </div>\n</section>'
    html = put(html, "all", allnav, "<footer>")

    path.write_text(html, encoding="utf-8")
    return True


CSS = """
/*seo*/
.topnav{display:flex;flex-wrap:wrap;gap:6px 18px;align-items:center;font-size:14px;font-weight:500}
.topnav a{color:var(--muted);text-decoration:none}
.topnav a:hover{color:var(--accent)}
.topnav .brand{font-family:var(--font-display);font-weight:800;font-size:18px;color:var(--ink);margin-right:auto}
.crumbs{font-size:13px;color:var(--muted)}
.crumbs a{color:var(--muted)}
@media (min-width:640px){.allnav .more{grid-template-columns:1fr 1fr 1fr}}
/*/seo*/
"""


def main():
    css = ROOT / "assets" / "style.css"
    s = re.sub(r"\n/\*seo\*/.*?/\*/seo\*/\n", "", css.read_text(encoding="utf-8"), flags=re.S)
    css.write_text(s.rstrip("\n") + "\n" + CSS, encoding="utf-8")
    n = sum(process(p) for p in sorted(ROOT.rglob("index.html")) if ".git" not in p.parts)
    print(n, "pages traitées")


if __name__ == "__main__":
    main()
