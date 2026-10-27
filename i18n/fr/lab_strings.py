"""French strings for the Lab 03 browser lab (initial bipartition).

Each entry is (file, English source text, French text). build_site.py copies the lab
into docs/fr/ and replaces every English snippet. If a snippet is no longer found
(the lab changed in eda-learning), the build stops, so a half-translated lab is never
published: update the snippet here and rebuild.

Paths are relative to docs/fr/. Challenge ids, CSS classes, node names (A–F), method keys
and numbers stay as they are. Vocabulary: partition (split), côté (side), taille de coupe
(cutsize), équilibre (balance), valide (legal), glouton (greedy), croissance (grow), graine (seed).
"""

LAB = "tools/initial-bipartition/"
UI = "assets/clustering-ui.js"
UIJS = LAB + "initial-bipartition.js"
MODEL = LAB + "initial-bipartition-lab-model.js"

STRINGS = [
    # ---------------- page (index.html) ----------------
    (LAB + "index.html", '<html lang="en">', '<html lang="fr">'),
    (LAB + "index.html", "<title>Initial bipartition — EDA Algorithms Platform</title>",
     "<title>Bipartition initiale — EDA Algorithms Platform</title>"),
    (LAB + "index.html", ">Skip to content<", ">Aller au contenu<"),
    (LAB + "index.html", '<div class="eyebrow">Interactive tool</div>', '<div class="eyebrow">Outil interactif</div>'),
    (LAB + "index.html", "<h1>Initial bipartition</h1>", "<h1>Bipartition initiale</h1>"),
    (LAB + "index.html",
     "Build a legal starting split by hand, run random, greedy and grow, and compare their cuts on four small graphs.",
     "Construisez à la main une partition de départ valide, lancez l'aléatoire, le glouton et la croissance, et comparez leurs coupes sur quatre petits graphes."),

    # ---------------- shared challenge chrome (clustering-ui.js) ----------------
    (UI, 'statusText: "Idle"', 'statusText: "En attente"'),
    (UI, '"Challenge armed — act, then Check"', '"Défi lancé : agissez, puis Vérifier"'),
    (UI, '"Starter loaded (reference)"', '"Exemple de départ chargé (référence)"'),
    (UI, '"Load a challenge with Start"', '"Lancez un défi avec Commencer"'),
    (UI, 'setStatus("pass", "PASS")', 'setStatus("pass", "RÉUSSI")'),
    (UI, '"Not yet — try again or show hint"', '"Pas encore : réessayez ou affichez l\'indice"'),
    (UI, '"Load starter example"', '"Charger l\'exemple de départ"'),
    (UI, "<h2>Challenges</h2>", "<h2>Défis</h2>"),
    (UI, "${challenges.length} cleared</span>", "${challenges.length} réussis</span>"),
    (UI, '<label for="lab-chal-sel">Pick one</label>', '<label for="lab-chal-sel">Choisir</label>'),
    (UI, '"Pick a challenge and click <strong>Start</strong>. The starter example above stays available as a reference — reload it anytime."',
     '"Choisissez un défi et cliquez sur <strong>Commencer</strong>. L\'exemple de départ reste disponible comme référence : rechargez-le quand vous voulez."'),
    (UI, "<strong>Hint:</strong>", "<strong>Indice :</strong>"),
    (UI, '"Restart" : "Start"', '"Recommencer" : "Commencer"'),
    (UI, '"Hide hint" : "Show hint"', '"Masquer l\'indice" : "Afficher l\'indice"'),
    (UI, '"disabled"}>Check</button>', '"disabled"}>Vérifier</button>'),
    (UI, ">Next challenge</button>", ">Défi suivant</button>"),
    (UI, ">Stop checking</button>", ">Arrêter le défi</button>"),
    (UI, 'el("h2", { text: "Graph" })', 'el("h2", { text: "Graphe" })'),
    (UI, 'el("h2", { text: "Reference / metrics" })', 'el("h2", { text: "Travail et mesures" })'),

    # ---------------- model: graph names ----------------
    (MODEL, 'label: "Tiny graph (A–E)"', 'label: "Petit graphe (A–E)"'),
    (MODEL, 'label: "Star graph (size limit)"', 'label: "Graphe en étoile (limite de taille)"'),
    (MODEL, 'label: "Tie graph (two heaviest edges)"', 'label: "Graphe à égalité (deux arêtes les plus lourdes)"'),
    (MODEL, 'label: "Bridge graph (heavy middle wire)"', 'label: "Graphe pont (fil lourd au milieu)"'),

    # ---------------- model: how each start is built (the trace shown to the learner) ----------------
    (MODEL, "`anchor ${u0}–${v0} (heaviest edge) → side 0`", "`ancre ${u0}–${v0} (arête la plus lourde) → côté 0`"),
    (MODEL, "`${seed1} → side 1 (weakest tie to the anchor: ${tie(seed1)})`",
     "`${seed1} → côté 1 (lien le plus faible avec l'ancre : ${tie(seed1)})`"),
    (MODEL, '"side 0 is full"', '"le côté 0 est plein"'),
    (MODEL, '"side 1 is full"', '"le côté 1 est plein"'),
    (MODEL, "`cut +${add0}; side 1 would add ${add1}`", "`coupe +${add0} ; le côté 1 ajouterait ${add1}`"),
    (MODEL, "`cut +${add1}; side 0 would add ${add0}`", "`coupe +${add1} ; le côté 0 ajouterait ${add0}`"),
    (MODEL, "`${x} → side ${pick} (${why})`", "`${x} → côté ${pick} (${why})`"),
    (MODEL, "`start ${start}`", "`départ ${start}`"),
    (MODEL, "`no edge leaves: take ${best.v}`", "`aucune arête ne sort : on prend ${best.v}`"),
    (MODEL, "`+ ${best.v} (edge ${best.u}–${best.v}, weight ${best.w})`", "`+ ${best.v} (arête ${best.u}–${best.v}, poids ${best.w})`"),

    # ---------------- model: method names and messages ----------------
    (MODEL, "`random seed ${m.seed}`", "`aléatoire graine ${m.seed}`"),
    (MODEL, "`grow from ${m.start}`", "`croissance depuis ${m.start}`"),
    (MODEL, 'return "greedy";', 'return "glouton";'),
    (MODEL, '"Type a whole number 0 or more as the seed."', '"Saisissez un entier supérieur ou égal à 0 comme graine."'),
    (MODEL, '`shuffled order: ${res.order.join(" ")}`', '`ordre mélangé : ${res.order.join(" ")}`'),
    (MODEL, "`side 0 = first ${Math.floor(s.nodes.length / 2)} names`", "`côté 0 = les ${Math.floor(s.nodes.length / 2)} premiers noms`"),
    (MODEL, "`Random seed ${k}: ${parts(n)}, cut ${cut(n)}.`", "`Aléatoire, graine ${k} : ${parts(n)}, coupe ${cut(n)}.`"),
    (MODEL, "`Greedy: ${parts(n)}, cut ${cut(n)}.`", "`Glouton : ${parts(n)}, coupe ${cut(n)}.`"),
    (MODEL, "`Grow from ${start}: ${parts(n)}, cut ${cut(n)}.`", "`Croissance depuis ${start} : ${parts(n)}, coupe ${cut(n)}.`"),
    (MODEL, "`${id} → side ${n.asn[id]}. You edited the ${methodLabel(wasMethod)} split: it now counts as your own.`",
     "`${id} → côté ${n.asn[id]}. Vous avez modifié la partition « ${methodLabel(wasMethod)} » : elle compte maintenant comme la vôtre.`"),
    (MODEL, "`${id} → side ${n.asn[id]}.`", "`${id} → côté ${n.asn[id]}.`"),
    (MODEL, "`${id} is already in the grown side.`", "`${id} est déjà dans le côté qui grandit.`"),
    (MODEL, '`Grown side: ${n.handGrow.order.join(", ")} (${target} nodes). Done — press Check.`',
     '`Côté qui grandit : ${n.handGrow.order.join(", ")} (${target} nœuds). Terminé : cliquez sur Vérifier.`'),
    (MODEL, '`Grown side: ${n.handGrow.order.join(", ")}. Click the next node grow would take.`',
     '`Côté qui grandit : ${n.handGrow.order.join(", ")}. Cliquez sur le nœud que la croissance prendrait ensuite.`'),

    # ---------------- lab script: levels and the ten challenges ----------------
    (UIJS, 'level: "Intro"', 'level: "Initiation"'),
    (UIJS, 'level: "Practice"', 'level: "Pratique"'),
    (UIJS, 'level: "Stretch"', 'level: "Approfondissement"'),
    # 1 two-sides
    (UIJS, '"A legal split by hand"', '"Une partition valide à la main"'),
    (UIJS, '"Tiny graph. Click nodes to put every node on a side yourself (no start button). Legal means no grey node left and no side with more than 3 nodes."',
     '"Petit graphe. Cliquez sur les nœuds pour mettre chacun sur un côté vous-même (sans bouton de départ). Valide veut dire : plus aucun nœud gris et aucun côté de plus de 3 nœuds."'),
    (UIJS, '"One click puts a grey node on side 0; the next click moves it to side 1. Two on one side and three on the other is legal."',
     '"Un clic met un nœud gris sur le côté 0 ; le clic suivant le passe sur le côté 1. Deux d\'un côté et trois de l\'autre, c\'est valide."'),
    # 2 hand-cut-3
    (UIJS, '"Best split by hand: cut 3"', '"La meilleure partition à la main : coupe 3"'),
    (UIJS, '"Tiny graph. Build by hand the legal split with the smallest cut. The red dashed edges are the ones you cut."',
     '"Petit graphe. Construisez à la main la partition valide qui a la plus petite coupe. Les arêtes rouges en pointillés sont celles que vous coupez."'),
    (UIJS, '"Keep both weight-5 edges inside a side: A–B together, D–E together. Where does C cut less?"',
     '"Gardez les deux arêtes de poids 5 à l\'intérieur d\'un côté : A–B ensemble, D–E ensemble. Où C coupe-t-il le moins ?"'),
    # 3 grow-d-cut-3
    (UIJS, '"Grow from D by hand"', '"Croissance depuis D à la main"'),
    (UIJS, "Tiny graph. Press “Grow by hand”, click D, then click the node that grow adds next: the end of the heaviest edge leaving the grown side.",
     "Petit graphe. Cliquez sur « Croissance à la main », cliquez sur D, puis sur le nœud que la croissance ajoute ensuite : le bout de l'arête la plus lourde qui sort du côté qui grandit."),
    (UIJS, '"The grown side stops at 2 nodes (half of 5, rounded down). D\'s heaviest edge is D–E (5)."',
     '"Le côté qui grandit s\'arrête à 2 nœuds (la moitié de 5, arrondie vers le bas). L\'arête la plus lourde de D est D–E (5)."'),
    # 4 grow-a-cut-5
    (UIJS, '"Fix grow from A with one move"', '"Corriger la croissance depuis A en un seul déplacement"'),
    (UIJS, "Tiny graph. Run “Grow from A” (cut 5). Then move exactly ONE node so the split stays legal and the cut drops to 3.",
     "Petit graphe. Lancez « Croissance depuis A » (coupe 5). Puis déplacez exactement UN nœud pour que la partition reste valide et que la coupe tombe à 3."),
    (UIJS, '"Grow from A stops at A, B. Node C hangs on B with weight 4: which side should it join?"',
     '"La croissance depuis A s\'arrête à A, B. Le nœud C tient à B par un poids de 4 : quel côté doit-il rejoindre ?"'),
    # 5 random-lucky
    (UIJS, '"Find a lucky seed"', '"Trouver une graine chanceuse"'),
    (UIJS, '"Tiny graph. Type seeds and run random until the split has cut 3, as good as the best split. Leave that random split on screen."',
     '"Petit graphe. Saisissez des graines et lancez l\'aléatoire jusqu\'à obtenir une coupe de 3, aussi bonne que la meilleure partition. Laissez cette partition aléatoire à l\'écran."'),
    (UIJS, '"Most seeds are unlucky. Try 0, 1, 2 … and read the cut each time; the log lists every seed you ran."',
     '"La plupart des graines sont malchanceuses. Essayez 0, 1, 2 … et lisez la coupe à chaque fois ; le journal liste chaque graine lancée."'),
    # 6 keep-best
    (UIJS, '"Keep the best of four seeds"', '"Garder la meilleure de quatre graines"'),
    (UIJS, '"Tiny graph. Run random with at least four different seeds. Then put the best one you found back on screen (run its seed again)."',
     '"Petit graphe. Lancez l\'aléatoire avec au moins quatre graines différentes. Puis remettez à l\'écran la meilleure trouvée (relancez sa graine)."'),
    (UIJS, '"The log on the right lists the cut of every seed you tried. The smallest one wins; ties are fine."',
     '"Le journal à droite liste la coupe de chaque graine essayée. La plus petite gagne ; les égalités sont acceptées."'),
    # 7 grow-best-start
    (UIJS, '"Best start node for grow"', '"Le meilleur nœud de départ pour la croissance"'),
    (UIJS, '"Bridge graph. Run grow from EVERY node, compare the cuts in the log, then leave a grow split with the smallest cut on screen."',
     '"Graphe pont. Lancez la croissance depuis CHAQUE nœud, comparez les coupes dans le journal, puis laissez à l\'écran une partition de croissance de plus petite coupe."'),
    (UIJS, '"Grow stops at 3 nodes. Starting on the left triangle keeps the triangle together; starting at C or D pulls the bridge in."',
     '"La croissance s\'arrête à 3 nœuds. Partir du triangle de gauche garde le triangle ensemble ; partir de C ou D attire le pont."'),
    # 8 hand-grow-tie
    (UIJS, '"Grow by hand through a tie"', '"Croissance à la main à travers une égalité"'),
    (UIJS, '"Bridge graph. Grow by hand from C, in the rule\'s order. After the bridge, four edges of weight 3 tie: the rule takes the smaller name."',
     '"Graphe pont. Faites grandir à la main depuis C, dans l\'ordre de la règle. Après le pont, quatre arêtes de poids 3 sont à égalité : la règle prend le plus petit nom."'),
    (UIJS, '"C first, then D (the bridge, weight 4). Then C–A, C–B, D–E and D–F all weigh 3: pick the smallest letter."',
     '"C d\'abord, puis D (le pont, poids 4). Ensuite C–A, C–B, D–E et D–F pèsent toutes 3 : prenez la plus petite lettre."'),
    # 9 star-cap
    (UIJS, '"Star: the best legal split"', '"Étoile : la meilleure partition valide"'),
    (UIJS, '"Star graph. Build by hand the legal split with the smallest cut. Six nodes, so each side holds 3. Is cut 5 possible if it must be legal?"',
     '"Graphe en étoile. Construisez à la main la partition valide de plus petite coupe. Six nœuds, donc chaque côté en contient 3. Une coupe de 5 est-elle possible si elle doit être valide ?"'),
    (UIJS, '"Everything around A on one side gives cut 5, but that is 5 nodes against 1: not legal. Keep A–B (9) together."',
     '"Tout autour de A du même côté donne une coupe de 5, mais c\'est 5 nœuds contre 1 : pas valide. Gardez A–B (9) ensemble."'),
    # 10 manual-beats-greedy
    (UIJS, '"Beat greedy on the tie graph"', '"Battre le glouton sur le graphe à égalité"'),
    (UIJS, '"Tie graph. Run greedy first: it anchors on A–B, one of two edges of weight 5. Then build by hand a legal split with cut 4."',
     '"Graphe à égalité. Lancez d\'abord le glouton : il s\'ancre sur A–B, l\'une des deux arêtes de poids 5. Puis construisez à la main une partition valide de coupe 4."'),
    (UIJS, '"Greedy keeps A–B and cuts D–E. Keep BOTH weight-5 edges inside, and cut only light edges."',
     '"Le glouton garde A–B et coupe D–E. Gardez LES DEUX arêtes de poids 5 à l\'intérieur, et ne coupez que des arêtes légères."'),

    # ---------------- lab script: toolbar, workspace, messages ----------------
    (UIJS, '"aria-label": "Graph",', '"aria-label": "Graphe",'),
    (UIJS, '`Graph changed to ${M.GRAPHS[state.graphKey].label}: the split and the log were cleared.`',
     '`Graphe changé : ${M.GRAPHS[state.graphKey].label}. La partition et le journal ont été effacés.`'),
    (UIJS, '["Graph ", sel]', '["Graphe ", sel]'),
    (UIJS, 'btn("Clear split"', 'btn("Effacer la partition"'),
    (UIJS, '"Split cleared: every node is grey again."', '"Partition effacée : tous les nœuds sont de nouveau gris."'),
    (UIJS, '"revealed best split (study) — does not count"', '"meilleure partition révélée (révision) : ne compte pas"'),
    (UIJS, "`${M.methodLabel(state.method)} (unchanged)`", "`${M.methodLabel(state.method)} (inchangée)`"),
    (UIJS, '"your hand grow (finished)" : "your hand grow (in progress)"', '"votre croissance à la main (terminée)" : "votre croissance à la main (en cours)"'),
    (UIJS, "`your edits of ${M.methodLabel(state.base.method)} (${M.movedSinceStart(state).length} node(s) moved)`",
     "`vos modifications de « ${M.methodLabel(state.base.method)} » (${M.movedSinceStart(state).length} nœud(s) déplacé(s))`"),
    (UIJS, 'return "your clicks";', 'return "vos clics";'),
    (UIJS, "`legal: no (${unplaced} grey node(s) not placed)`", "`valide : non (${unplaced} nœud(s) gris non placé(s))`"),
    (UIJS, '"legal: no (one side is empty)"', '"valide : non (un côté est vide)"'),
    (UIJS, "`legal: no (a side holds more than ${cap})`", "`valide : non (un côté contient plus de ${cap})`"),
    (UIJS, '"legal: yes"', '"valide : oui"'),
    (UIJS, '"Click a node to move it to the other side (grey → side 0 → side 1 → side 0 …)."',
     '"Cliquez sur un nœud pour le passer de l\'autre côté (gris → côté 0 → côté 1 → côté 0 …)."'),
    (UIJS, '"aria-label": "Random seed"', '"aria-label": "Graine aléatoire"'),
    (UIJS, 'row("Random", [', 'row("Aléatoire", ['),
    (UIJS, 'btn("Run random"', 'btn("Lancer l\'aléatoire"'),
    (UIJS, 'row("Greedy", [btn("Run greedy"', 'row("Glouton", [btn("Lancer le glouton"'),
    (UIJS, 'row("Grow from", state.nodes', 'row("Croissance depuis", state.nodes'),
    (UIJS, 'row("By hand", [', 'row("À la main", ['),
    (UIJS, 'btn("Grow by hand"', 'btn("Croissance à la main"'),
    (UIJS, "`Grow by hand: all nodes are on side 1. Click your start node, then each node grow would add, until side 0 holds ${Math.floor(state.nodes.length / 2)}.`",
     "`Croissance à la main : tous les nœuds sont sur le côté 1. Cliquez sur votre nœud de départ, puis sur chaque nœud que la croissance ajouterait, jusqu'à ce que le côté 0 en contienne ${Math.floor(state.nodes.length / 2)}.`"),
    (UIJS, 'row("Study", [', 'row("Révision", ['),
    (UIJS, 'btn("Reveal best split (study)"', 'btn("Révéler la meilleure partition (révision)"'),
    (UIJS, '"Best legal split revealed (study): it does not count for any challenge. Clear the split or run a start to go on."',
     '"Meilleure partition valide révélée (révision) : elle ne compte pour aucun défi. Effacez la partition ou lancez un départ pour continuer."'),

    # ---------------- lab script: the metrics block ----------------
    (UIJS, "`graph: ${M.GRAPHS[state.graphKey].label}`", "`graphe : ${M.GRAPHS[state.graphKey].label}`"),
    (UIJS, '`split: ${M.parts(state) || "—"}`', '`partition : ${M.parts(state) || "—"}`'),
    (UIJS, "`cutsize: ${M.cut(state)}", "`taille de coupe : ${M.cut(state)}"),
    (UIJS, "`balance: ${s0} | ${s1} nodes (limit ${M.capOf(state.nodes.length)} per side)`",
     "`équilibre : ${s0} | ${s1} nœuds (limite ${M.capOf(state.nodes.length)} par côté)`"),
    (UIJS, "`colours: blue = side ${blueSide()} (has ${", "`couleurs : bleu = côté ${blueSide()} (contient ${"),
    (UIJS, "`made by: ${sourceLine()}`", "`obtenue par : ${sourceLine()}`"),
    (UIJS, '"how the start was built:"', '"comment le départ a été construit :"'),
    (UIJS, '"starts you ran on this graph:"', '"départs lancés sur ce graphe :"'),
    (UIJS, '`  ${M.methodLabel(t).padEnd(15)} ${t.parts.padEnd(8)} cut ${t.cut}${t.legal ? "" : "  (not legal)"}`',
     '`  ${M.methodLabel(t).padEnd(22)} ${t.parts.padEnd(8)} coupe ${t.cut}${t.legal ? "" : "  (non valide)"}`'),
    (UIJS, '"  (none yet)"', '"  (aucun pour l\'instant)"'),

    # ---------------- lab script: challenge box ----------------
    (UIJS, 'starterButtonLabel: "Reset workspace"', 'starterButtonLabel: "Réinitialiser"'),
    (UIJS, '"Pick a challenge and click <strong>Start</strong>. Build the split yourself, then <strong>Check</strong>. The reveal is for study: what it shows never counts."',
     '"Choisissez un défi et cliquez sur <strong>Commencer</strong>. Construisez la partition vous-même, puis <strong>Vérifier</strong>. La révélation sert à réviser : ce qu\'elle montre ne compte jamais."'),
    (UIJS, """<p><strong>Your workspace:</strong> click nodes to move them between the two sides and watch the
    cutsize and the balance. Run random, greedy and grow, and compare their cuts in the log.
    Challenges check the split <em>you</em> built: a start you edit no longer counts as that start,
    and the study reveal never counts.</p>""",
     """<p><strong>Votre espace de travail :</strong> cliquez sur les nœuds pour les passer d'un côté à l'autre et observez
    la taille de coupe et l'équilibre. Lancez l'aléatoire, le glouton et la croissance, et comparez leurs coupes dans le journal.
    Les défis vérifient la partition que <em>vous</em> avez construite : un départ que vous modifiez ne compte plus comme ce départ,
    et la révélation de révision ne compte jamais.</p>"""),
]
