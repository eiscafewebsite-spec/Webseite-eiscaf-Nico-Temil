// Diese Datei enthält ALLE Preise der Speisekarte.
// Hier kannst du jederzeit Preise, Namen oder Beschreibungen ändern,
// ohne die index.html anzufassen. Einfach speichern und hochladen.
//
// Wichtig: Diese Zahlen/Texte tauchen an zwei Stellen auf, die eigentlich
// dasselbe sagen sollten - bitte beide gleich halten:
//   - kugelPreis (oben, für die Werbe-Badges)
//   - der Satz "Kugel Eis ..." in kategorien.eis.hinweis

const SPEISEKARTE = {

  // Wird in den Badges "1 Kugel = 1,00 €" verwendet (Startseite + Preis-Banner)
  kugelPreis: "1,00 €",

  // Preis fürs Eismobil (Eiswagen-Sektion)
  eismobil: {
    preis: "1,50 €",
    einheit: "pro Kugel Eis"
  },

  kategorien: {

    // ── EISBECHER ──
    eis: {
      label: "Eisbecher",
      hinweis: "Alle Eisbecher auch zum Mitnehmen (außer Haus). · Kugel Eis 1,00 € · Portion Sahne 1,50 € · Sauce extra 0,80 € · Streusel extra 0,80 €",
      extras: "Kugel Eis 1,00 € · Portion Sahne 1,50 € · Sauce extra 0,80 € · Streusel extra 0,80 €",
      items: [
        { name: "Amarena-Becher", preis: "10,90 €", desc: "gemischtes Eis, Amarena-Kirschen, Amarena-Sauce & Sahne" },
        { name: "Joghurt-Becher", preis: "10,60 €", desc: "gemischtes Eis, Natur-Joghurt & Sauce, wahlweise Kiwi, Banane, Amarena-Kirschen, Erdbeeren (nach Saison), Heidelbeeren" },
        { name: "Bananensplit", preis: "9,90 €", desc: "gemischtes Eis, Bananen, Streusel, Schoko-Sauce & Sahne" },
        { name: "Coppa per due", preis: "auf Anfrage", desc: "für 2 Personen – gemischtes Eis, gemischtes Obst, Schoko-Pralinen, Erdbeer- & Schoko-Sauce & Sahne" },
        { name: "Kiwi-Becher", preis: "9,90 €", desc: "gemischtes Eis, frische Kiwi, Kiwi-Sauce & Sahne" },
        { name: "Heidelbeer-Becher", preis: "10,60 €", desc: "gemischtes Eis, Heidelbeeren, Sauce & Sahne" },
        { name: "Erdbeer-Becher", preis: "9,90 €", desc: "nach Saison – gemischtes Eis, Erdbeeren, Erdbeer-Sauce & Sahne" },
        { name: "Früchte-Becher", preis: "10,90 €", desc: "gemischtes Eis, frisches Obst (nach Saison), Sauce & Sahne" },
        { name: "After Eight-Becher", preis: "10,90 €", desc: "gemischtes Eis, Minz- & Schoko-Sauce & Sahne" },
        { name: "Krokant-Becher", preis: "10,50 €", desc: "gemischtes Eis, Krokantsplitter, Karamell-Sauce & Sahne" },
        { name: "Rocher-Becher", preis: "10,90 €", desc: "nach Saison – gemischtes Eis, Rocher Pralinen, Nusskrokant, Karamell-Sauce & Sahne" },
        { name: "Raffaello-Becher", preis: "10,90 €", desc: "nach Saison – gemischtes Eis, Raffaello Pralinen, weiße Schokolade, Sauce & Sahne" },
        { name: "Schoko-Becher", preis: "10,90 €", desc: "gemischtes Eis, Schoko-Splitter, Schoko-Sauce & Sahne" },
        { name: "Nuss-Becher", preis: "10,90 €", desc: "gemischtes Eis, Haselnüsse, Nuss-Sauce & Sahne" },
        { name: "Amaretto-Becher", preis: "10,90 €", desc: "gemischtes Eis, Amaretto-Likör, Amarettokekse, Krokant, Sauce & Sahne" },
        { name: "Kiba-Becher", preis: "10,90 €", desc: "Kirsch-Banane – gemischtes Eis, Amarena-Kirschen, Banane, Amarena-Sauce & Sahne" },
        { name: "Melonen-Becher", preis: "10,90 €", desc: "nach Saison – gemischtes Eis, frische Melone, Tropical-Sauce & Sahne" },
        { name: "Spaghetti Carbonara", preis: "9,40 €", desc: "Vanilleeis, Krokantstreusel, Karamell-Sauce & Sahne", gruppe: "spaghetti" },
        { name: "Spaghetti-Eis", preis: "9,40 €", desc: "Vanilleeis, weiße Schokolade, Erdbeer-Sauce & Sahne", gruppe: "spaghetti" },
        { name: "Spaghetti-Kiwi", preis: "9,90 €", desc: "Vanilleeis, Sahne, weiße Schokolade, Kiwi-Sauce, frische Kiwis", gruppe: "spaghetti" },
        { name: "Spaghetti-Fragole", preis: "9,90 €", desc: "Vanilleeis, Sahne, weiße Schokolade, Kiwi-Sauce, frische Erdbeeren", gruppe: "spaghetti" },
        { name: "Spaghetti-Italia", preis: "9,90 €", desc: "Vanilleeis, Sahne, weiße Schokolade, Kiwi-Sauce, Erdbeer-Sauce, Kiwis, Erdbeeren", gruppe: "spaghetti" },
        { name: "Spaghetti Eis für Kinder", preis: "7,60 €", desc: "Vanilleeis, Erdbeer-Sauce, weiße Schokolade & Sahne", gruppe: "kinder" },
        { name: "Kinder-Eisbecher", preis: "8,50 €", desc: "2 Kugeln gemischtes Eis, Kinder-Überraschung, Smarties, Sauce & Sahne", gruppe: "kinder" },
        { name: "Pinocchio Eis", preis: "6,15 €", desc: "gemischtes Eis, Smarties, Zuckerstreusel & Sahne", gruppe: "kinder" },
        { name: "Micky Maus Eis", preis: "6,15 €", desc: "gemischtes Eis, Smarties, Zuckerstreusel & Sahne", gruppe: "kinder" }
      ]
    },

    // ── KAFFEE & HEISSGETRÄNKE ──
    kaffee: {
      label: "Kaffeespezialitäten",
      items: [
        { name: "Kaffee Crema", preis: "1,70 €", desc: "auch entcoffeiniert" },
        { name: "Pott Kaffee Crema", preis: "3,10 €", desc: "auch entcoffeiniert" },
        { name: "Kännchen", preis: "3,10 €", desc: "auch entcoffeiniert" },
        { name: "Milchkaffee", preis: "3,40 €" },
        { name: "Espresso", preis: "1,40 €", desc: "auch groß 2,60 €" },
        { name: "Espresso Macchiato", preis: "2,00 €" },
        { name: "Cappuccino", preis: "3,90 €", desc: "auch groß 4,60 €" },
        { name: "Espresso-Cappuccino", preis: "4,90 €" },
        { name: "Schoko-Cappuccino", preis: "4,90 €" },
        { name: "Eiskaffee", preis: "4,90 €" },
        { name: "Latte Macchiato", preis: "3,60 €" },
        { name: "Iced Latte Macchiato", preis: "3,90 €" },
        { name: "Caffè Latte", preis: "4,60 €" },
        { name: "Nico Spezial", preis: "–", desc: "Eierlikör" },
        { name: "Latte Macchiato Flavour", preis: "4,90 €", desc: "Haselnuss, Karamell, Vanille, Erdbeere, Schokolade, Curaçao Bleu alk.frei, Amaretto alk.frei" }
      ]
    },

    // ── SHAKES & MILCHGETRÄNKE ──
    shakes: {
      label: "Getränke",
      items: [
        { name: "Hot Chocolate", preis: "3,35 €", gruppe: "schokolade" },
        { name: "Hot Chocolate + Sahne", preis: "4,35 €", gruppe: "schokolade" },
        { name: "Hot Chocolate mit Baileys oder Karamell", preis: "4,60 €", gruppe: "schokolade" },
        { name: "Hot'n Cold Chocolate", preis: "4,00 €", gruppe: "schokolade" },
        { name: "Chococcino", preis: "4,20 €", gruppe: "schokolade" },
        { name: "Iced Chococcino", preis: "4,70 €", gruppe: "schokolade" },
        { name: "Milchshake mit Sahne", preis: "3,90 €", desc: "ohne Eis – Erdbeere, Vanille, Schoko, Banane, Mango, Cookies, Mint", gruppe: "shake" },
        { name: "Eismilchshake mit Sahne", preis: "4,90 €", desc: "mit Eis – Erdbeere, Vanille, Schoko, Banane, Mango, Cookies, Mint", gruppe: "shake" },
        { name: "Coca Cola 0,33 l", preis: "2,50 €", gruppe: "kalt" },
        { name: "Fanta, Sprite 0,33 l", preis: "2,50 €", gruppe: "kalt" },
        { name: "Banane, Kirsche, Orange, Apfel", preis: "2,50 €", gruppe: "kalt" },
        { name: "Mineralwasser 0,33 l", preis: "1,90 €", gruppe: "kalt" },
        { name: "Stilles Wasser", preis: "1,60 €", gruppe: "kalt" },
        { name: "Apfelschorle, Multi 0,33 l", preis: "2,50 €", gruppe: "kalt" },
        { name: "KIBA", preis: "2,70 €", desc: "Kirsch-Banane", gruppe: "kalt" },
        { name: "Caprisonne", preis: "1,00 €", gruppe: "kalt" }
      ]
    },

    // ── WEIN & COCKTAILS ──
    cocktails: {
      label: "Weine & Cocktails",
      items: [
        { name: "Weißwein 0,25 l", preis: "2,80 €" },
        { name: "Rotwein 0,25 l", preis: "2,80 €" },
        { name: "Weißweinschorle", preis: "2,50 €" },
        { name: "Rotweinschorle", preis: "2,50 €" },
        { name: "Sekt", preis: "2,80 €" },
        { name: "Bier (Flasche 0,5 l)", preis: "2,10 €" },
        { name: "Radler", preis: "2,10 €" },
        { name: "Grüne Wiese", preis: "5,90 €", desc: "Blue Curaçao, O-Saft, Sekt" },
        { name: "Orangen Cup", preis: "5,90 €", desc: "O-Saft, Van.-Eis, Sekt" },
        { name: "Sanfter Engel", preis: "3,90 €", desc: "O-Saft, Van.-Eis, Sahne" },
        { name: "Sanfter Engel mit Rum", preis: "5,90 €", desc: "mit Alkohol" },
        { name: "Cola Whisky", preis: "5,90 €" },
        { name: "Arancia Crema", preis: "4,00 €", desc: "O-Saft, Eis, Sahne, Amarena" },
        { name: "Latina Kiss", preis: "4,00 €", desc: "Kirschsaft, Eis, Sahne, Amarena" },
        { name: "Formula One", preis: "5,90 €", desc: "Rum, Kokoslikör, Ananas, Grenadine" },
        { name: "Planter's Punch", preis: "5,90 €", desc: "Rum, Orange, Ananas, Zitrone" }
      ]
    }
  },

  // ── KUCHEN & SÜSSES (eigenes Layout mit Emoji-Kacheln) ──
  // preis: null = kein fester Preis (z.B. "siehe Auslage")
  kuchen: [
    { emoji: "🎂", titel: "Tortenangebot", desc: "siehe Auslage – wechselnde Angebote", preis: null },
    { emoji: "🥐", titel: "1 Apfelstrudel", desc: "mit Sahne & Eis", preis: "4,90 €" },
    { emoji: "🥞", titel: "2 Eierkuchen", desc: "Apfelmus oder Zimt-Zucker, mit Sahne & Eis", preis: "4,90 €" }
  ]

};
