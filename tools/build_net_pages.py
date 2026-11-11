"""Génère les pages « X € de chiffre d'affaires : combien net ? » à partir des barèmes 2026."""
import os

BASE = "https://diosako.github.io/are-ou-arce/"
ROOT = os.path.join(os.path.dirname(__file__), "..")

ACTS = {
    "activite-liberale": dict(nom="activité libérale", court="libéral (BNC)", cotis=0.256, cfp=0.002, vl=0.022, abatt=0.34, plafond=83600),
    "prestation-de-services": dict(nom="prestation de services", court="services (BIC)", cotis=0.212, cfp=0.001, vl=0.017, abatt=0.50, plafond=83600),
    "vente": dict(nom="vente de marchandises", court="vente", cotis=0.123, cfp=0.001, vl=0.010, abatt=0.71, plafond=203100),
}
MONTANTS = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000, 7000]


def eur(v):
    return f"{round(v):,}".replace(",", " ") + " €"


def pct(v):
    return f"{v * 100:.1f}".replace(".", ",").replace(",0", "") + " %"


def calc(ca, a, acre=1.0, vl=True):
    cotis = ca * a["cotis"] * acre
    cfp = ca * a["cfp"]
    impot = ca * a["vl"] if vl else 0
    return dict(cotis=cotis, cfp=cfp, impot=impot, net=ca - cotis - cfp - impot)


def slug(ca, key):
    return f"{ca}-euros-{key}"


HEAD = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}assets/style.css">
</head>
<body>
<div class="wrap">
"""

FOOT = """
<div class="cta">
  <h2>Pour gagner plus, il faut d'abord plus de clients.</h2>
  <p>Le Kit 5 Premiers Clients rassemble les messages de prospection et le tableau de suivi pour décrocher vos premières missions en freelance.</p>
  <a class="btn" href="https://bouzidi837.gumroad.com/l/kit-premiers-clients" target="_blank" rel="noopener">Voir le kit</a>
</div>

<footer>
  <span>Sources : <a href="https://www.autoentrepreneur.urssaf.fr/" target="_blank" rel="noopener">Urssaf auto-entrepreneur</a>, <a href="https://entreprendre.service-public.gouv.fr/" target="_blank" rel="noopener">Service-Public Entreprendre</a>. Barèmes en vigueur en novembre 2026.</span>
  <span>Estimation indicative, qui ne remplace pas un conseil personnalisé.</span>
</footer>
</div>
</body>
</html>
"""


def page(ca, key):
    a = ACTS[key]
    r = calc(ca, a)
    r_sans_vl = calc(ca, a, vl=False)
    r_acre = calc(ca, a, acre=0.75)
    taux = (r["cotis"] + r["cfp"] + r["impot"]) / ca
    an = ca * 12
    title = f"{eur(ca)} de chiffre d'affaires en {a['nom']} : combien net en 2026 ?"
    desc = (f"Micro-entrepreneur en {a['nom']} : sur {eur(ca)} de chiffre d'affaires par mois, il reste environ "
            f"{eur(r['net'])} après cotisations, formation et versement libératoire (barèmes 2026).")
    h = HEAD.format(title=title, desc=desc, canon=f"{BASE}net/{slug(ca, key)}/", rel="../../")
    h += f"""
<header>
  <span class="tag">Micro-entreprise · barèmes 2026</span>
  <h1>{eur(ca)} de chiffre d'affaires en {a['nom']} : combien vous reste-t-il ?</h1>
  <p class="lead">Avec {eur(ca)} encaissés dans le mois, un micro-entrepreneur en {a['nom']} garde environ <strong>{eur(r['net'])}</strong> après cotisations sociales, formation professionnelle et versement libératoire de l'impôt.</p>
</header>

<section>
  <h2>Le détail du calcul</h2>
  <div class="rows">
    <div class="row"><span>Chiffre d'affaires du mois</span><span>{eur(ca)}</span></div>
    <div class="row"><span>Cotisations sociales ({pct(a['cotis'])})</span><span>− {eur(r['cotis'])}</span></div>
    <div class="row"><span>Formation professionnelle ({pct(a['cfp'])})</span><span>− {eur(r['cfp'])}</span></div>
    <div class="row"><span>Versement libératoire de l'impôt ({pct(a['vl'])})</span><span>− {eur(r['impot'])}</span></div>
    <div class="row total"><span>Reste pour vous</span><span>{eur(r['net'])}</span></div>
  </div>
  <p>Au total, {pct(taux)} du chiffre d'affaires part en prélèvements. Sur une année complète à ce rythme, cela représente {eur(an)} de chiffre d'affaires et {eur(r['net'] * 12)} de revenu net, avant vos frais professionnels.</p>
</section>

<section>
  <h2>Selon votre situation</h2>
  <div class="rows">
    <div class="row"><span>Avec versement libératoire, sans ACRE</span><span>{eur(r['net'])}</span></div>
    <div class="row"><span>Première année avec l'ACRE (création depuis juillet 2026)</span><span>{eur(r_acre['net'])}</span></div>
    <div class="row"><span>Sans versement libératoire, avant impôt sur le revenu</span><span>{eur(r_sans_vl['net'])}</span></div>
  </div>
  <p>Sans versement libératoire, l'impôt est calculé plus tard sur {pct(1 - a['abatt'])} de votre chiffre d'affaires, soit {eur(ca * (1 - a['abatt']))} de revenu imposable pour ce mois. {plafond_txt(an, a)}</p>
  <p><a href="../../revenu-net-micro-entrepreneur/">Refaire le calcul avec vos propres chiffres dans le simulateur</a>.</p>
</section>

<section>
  <h2>Et avec un autre chiffre d'affaires ?</h2>
  <div class="rows">
{autres(ca, key)}
  </div>
</section>

<section>
  <h2>Autres simulateurs</h2>
  <div class="more">
    <a href="../../tarif-journalier-freelance/"><strong>Tarif journalier freelance</strong><span>Le prix par jour à facturer pour atteindre le revenu que vous visez.</span></a>
    <a href="../../"><strong>ARE ou ARCE</strong><span>Capital ou maintien mensuel de vos allocations chômage.</span></a>
  </div>
</section>
"""
    return h + FOOT


def plafond_txt(an, a):
    if an > a["plafond"]:
        return f"Attention : {eur(an)} par an dépasse le plafond de la micro-entreprise pour cette activité ({eur(a['plafond'])})."
    return f"Ce niveau d'activité ({eur(an)} par an) reste sous le plafond de la micro-entreprise ({eur(a['plafond'])})."


def autres(ca, key):
    a = ACTS[key]
    out = []
    for m in MONTANTS:
        if m == ca:
            continue
        out.append(f'    <div class="row"><a href="../{slug(m, key)}/">{eur(m)} en {a["nom"]}</a><span>{eur(calc(m, a)["net"])} net</span></div>')
    return "\n".join(out)


def hub():
    title = "Micro-entrepreneur : combien net selon votre chiffre d'affaires (2026)"
    desc = "Tableaux 2026 du revenu net d'un micro-entrepreneur selon le chiffre d'affaires mensuel, en activité libérale, prestation de services et vente."
    h = HEAD.format(title=title, desc=desc, canon=f"{BASE}net/", rel="../")
    h += """
<header>
  <span class="tag">Micro-entreprise · barèmes 2026</span>
  <h1>Combien reste-t-il net selon votre chiffre d'affaires ?</h1>
  <p class="lead">Revenu net mensuel d'un micro-entrepreneur après cotisations sociales, formation professionnelle et versement libératoire, pour chaque type d'activité.</p>
</header>
"""
    for key, a in ACTS.items():
        rows = "\n".join(
            f'    <div class="row"><a href="{slug(m, key)}/">{eur(m)} de chiffre d\'affaires</a><span>{eur(calc(m, a)["net"])} net</span></div>'
            for m in MONTANTS)
        h += f"""
<section>
  <h2>En {a['nom']}</h2>
  <div class="rows">
{rows}
  </div>
</section>
"""
    h += """
<section>
  <h2>Simulateurs</h2>
  <div class="more">
    <a href="../revenu-net-micro-entrepreneur/"><strong>Revenu net micro-entrepreneur</strong><span>Le calcul avec vos propres chiffres, ACRE et frais compris.</span></a>
    <a href="../tarif-journalier-freelance/"><strong>Tarif journalier freelance</strong><span>Le prix par jour à facturer pour atteindre le revenu que vous visez.</span></a>
  </div>
</section>
"""
    return h + FOOT


def main():
    urls = ["", "revenu-net-micro-entrepreneur/", "tarif-journalier-freelance/", "net/"]
    os.makedirs(os.path.join(ROOT, "net"), exist_ok=True)
    with open(os.path.join(ROOT, "net", "index.html"), "w", encoding="utf-8") as f:
        f.write(hub())
    for key in ACTS:
        for ca in MONTANTS:
            d = os.path.join(ROOT, "net", slug(ca, key))
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
                f.write(page(ca, key))
            urls.append(f"net/{slug(ca, key)}/")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{BASE}{u}</loc><lastmod>2026-11-10</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm) + "\n")
    print(len(urls), "URL dans le sitemap")


if __name__ == "__main__":
    main()
