"""Génère les pages « X € de chiffre d'affaires : combien net ? » à partir des barèmes 2026."""
import os

BASE = "https://combien-net.fr/"
ROOT = os.path.join(os.path.dirname(__file__), "..")

ACTS = {
    "activite-liberale": dict(nom="activité libérale", art="à l'activité libérale", court="libéral (BNC)", cotis=0.256, cfp=0.002, vl=0.022, abatt=0.34, plafond=83600,
                              tva=37500, tva_maj=41250, impot_cat="BNC (bénéfices non commerciaux)"),
    "prestation-de-services": dict(nom="prestation de services", art="à la prestation de services", court="services (BIC)", cotis=0.212, cfp=0.001, vl=0.017, abatt=0.50, plafond=83600,
                                   tva=37500, tva_maj=41250, impot_cat="BIC (bénéfices industriels et commerciaux)"),
    "vente": dict(nom="vente de marchandises", art="à la vente de marchandises", court="vente", cotis=0.123, cfp=0.001, vl=0.010, abatt=0.71, plafond=203100,
                  tva=85000, tva_maj=93500, impot_cat="BIC (bénéfices industriels et commerciaux)"),
}

# Texte propre à chaque activité, pour que les pages d'un même montant ne se ressemblent pas.
PROFILS = {
    "activite-liberale": dict(
        qui="Ce barème concerne les professions libérales non réglementées affiliées à la Sécurité sociale des indépendants : consultants, formateurs, coachs, développeurs, graphistes, rédacteurs, traducteurs, community managers.",
        specif="C'est l'activité la plus taxée en micro-entreprise. Les cotisations sociales prennent 25,6 % du chiffre d'affaires et l'abattement fiscal n'est que de 34 %, car l'administration considère que vous avez peu de frais. Les professions réglementées qui cotisent à la CIPAV (architectes, psychologues, ostéopathes…) ont un taux de cotisation un peu différent.",
        conseil="Comme vous n'achetez presque rien pour travailler, votre marge réelle est proche du net affiché ici. Le levier principal reste votre tarif : comparez avec le <a href=\"../../tarif-journalier-freelance/\">calculateur de tarif journalier</a>.",
    ),
    "prestation-de-services": dict(
        qui="Ce barème concerne les prestations commerciales et artisanales : plombiers, électriciens, coiffeurs, chauffeurs VTC, livreurs, réparateurs, agents de nettoyage, déménageurs.",
        specif="Les cotisations sociales prennent 21,2 % du chiffre d'affaires et l'abattement fiscal est de 50 %, plus favorable qu'en libéral. La contribution à la formation professionnelle affichée ici (0,1 %) est celle des commerçants ; un artisan inscrit au répertoire des métiers paie 0,3 %, soit quelques euros de plus par mois.",
        conseil="Ces métiers ont souvent des frais réels (véhicule, carburant, outillage, produits) qui ne sont pas déductibles en micro-entreprise. Retirez-les du net affiché pour connaître ce qui vous reste vraiment.",
    ),
    "vente": dict(
        qui="Ce barème concerne l'achat-revente de marchandises : e-commerce, dropshipping, vente sur les marchés, revente sur Vinted ou Leboncoin à titre professionnel, ainsi que la vente à emporter.",
        specif="Les cotisations sont les plus basses de la micro-entreprise (12,3 %) parce que le chiffre d'affaires inclut le prix d'achat des marchandises. L'abattement fiscal monte à 71 % pour la même raison.",
        conseil="Attention, le « net » de cette page est calculé sur le chiffre d'affaires et ne retire pas le coût de vos marchandises. Si vous achetez un produit 60 € pour le revendre 100 €, votre vraie marge est bien plus faible que le résultat affiché.",
    ),
}
LASTMOD = "2026-11-26"
MONTANTS = [500, 1000, 1500, 2000, 3000, 4000, 5000, 7000]
# Montants retirés le 26/11/2026 (pages trop proches de leurs voisines) -> redirigés vers le montant le plus proche
RETIRES = {2500: 2000, 3500: 3000, 6000: 5000}


def palier(ca, a, r):
    an = ca * 12
    if ca <= 500:
        return (f"À ce niveau, la micro-entreprise sert souvent d'activité d'appoint, à côté d'un salaire, d'études ou des allocations chômage. "
                f"Si vous touchez l'ARE, ces {eur(r['net'])} ne s'ajoutent pas simplement à vos allocations : France Travail réduit vos allocations en fonction du chiffre d'affaires que vous déclarez. "
                f"Le <a href=\"../../\">simulateur ARE ou ARCE</a> vous aide à choisir la formule la plus intéressante.")
    if ca <= 1500:
        return (f"Avec {eur(r['net'])} par mois, vous êtes dans la zone où l'activité commence à remplacer un revenu, sans encore permettre de vivre confortablement seul. "
                f"C'est aussi le niveau où l'ACRE pèse le plus dans le budget : profitez de la première année pour augmenter vos tarifs ou votre nombre de clients.")
    if ca <= 3000:
        return (f"{eur(r['net'])} net par mois correspond à une activité principale. Pensez à mettre de côté de quoi couvrir vos congés et les mois creux : "
                f"un indépendant ne touche rien quand il ne facture pas, et votre retraite se calcule uniquement sur les cotisations versées.")
    return (f"À {eur(an)} de chiffre d'affaires par an, la question du statut se pose. Au-delà d'un certain niveau de frais réels, une EURL ou une SASU peut devenir plus intéressante que la micro-entreprise, "
            f"parce que les charges y sont déductibles. Faites le point avec un expert-comptable, surtout si vous approchez du plafond du régime.")



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

{specifique(ca, key, r, r_acre, r_sans_vl)}

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


def tva_txt(an, a):
    if an <= a["tva"]:
        return (f"Sur un an, {eur(an)} de chiffre d'affaires reste sous le seuil de franchise en base de TVA de {eur(a['tva'])} pour cette activité. "
                f"Vous facturez donc sans TVA, avec la mention « TVA non applicable, art. 293 B du CGI », et le calcul ci-dessus s'applique tel quel. "
                f"Il vous reste {eur(a['tva'] - an)} de marge annuelle avant d'atteindre ce seuil.")
    if an <= a["tva_maj"]:
        return (f"Sur un an, {eur(an)} dépasse le seuil de franchise de TVA ({eur(a['tva'])}) sans atteindre le seuil majoré ({eur(a['tva_maj'])}). "
                f"Vous gardez la franchise cette année, mais vous devrez facturer la TVA à partir du 1er janvier suivant. "
                f"Pour ne pas perdre de revenu, il faudra alors augmenter vos prix de 20 % ou accepter que la TVA soit prise sur votre marge.")
    return (f"Sur un an, {eur(an)} dépasse le seuil majoré de franchise de TVA ({eur(a['tva_maj'])}). "
            f"Vous devenez redevable de la TVA dès le mois où ce seuil est franchi : vos factures doivent alors inclure 20 % de TVA, à reverser à l'État. "
            f"Les montants nets de cette page sont calculés sur un chiffre d'affaires hors taxes : si vos clients sont des particuliers et que vos prix TTC ne bougent pas, votre chiffre d'affaires HT baisse d'un sixième.")


def specifique(ca, key, r, r_acre, r_sans_vl):
    a, prof = ACTS[key], PROFILS[key]
    an = ca * 12
    gain_acre = r_acre["net"] - r["net"]
    trimestre = (r["cotis"] + r["cfp"]) * 3
    part_plafond = an / a["plafond"]
    autres_act = "\n".join(
        f'    <div class="row"><a href="../{slug(ca, k)}/">{eur(ca)} en {b["nom"]}</a><span>{eur(calc(ca, b)["net"])} net</span></div>'
        for k, b in ACTS.items() if k != key)
    faq = [
        (f"Combien de cotisations payer chaque trimestre avec {eur(ca)} de chiffre d'affaires mensuel en {a['nom']} ?",
         f"Si vous déclarez tous les trimestres, vous réglez environ {eur(trimestre)} de cotisations sociales et de formation à l'Urssaf, plus {eur(r['impot'] * 3)} de versement libératoire si vous l'avez choisi."),
        (f"Combien l'ACRE fait-elle gagner à {eur(ca)} par mois ?",
         f"Avec l'ACRE, les cotisations sociales baissent de 25 % la première année : le net passe de {eur(r['net'])} à {eur(r_acre['net'])}, soit {eur(gain_acre)} de plus par mois et {eur(gain_acre * 12)} sur l'année."),
        (f"Faut-il facturer la TVA avec {eur(an)} de chiffre d'affaires annuel en {a['nom']} ?",
         "Non, vous restez en franchise en base de TVA." if an <= a["tva"] else
         ("Pas la première année : vous dépassez le seuil de base mais pas le seuil majoré, la TVA s'applique au 1er janvier suivant." if an <= a["tva_maj"] else
          "Oui : vous dépassez le seuil majoré, la TVA s'applique dès le mois du dépassement.")),
    ]
    import json
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": rep}} for q, rep in faq]}, ensure_ascii=False)
    faq_html = "\n".join(f"  <details><summary>{q}</summary><p>{rep}</p></details>" for q, rep in faq)
    return f"""<section>
  <h2>Ce qui est propre {a['art']}</h2>
  <p>{prof['qui']}</p>
  <p>{prof['specif']} Sans versement libératoire, votre bénéfice est imposé dans la catégorie {a['impot_cat']}.</p>
  <p>{prof['conseil']}</p>
</section>

<section>
  <h2>Que représente {eur(ca)} de chiffre d'affaires par mois ?</h2>
  <p>{palier(ca, a, r)}</p>
</section>

<section>
  <h2>À {eur(ca)} par mois : TVA et plafond de la micro-entreprise</h2>
  <p>{tva_txt(an, a)}</p>
  <p>Côté régime, {eur(an)} par an représente {pct(part_plafond)} du plafond de la micro-entreprise pour cette activité ({eur(a['plafond'])}). {"Vous avez de la marge pour développer votre activité sans changer de statut." if part_plafond < 0.6 else ("Vous approchez du plafond : au-delà de deux années de dépassement, vous basculez au régime réel." if part_plafond <= 1 else "Au-delà de deux années consécutives de dépassement, vous sortez du régime micro et passez au régime réel.")}</p>
</section>

<section>
  <h2>Le même montant dans les autres activités</h2>
  <div class="rows">
{autres_act}
  </div>
</section>

<section class="faq">
  <h2>Questions fréquentes</h2>
{faq_html}
</section>
<script type="application/ld+json">{ld}</script>"""


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
    for key in ACTS:
        for old, new in RETIRES.items():
            d = os.path.join(ROOT, "net", slug(old, key))
            os.makedirs(d, exist_ok=True)
            cible = f"{BASE}net/{slug(new, key)}/"
            with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
                f.write(f'<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>Page déplacée</title>'
                        f'<link rel="canonical" href="{cible}"><meta name="robots" content="noindex">'
                        f'<meta http-equiv="refresh" content="0; url={cible}"></head>'
                        f'<body><p>Cette page a été déplacée : <a href="{cible}">{cible}</a></p></body></html>\n')
    import re
    smp = os.path.join(ROOT, "sitemap.xml")
    sm = open(smp, encoding="utf-8").read()
    for key in ACTS:
        for old in RETIRES:
            sm = re.sub(r"\s*<url><loc>" + re.escape(f"{BASE}net/{slug(old, key)}/") + r"</loc>.*?</url>", "", sm)
    sm = re.sub(r"(<loc>" + re.escape(BASE) + r"net/[^<]*</loc><lastmod>)[^<]*", r"\g<1>" + LASTMOD, sm)
    with open(smp, "w", encoding="utf-8") as f:
        f.write(sm)
    print(len(urls) - 4, "pages /net/ générées (hors hub)")


if __name__ == "__main__":
    main()
