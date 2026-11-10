/* Barèmes micro-entrepreneur 2026 partagés par les simulateurs */
var MICRO = {
  activites: {
    vente:   {label: "Vente de marchandises",                 cotis: 0.123, cfp: 0.001, vl: 0.010, abatt: 0.71, plafond: 203100},
    bicCom:  {label: "Prestations de services commerciales (BIC)", cotis: 0.212, cfp: 0.001, vl: 0.017, abatt: 0.50, plafond: 83600},
    bicArt:  {label: "Prestations de services artisanales (BIC)",  cotis: 0.212, cfp: 0.003, vl: 0.017, abatt: 0.50, plafond: 83600},
    bnc:     {label: "Activité libérale (BNC)",                cotis: 0.256, cfp: 0.002, vl: 0.022, abatt: 0.34, plafond: 83600},
    cipav:   {label: "Profession libérale Cipav",              cotis: 0.232, cfp: 0.002, vl: 0.022, abatt: 0.34, plafond: 83600}
  },
  acre: {aucune: 1, avant: 0.5, apres: 0.75}
};

/* Taux global prélevé sur le chiffre d'affaires */
function tauxGlobal(p) {
  var a = MICRO.activites[p.act];
  var cotis = a.cotis * MICRO.acre[p.acre];
  var impot = p.vl ? a.vl : (1 - a.abatt) * p.tmi;
  return {cotis: cotis, cfp: a.cfp, impot: impot, total: cotis + a.cfp + impot};
}

/* Revenu net à partir d'un chiffre d'affaires mensuel */
function revenuNet(p) {
  var a = MICRO.activites[p.act], t = tauxGlobal(p);
  var cotis = p.ca * t.cotis, cfp = p.ca * t.cfp, impot = p.ca * t.impot;
  var net = p.ca - cotis - cfp - impot - p.frais;
  return {cotis: cotis, cfp: cfp, impot: impot, net: net, taux: t.total,
          caAnnuel: p.ca * 12, plafond: a.plafond, depasse: p.ca * 12 > a.plafond};
}

/* Tarif journalier nécessaire pour atteindre un revenu net mensuel */
function tarifJour(p) {
  var a = MICRO.activites[p.act], t = tauxGlobal(p);
  var caAnnuel = (p.net + p.frais) * 12 / (1 - t.total);
  var jours = p.joursSemaine * (52 - p.semainesOff);
  var tjm = jours > 0 ? caAnnuel / jours : 0;
  return {caAnnuel: caAnnuel, caMensuel: caAnnuel / 12, jours: jours, tjm: tjm,
          horaire: tjm / 7, taux: t.total, plafond: a.plafond, depasse: caAnnuel > a.plafond};
}

if (typeof module !== "undefined") module.exports = {MICRO: MICRO, tauxGlobal: tauxGlobal, revenuNet: revenuNet, tarifJour: tarifJour};
