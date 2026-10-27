# Bipartition initiale

**Module id:** module01-03-initial-bipartition
**Lab:** initial-bipartition
**Tracks:** A (implémentation) · B (lab dans le navigateur)

## Slide 1 — Bipartition initiale

Avant d'améliorer une coupe, il faut une première coupe. Cette première coupe s'appelle la bipartition initiale. Vous allez découvrir trois façons de la construire : aléatoire, gloutonne et par croissance. Vous verrez le même petit graphe obtenir une coupe de trois, ou une coupe de seize. Et vous apprendrez la bonne habitude qui règle ce problème : essayer plusieurs départs, et garder le meilleur.

## Slide 2 — D'une puce à un graphe

![Des cellules et des fils sur une puce, puis la même chose dessinée en graphe](assets/chip-to-graph.png)

Une puce est faite de petites briques appelées cellules, reliées par des fils. On dessine chaque cellule comme un point, appelé nœud. Un trait entre deux nœuds est une arête : les deux cellules sont reliées. Le nombre sur une arête est son poids : combien de fils relient la paire. Notre exemple a cinq cellules, de A à E. Les arêtes les plus lourdes, A–B et D–E, ont cinq fils chacune.

## Slide 3 — Deux nombres : coupe et équilibre

![Une partition valide de coupe trois, et tout du même côté avec une coupe de zéro, qui n'est pas valide](assets/cut-and-balance.png)

Couper une puce en deux côtés s'appelle une bipartition. Les arêtes qui passent d'un côté à l'autre sont coupées, et on les dessine en rouge. La taille de coupe additionne leurs poids : ici, deux plus un font trois. Tout mettre du même côté donne une coupe de zéro, mais cela ne sert à rien. On vérifie donc aussi l'équilibre : combien de cellules chaque côté contient. Une partition est valide quand aucun côté ne dépasse trois cellules sur cinq.

## Slide 4 — Pourquoi une partition de départ ?

Les labs quatre et cinq enseignent deux méthodes célèbres, appelées KL et FM. Elles améliorent une partition en déplaçant des cellules d'un côté à l'autre. Mais elles ne peuvent qu'améliorer : il leur faut une partition valide pour démarrer. Pensez à former deux équipes pour un jeu. D'abord deux équipes au hasard, puis on échange des joueurs pour équilibrer. Un bon premier découpage laisse moins d'échanges à faire.

<!-- algorithm-walkthrough -->

## Slide 5 — Il faut une partition de départ valide

![Il faut une partition de départ valide](assets/steps/01-empty.png)

Voici notre graphe, avant toute coupe. Il a cinq cellules, donc les côtés auront deux cellules et trois cellules. Chaque méthode donne deux nombres : la taille de coupe et l'équilibre. Construisons une première partition de trois façons différentes.

## Slide 6 — Aléatoire, graine 5 : ABC|DE, coupe 3

![Aléatoire, graine 5 : ABC|DE, coupe 3](assets/steps/02-random-lucky.png)

La méthode un est l'aléatoire. Écrivez les cinq noms sur des cartes, mélangez-les, et donnez deux cartes à un côté. Les trois autres cartes vont de l'autre côté. Un ordinateur mélange à l'aide d'un nombre appelé la graine. La même graine donne toujours le même mélange. Avec la graine cinq, D et E tombent ensemble. Seules C–D et C–E sont coupées, donc la taille de coupe est trois. C'est la meilleure partition de ce graphe, trouvée par pure chance.

## Slide 7 — Glouton : ABC|DE, coupe 3

![Glouton : ABC|DE, coupe 3](assets/steps/03-greedy.png)

La méthode deux est la méthode gloutonne : à chaque étape, elle prend ce qui paraît le meilleur sur le moment. Elle commence par mettre les deux bouts de l'arête la plus lourde du même côté. A–B et D–E pèsent cinq toutes les deux, donc une règle fixe choisit le plus petit nom : A–B. D démarre l'autre côté : il n'a aucun fil vers A ou B, et il vient avant E. C rejoint A et B, avec cinq fils de ce côté contre deux vers D. Enfin E rejoint D, ce qui ne coupe que l'arête de poids un vers C. La taille de coupe est trois.

## Slide 8 — Croissance depuis D : ABC|DE, coupe 3

![Croissance depuis D : ABC|DE, coupe 3](assets/steps/04-grow-d.png)

La méthode trois est la croissance. Choisissez un nœud de départ, et faites grandir un côté autour de lui, comme une goutte d'encre qui s'étale sur le papier. À chaque étape, ajoutez le nœud au bout de l'arête la plus lourde qui sort du côté. Partons de D. L'arête la plus lourde qui sort de D va vers E, avec un poids de cinq. Le côté contient alors deux cellules sur cinq, ce qui suffit, donc il s'arrête. A, B et C forment l'autre côté, et la taille de coupe vaut encore trois.

## Slide 9 — Essayer plusieurs départs, garder le meilleur

![Essayer plusieurs départs, garder le meilleur](assets/steps/05-takeaway.png)

Jusqu'ici, les trois méthodes ont trouvé la même partition. Mais c'était en partie de la chance. D'autres graines et d'autres nœuds de départ donnent des coupes de trois jusqu'à seize. Chacune de ces partitions est valide, donc aucune n'est fausse. C'est pourquoi on construit plusieurs départs, et on garde celui qui a la plus petite coupe.

<!-- /algorithm-walkthrough -->

## Slide 10 — Exemple détaillé : une graine malchanceuse

![Aléatoire, graine 3 : la coupe additionnée arête par arête](assets/worked-unlucky.png)

Voyons maintenant jusqu'où peut aller la malchance. Avec la graine trois, le mélange donne B et D à un côté. A, C et E se retrouvent de l'autre. Additionnons la coupe, arête par arête. A–B cinq, B–C quatre, C–D deux et D–E cinq : seize au total. Les deux arêtes lourdes sont coupées, donc c'est la pire partition valide qui existe. Sur les seize graines essayées, seules trois donnent la meilleure coupe, trois.

## Slide 11 — La croissance dépend du nœud de départ

![Croissance depuis A, étape par étape](assets/grow-a.png)

La croissance n'a pas de hasard, mais elle a un choix : le nœud de départ. Partons de A au lieu de D. L'arête la plus lourde qui sort de A va vers B, avec un poids de cinq, donc B rejoint A. Avec deux cellules, le côté est plein, et il s'arrête. C, D et E forment l'autre côté, donc A–C et B–C sont coupées. Un plus quatre font cinq, ce qui est pire que trois. Partir de C est encore pire : une taille de coupe de neuf.

## Slide 12 — Garder le meilleur départ valide

La solution est simple : ne jamais faire confiance à un seul départ. Construisez-en plusieurs : graines aléatoires, glouton, croissance depuis chaque nœud. Jetez toute partition qui enfreint la règle de taille. Gardez celle dont la coupe est la plus petite. Ici, le glouton et les cinq croissances donnent trois, cinq, cinq, neuf, trois, trois. Le meilleur est trois : A, B et C contre D et E.

```text
best_start(graph):
  starts = random(seed) pour quelques graines
         + greedy
         + grow(x) pour chaque nœud x
  jeter chaque départ qui n'est pas valide
  renvoyer le départ de plus petite taille de coupe
```

## Slide 13 — Une limite de taille garde la partition valide

![Graphe en étoile : l'ancien glouton sans limite de taille, puis le glouton avec la limite](assets/star-cap.png)

Voici une étoile : A est au milieu, relié à toutes les autres cellules. A–B pèse neuf, et les quatre autres arêtes pèsent cinq. Avec six cellules, chaque côté doit en contenir exactement trois. Un ancien glouton sans limite de taille ajoutait toujours des cellules près de A. Il finissait avec cinq cellules contre une : coupe cinq, mais pas valide. Notre glouton arrête chaque côté à trois cellules, et obtient quinze. Aucune partition valide de cette étoile ne fait mieux.

## Slide 14 — Une égalité peut décider du résultat

![Graphe à égalité : l'ancre A–B donne une coupe de neuf, l'ancre D–E une coupe de quatre](assets/tie-graph.png)

Dans ce graphe, A–B et D–E pèsent de nouveau cinq toutes les deux. Le glouton doit en choisir une pour démarrer. La règle prend le plus petit nom, A–B, et cela donne une taille de coupe de neuf. Démarrer de D–E donne une taille de coupe de quatre. Une simple règle de départage a donc plus que doublé la coupe. La croissance depuis C trouve aussi quatre, une raison de plus d'essayer plusieurs départs.

## Slide 15 — Le fil le plus lourd n'est pas toujours à l'intérieur

![Graphe pont : le glouton s'ancre sur le pont, la croissance depuis A garde les deux triangles](assets/bridge-graph.png)

Voici deux triangles, reliés par un seul pont, C–D, de poids quatre. Chaque arête de triangle pèse trois. La coupe naturelle met un triangle de chaque côté, et ne coupe que le pont. Mais le glouton démarre de l'arête la plus lourde, et ici c'est le pont lui-même. C et D commencent donc du même côté, et la coupe finit à douze. La croissance depuis A garde son triangle ensemble et ne coupe que le pont : quatre.

## Slide 16 — Parcours lab dans le navigateur

![Lab dans le navigateur, état de départ](assets/lab-starter.png)

Dans le lab du navigateur, vous travaillez sur le même petit graphe. Vous pouvez déplacer des cellules d'un côté à l'autre, et voir la taille de coupe et l'équilibre changer. Vous pouvez aussi lancer l'aléatoire, le glouton et la croissance, et comparer leurs coupes. Les défis vérifient la partition que vous avez construite, pas le bouton sur lequel vous avez cliqué. Par exemple : trouvez le nœud de départ qui donne la plus petite coupe.

## Slide 17 — Parcours implémentation

![Une vraie session de terminal](assets/real-shell.png)

Si vous aimez programmer, écrivez les trois méthodes en Python. Le fichier d'exemples donne les règles exactes, y compris la façon de départager les égalités. D'abord, lancez le vérificateur pour afficher toutes les bonnes réponses. Ensuite écrivez vos propres fonctions, et lancez le vérificateur sur votre fichier. Il passe aussi le graphe à l'envers, donc une règle de départage manquante se voit comme un échec.

```bash
# afficher toutes les bonnes réponses
python3 examples/initial_bipartition_check.py --show

# vérifier vos propres fonctions
python3 examples/initial_bipartition_check.py --impl my_init.py
```

## Slide 18 — Pièges à éviter

Attention à quatre erreurs courantes. Donner la taille de coupe sans l'équilibre. Laisser un côté dépasser sa limite, ce qui embellit la coupe. Se fier à une seule graine : ici, la coupe va de trois à seize. Et départager selon l'ordre de l'entrée : la réponse change avec le fichier.

## Slide 19 — Bilan : trois façons de démarrer

Des méthodes comme KL et FM ont besoin d'une première partition valide. L'aléatoire mélange et distribue : c'est rapide, mais cela dépend de la chance. Le glouton garde l'arête la plus lourde dedans, puis coupe le moins possible. La croissance s'étend depuis un nœud de départ, donc le nœud de départ compte. Les égalités et les limites de taille peuvent changer la réponse. Construisez plusieurs départs, gardez les valides, choisissez la plus petite coupe.

## Slide 20 — À vous de jouer

C'est maintenant à vous. Choisissez un parcours : le lab dans le navigateur, le parcours Python, ou les deux. Cochez chaque case de la liste de contrôle au fur et à mesure. Puis faites le court quiz pour vérifier les idées principales. La suite, c'est Kernighan–Lin, qui part de votre partition et l'améliore.
