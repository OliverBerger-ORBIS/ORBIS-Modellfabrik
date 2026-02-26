#!/usr/bin/env node
/**
 * Add missing i18n translations to messages.de.json and messages.fr.json.
 * Reads missing_keys.txt (key|defaultEn format) and merges into both locale files.
 * Uses translation map for DE/FR where available, else derives from English.
 */
import { readFileSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const localeDir = join(__dirname, '../osf/apps/osf-ui/src/locale');

// Common term mappings EN -> {de, fr}
const TERMS = {
  Loading: { de: 'Laden', fr: 'Chargement' },
  Available: { de: 'Verfügbar', fr: 'Disponible' },
  Availability: { de: 'Verfügbarkeit', fr: 'Disponibilité' },
  Connected: { de: 'Verbunden', fr: 'Connecté' },
  Disconnected: { de: 'Getrennt', fr: 'Déconnecté' },
  Configuration: { de: 'Konfiguration', fr: 'Configuration' },
  Status: { de: 'Status', fr: 'Statut' },
  Command: { de: 'Befehl', fr: 'Commande' },
  Connection: { de: 'Verbindung', fr: 'Connexion' },
  Failed: { de: 'Fehlgeschlagen', fr: 'Échoué' },
  Passed: { de: 'Bestanden', fr: 'Réussi' },
  Unknown: { de: 'Unbekannt', fr: 'Inconnu' },
  Empty: { de: 'Leer', fr: 'Vide' },
  None: { de: 'Keine', fr: 'Aucun' },
  Active: { de: 'Aktiv', fr: 'Actif' },
  Online: { de: 'Online', fr: 'En ligne' },
  Offline: { de: 'Offline', fr: 'Hors ligne' },
  Ready: { de: 'Bereit', fr: 'Prêt' },
  Busy: { de: 'Beschäftigt', fr: 'Occupé' },
  Error: { de: 'Fehler', fr: 'Erreur' },
  Yes: { de: 'Ja', fr: 'Oui' },
  No: { de: 'Nein', fr: 'Non' },
  Close: { de: 'Schließen', fr: 'Fermer' },
  Start: { de: 'Start', fr: 'Démarrer' },
  Stop: { de: 'Stopp', fr: 'Arrêter' },
  Order: { de: 'Auftrag', fr: 'Commande' },
  Blue: { de: 'Blau', fr: 'Bleu' },
  White: { de: 'Weiß', fr: 'Blanc' },
  Red: { de: 'Rot', fr: 'Rouge' },
  Production: { de: 'Produktion', fr: 'Production' },
  Storage: { de: 'Lager', fr: 'Stockage' },
  Environment: { de: 'Umgebung', fr: 'Environnement' },
  Language: { de: 'Sprache', fr: 'Langue' },
  Role: { de: 'Rolle', fr: 'Rôle' },
  Filter: { de: 'Filter', fr: 'Filtre' },
  Valid: { de: 'Gültig', fr: 'Valide' },
  Invalid: { de: 'Ungültig', fr: 'Invalide' },
  Topic: { de: 'Topic', fr: 'Sujet' },
  Payload: { de: 'Payload', fr: 'Données' },
  Name: { de: 'Name', fr: 'Nom' },
  Duration: { de: 'Dauer', fr: 'Durée' },
  Result: { de: 'Ergebnis', fr: 'Résultat' },
  State: { de: 'Zustand', fr: 'État' },
  Timestamp: { de: 'Zeitstempel', fr: 'Horodatage' },
  SerialNumber: { de: 'Seriennummer', fr: 'Numéro de série' },
  Current: { de: 'Aktuell', fr: 'Actuel' },
  Previous: { de: 'Vorherig', fr: 'Précédent' },
  Temperature: { de: 'Temperatur', fr: 'Température' },
  Humidity: { de: 'Luftfeuchtigkeit', fr: 'Humidité' },
  Pressure: { de: 'Luftdruck', fr: 'Pression' },
  Center: { de: 'Zentrieren', fr: 'Centrer' },
  Left: { de: 'Links', fr: 'Gauche' },
  Right: { de: 'Rechts', fr: 'Droite' },
  Up: { de: 'Hoch', fr: 'Haut' },
  Down: { de: 'Runter', fr: 'Bas' },
};

function translate(en, locale) {
  if (locale === 'de' && en in TERMS) return TERMS[en].de;
  if (locale === 'fr' && en in TERMS) return TERMS[en].fr;
  const lower = en.toLowerCase();
  for (const [key, val] of Object.entries(TERMS)) {
    if (lower === key.toLowerCase()) return val[locale];
    if (en.startsWith(key)) {
      const rest = en.slice(key.length);
      return val[locale] + rest;
    }
  }
  return en; // fallback to English
}

function translatePhrase(en, locale) {
  const placeholders = en.match(/\{\$[A-Z_]+\}|{\$PH}/g) || [];
  let t = en;
  for (const [eng, def] of Object.entries(TERMS)) {
    const re = new RegExp(`\\b${eng}\\b`, 'gi');
    t = t.replace(re, (m) => (m[0] === m[0].toUpperCase() ? def[locale][0].toUpperCase() + def[locale].slice(1) : def[locale]));
  }
  if (locale === 'de') {
    t = t.replace(/\bLoading\b/g, 'Laden').replace(/\bConnecting\b/g, 'Verbindung wird aufgebaut')
      .replace(/\bDisconnected\b/g, 'Getrennt').replace(/\bConnected\b/g, 'Verbunden')
      .replace(/\bConnection error\b/g, 'Verbindungsfehler').replace(/\bReset factory\b/g, 'Fabrik zurücksetzen')
      .replace(/\bMain navigation\b/g, 'Hauptnavigation').replace(/\bMock environment\b/g, 'Mock-Umgebung')
      .replace(/\bLive environment\b/g, 'Live-Umgebung').replace(/\bReplay environment\b/g, 'Replay-Umgebung')
      .replace(/\bIntersection 1\b/g, 'Kreuzung 1').replace(/\bIntersection 2\b/g, 'Kreuzung 2')
      .replace(/\bIntersection 3\b/g, 'Kreuzung 3').replace(/\bIntersection 4\b/g, 'Kreuzung 4')
      .replace(/\bZoom in\b/g, 'Vergrößern').replace(/\bZoom out\b/g, 'Verkleinern')
      .replace(/\bReset zoom\b/g, 'Zoom zurücksetzen').replace(/\bLoading SVG\.\.\.\b/g, 'Lade SVG…')
      .replace(/\bFailed to load SVG\.\b/g, 'SVG konnte nicht geladen werden.')
      .replace(/\bDrilling Station \(DRILL\)\b/g, 'Bohrstation (DRILL)')
      .replace(/\bMilling Station \(MILL\)\b/g, 'Frässtation (MILL)')
      .replace(/\bDelivery & Pickup Station \(DPS\)\b/g, 'Warenein- und ausgang (DPS)')
      .replace(/\bAI Quality System \(AIQS\)\b/g, 'KI-Qualitätsstation (AIQS)')
      .replace(/\bHigh-Bay Warehouse \(HBW\)\b/g, 'Hochregallager (HBW)')
      .replace(/\bCharging Station\b/g, 'Ladestation')
      .replace(/\bAutomated Guided Vehicle\b/g, 'Fahrerloses Transportsystem')
      .replace(/\bHigh Bay Warehouse\b/g, 'Hochregallager')
      .replace(/\bDelivery and Pickup Station\b/g, 'Warenein- und ausgang')
      .replace(/\bAI Quality Station\b/g, 'KI-Qualitätsstation')
      .replace(/\bDrilling Station\b/g, 'Bohrstation').replace(/\bMilling Station\b/g, 'Frässtation')
      .replace(/\bOrders\b/g, 'Aufträge').replace(/\bModules\b/g, 'Module').replace(/\bProcesses\b/g, 'Prozesse')
      .replace(/\bEnvironment Data\b/g, 'Umgebungsdaten').replace(/\bSettings\b/g, 'Einstellungen')
      .replace(/\bConfiguration\b/g, 'Konfiguration').replace(/\bMessage Monitor\b/g, 'Nachrichten-Monitor')
      .replace(/\bShopfloor\b/g, 'Shopfloor').replace(/\bDSP\b/g, 'DSP').replace(/\bAGV\b/g, 'AGV');
  }
  if (locale === 'fr') {
    t = t.replace(/\bLoading\b/g, 'Chargement').replace(/\bConnecting\b/g, 'Connexion en cours')
      .replace(/\bDisconnected\b/g, 'Déconnecté').replace(/\bConnected\b/g, 'Connecté')
      .replace(/\bConnection error\b/g, 'Erreur de connexion').replace(/\bReset factory\b/g, 'Réinitialiser l\'usine')
      .replace(/\bMain navigation\b/g, 'Navigation principale').replace(/\bMock environment\b/g, 'Environnement fictif')
      .replace(/\bLive environment\b/g, 'Environnement live').replace(/\bReplay environment\b/g, 'Environnement replay')
      .replace(/\bIntersection 1\b/g, 'Intersection 1').replace(/\bIntersection 2\b/g, 'Intersection 2')
      .replace(/\bIntersection 3\b/g, 'Intersection 3').replace(/\bIntersection 4\b/g, 'Intersection 4')
      .replace(/\bZoom in\b/g, 'Zoom avant').replace(/\bZoom out\b/g, 'Zoom arrière')
      .replace(/\bReset zoom\b/g, 'Réinitialiser le zoom').replace(/\bLoading SVG\.\.\.\b/g, 'Chargement SVG…')
      .replace(/\bFailed to load SVG\.\b/g, 'Échec du chargement SVG.')
      .replace(/\bDrilling Station \(DRILL\)\b/g, 'Station de perçage (DRILL)')
      .replace(/\bMilling Station \(MILL\)\b/g, 'Station de fraisage (MILL)')
      .replace(/\bDelivery & Pickup Station \(DPS\)\b/g, 'Station livraison et collecte (DPS)')
      .replace(/\bAI Quality System \(AIQS\)\b/g, 'Système qualité IA (AIQS)')
      .replace(/\bHigh-Bay Warehouse \(HBW\)\b/g, 'Entrepôt haute-bay (HBW)')
      .replace(/\bCharging Station\b/g, 'Station de charge')
      .replace(/\bAutomated Guided Vehicle\b/g, 'Véhicule à guidage automatique')
      .replace(/\bHigh Bay Warehouse\b/g, 'Entrepôt haute-bay')
      .replace(/\bDelivery and Pickup Station\b/g, 'Station livraison et collecte')
      .replace(/\bAI Quality Station\b/g, 'Station qualité IA')
      .replace(/\bDrilling Station\b/g, 'Station de perçage').replace(/\bMilling Station\b/g, 'Station de fraisage')
      .replace(/\bOrders\b/g, 'Commandes').replace(/\bModules\b/g, 'Modules').replace(/\bProcesses\b/g, 'Processus')
      .replace(/\bEnvironment Data\b/g, 'Données environnement').replace(/\bSettings\b/g, 'Paramètres')
      .replace(/\bConfiguration\b/g, 'Configuration').replace(/\bMessage Monitor\b/g, 'Moniteur de messages')
      .replace(/\bShopfloor\b/g, 'Atelier').replace(/\bDSP\b/g, 'DSP').replace(/\bAGV\b/g, 'AGV');
  }
  return t;
}

function main() {
  const missingPath = join(localeDir, 'missing_keys.txt');
  let missingText;
  try {
    missingText = readFileSync(missingPath, 'utf8');
  } catch {
    console.error('missing_keys.txt not found. Run build first to generate it.');
    process.exit(1);
  }

  const pairs = new Map(); // key -> default (prefer one with placeholder)
  for (const line of missingText.split('\n')) {
    const m = line.match(/^([a-zA-Z0-9_.]+)\|(.+)$/);
    if (m) {
      const [, key, val] = m;
      if (!pairs.has(key) || val.includes('{$') || val.includes('{$PH}')) pairs.set(key, val);
    }
  }

  const truncatedKeys = [
    ['dspArchLabelAnalytics', 'Analytical\nApplications'],
    ['dspArchLabelCloudApps', 'Cloud\nApplications'],
    ['dspArchLabelFTS', 'AGV\nSystem'],
    ['dspArchLabelManagement', 'Management\nCockpit'],
    ['dspArchLabelUX', 'SmartFactory\nDashboard'],
  ];
  for (const [k, v] of truncatedKeys) pairs.set(k, v);

  const dePath = join(localeDir, 'messages.de.json');
  const frPath = join(localeDir, 'messages.fr.json');
  const de = JSON.parse(readFileSync(dePath, 'utf8'));
  const fr = JSON.parse(readFileSync(frPath, 'utf8'));

  let addedDe = 0, addedFr = 0;
  for (const [key, defaultEn] of pairs) {
    if (!de.translations[key]) {
      de.translations[key] = translatePhrase(defaultEn, 'de');
      addedDe++;
    }
    if (!fr.translations[key]) {
      fr.translations[key] = translatePhrase(defaultEn, 'fr');
      addedFr++;
    }
  }

  writeFileSync(dePath, JSON.stringify(de, null, 2), 'utf8');
  writeFileSync(frPath, JSON.stringify(fr, null, 2), 'utf8');

  console.log(`Added ${addedDe} keys to messages.de.json, ${addedFr} keys to messages.fr.json`);
}

main();
