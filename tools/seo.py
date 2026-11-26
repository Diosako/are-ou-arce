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


MAJ = "2026-11-26"
MAJ_TXT = "26 novembre 2026"

# Réponse courte placée juste sous le titre : format visé par l'encadré « position zéro » de Google et par les réponses IA.
ANSWERS = {
    "": ("ARE ou ARCE : laquelle choisir ?",
         "<p><strong>L'ARCE</strong> vous verse en capital 60 % de vos droits au chômage restants (moins 3 % de participation aux retraites complémentaires), en deux fois : à la création puis six mois plus tard. "
         "<strong>Le maintien de l'ARE</strong> continue de vous verser votre allocation chaque mois, réduite de 70 % de votre revenu (chiffre d'affaires après abattement). "
         "L'ARCE convient si vous avez besoin d'argent pour lancer l'activité ou si vous visez vite un bon chiffre d'affaires ; le maintien de l'ARE protège mieux si vos revenus démarrent lentement.</p>"),
    "revenu-net-micro-entrepreneur/": ("Combien reste-t-il net à un micro-entrepreneur en 2026 ?",
         "<p>Après cotisations sociales, formation professionnelle et versement libératoire, un micro-entrepreneur garde environ <strong>72 % de son chiffre d'affaires en activité libérale</strong>, <strong>77 % en prestation de services</strong> et <strong>87 % en vente de marchandises</strong>, avant ses frais professionnels.</p>"
         "<table class=\"answer-table\"><thead><tr><th>Activité</th><th>Prélèvements</th><th>Net pour 1 000 € encaissés</th></tr></thead><tbody>"
         "<tr><td>Libéral (BNC)</td><td>28 %</td><td>720 €</td></tr><tr><td>Services (BIC)</td><td>23 %</td><td>770 €</td></tr><tr><td>Vente</td><td>13,4 %</td><td>866 €</td></tr></tbody></table>"),
    "tarif-journalier-freelance/": ("Comment calculer son tarif journalier (TJM) en freelance ?",
         "<p><strong>TJM = (revenu net mensuel visé + frais mensuels) × 12 ÷ (1 − taux de prélèvement) ÷ nombre de jours facturés par an.</strong> "
         "Exemple : pour toucher 2 000 € net par mois en prestation de services (23 % de prélèvements avec versement libératoire) sur 180 jours facturés, il faut 31 169 € de chiffre d'affaires, soit <strong>environ 173 € par jour</strong>.</p>"),
    "taux-horaire-freelance/": ("Comment calculer son taux horaire en freelance ?",
         "<p>Calculez d'abord votre tarif journalier, puis divisez-le par le nombre d'heures facturées dans une journée (souvent 7). "
         "Exemple : 2 000 € net visés par mois en prestation de services, 180 jours facturés par an, donnent un TJM d'environ 173 €, soit <strong>un taux horaire d'environ 25 €</strong>.</p>"),
    "combien-facturer-freelance/": ("Combien facturer en freelance ?",
         "<ol><li>Fixez le revenu net mensuel que vous voulez toucher, frais compris.</li>"
         "<li>Comptez vos jours réellement facturés par an (135 à 180 pour 3 à 4 jours par semaine).</li>"
         "<li>Calculez votre prix plancher en ajoutant cotisations et impôt (23 % à 28 % du chiffre d'affaires selon l'activité).</li>"
         "<li>Comparez avec les tarifs de votre marché et ajustez vers le haut si possible.</li></ol>"),
    "jours-factures-freelance/": ("Combien de jours facture un freelance par an ?",
         "<p>Un freelance qui facture <strong>4 jours par semaine</strong> et s'arrête 7 semaines dans l'année (congés, jours fériés, creux) facture <strong>180 jours par an</strong>. "
         "À 3 jours facturés par semaine, on tombe à 135 jours. Le reste du temps part en prospection, devis, administratif et formation.</p>"),
    "brut-net-auto-entrepreneur/": ("Comment passer du brut au net en auto-entrepreneur ?",
         "<p>En micro-entreprise, le « brut » est votre chiffre d'affaires encaissé. Retirez-en les cotisations sociales (12,3 % en vente, 21,2 % en services, 25,6 % en libéral) et la formation professionnelle (0,1 % à 0,3 %). "
         "Pour 2 000 € encaissés, il reste avant impôt <strong>1 752 € en vente</strong>, <strong>1 574 € en services</strong> et <strong>1 484 € en libéral</strong>.</p>"),
    "versement-liberatoire-micro-entreprise/": ("Le versement libératoire est-il intéressant ?",
         "<p>En général, <strong>oui si votre foyer est imposable</strong> (tranche à 11 % ou plus) : le versement libératoire coûte 1 % du chiffre d'affaires en vente, 1,7 % en services et 2,2 % en libéral, moins que l'impôt au barème dans la plupart des cas. "
         "<strong>Non si vous êtes non imposable</strong> : vous paieriez un impôt que vous ne devriez pas. L'option est réservée aux foyers sous un plafond de revenu fiscal de référence.</p>"),
    "net/": ("Combien reste-t-il net selon le chiffre d'affaires ?",
         "<p>Pour <strong>1 000 € de chiffre d'affaires mensuel</strong>, un micro-entrepreneur garde environ <strong>720 € en activité libérale</strong>, <strong>770 € en prestation de services</strong> et <strong>866 € en vente de marchandises</strong>, après cotisations, formation et versement libératoire (barèmes 2026). Les tableaux ci-dessous donnent le résultat de 500 € à 7 000 € par mois.</p>"),
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

    # 3 bis. Date de mise à jour visible et dans les données structurées
    desc = re.search(r'<meta name="description" content="([^"]*)"', html)
    ld.append({"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": BASE + slug, "inLanguage": "fr-FR",
               "description": desc.group(1) if desc else "", "dateModified": MAJ,
               "publisher": {"@type": "Organization", "name": "combien-net.fr", "url": BASE}})
    payload = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    html = put(html, "ld", payload, "</head>")
    html = put(html, "maj", f'<p class="maj">Mis à jour le <time datetime="{MAJ}">{MAJ_TXT}</time> · barèmes Urssaf 2026</p>', "</header>")

    # 3 ter. Réponse courte sous le titre
    if slug in ANSWERS:
        q, a = ANSWERS[slug]
        bloc = f'<section class="answer" aria-label="Réponse courte">\n  <h2>{q}</h2>\n  {a}\n</section>'
        if slug in APPS:  # sur les simulateurs, l'outil reste en haut : la réponse vient juste après
            html = re.sub(r"<!--seo:answer-->.*?<!--/seo:answer-->\n?", "", html, flags=re.S)
            html = html.replace("\n<section>", "\n" + block("answer", bloc) + "\n<section>", 1)
        else:
            html = put(html, "answer", bloc, "</header>", before=False)

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
.maj{font-size:13px;color:var(--muted)}
.answer{background:var(--surface);border:1px solid var(--line);border-left:5px solid var(--accent);border-radius:14px;padding:18px 20px;gap:10px}
.answer h2{font-size:19px}
.answer ol{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:6px;max-width:65ch}
.answer-table{border-collapse:collapse;font-size:15px;font-variant-numeric:tabular-nums}
.answer-table th,.answer-table td{text-align:left;padding:6px 14px 6px 0;border-bottom:1px solid var(--line)}
.answer-table th{font-weight:600;color:var(--muted);font-size:13px}
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
