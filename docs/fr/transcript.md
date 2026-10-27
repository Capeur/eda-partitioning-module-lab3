# Bipartition initiale

**Module id:** module01-03-initial-bipartition
**Lab:** initial-bipartition
**Tracks:** A (implémentation) · B (lab dans le navigateur)

## Slide 1 — Bipartition initiale

Avant d'améliorer une coupe, il faut une première coupe, appelée la bipartition initiale. Vous allez découvrir trois façons de la construire : aléatoire, gloutonne et par croissance. Sur un même petit graphe, elles donnent des coupes de trois à seize. La bonne habitude qui règle ça : essayer plusieurs départs, garder le meilleur.

## Slide 2 — D'une puce à un graphe

![Des cellules reliées par des fils sur une puce](assets/chip-to-graph-1.png)

Une puce est faite de petites briques appelées cellules, reliées par des fils. Notre exemple a cinq cellules, nommées de A à E. Certaines paires partagent beaucoup de fils, d'autres un seul.

## Slide 3 — Les cellules deviennent des points, les fils des traits

![Les mêmes cellules et les mêmes fils dessinés en graphe](assets/chip-to-graph.png)

On dessine chaque cellule comme un point, appelé nœud. Un trait entre deux nœuds est une arête. Son nombre, le poids, compte les fils entre les deux cellules. A–B et D–E sont les plus lourdes, avec cinq fils chacune.

## Slide 4 — Deux nombres : coupe et équilibre

![Une partition de coupe trois](assets/cut-and-balance-1.png)

Couper les cellules en deux côtés s'appelle une bipartition. Les arêtes qui passent d'un côté à l'autre sont coupées, et dessinées en rouge. La taille de coupe additionne leurs poids : ici, deux plus un font trois.

## Slide 5 — L'équilibre : aucun côté trop gros

![Une partition valide de coupe trois, et tout du même côté avec une coupe de zéro, qui n'est pas valide](assets/cut-and-balance.png)

Tout mettre du même côté donne une coupe de zéro, mais cela ne sert à rien. On vérifie donc aussi l'équilibre : combien de cellules chaque côté contient. Une partition est valide quand aucun côté ne dépasse trois cellules sur cinq.

## Slide 6 — Pourquoi une partition de départ ?

Les labs quatre et cinq enseignent deux méthodes célèbres, appelées KL et FM. Elles améliorent une partition en déplaçant des cellules d'un côté à l'autre. Mais KL et FM ont besoin d'une partition valide pour démarrer. Pensez à former deux équipes : d'abord deux équipes au hasard, puis des échanges. Un bon premier découpage laisse moins d'échanges à faire. Faites une pause et devinez : le hasard peut-il aussi trouver une coupe de trois ?

<!-- algorithm-walkthrough -->

## Slide 7 — Trois façons de construire une première partition

![Trois façons de construire une première partition](assets/steps/01-empty.png)

Trois recettes courtes peuvent construire une première partition : aléatoire, gloutonne et par croissance. Et oui, une partition au hasard peut atteindre une coupe de trois, avec de la chance. Chaque recette met deux cellules d'un côté, et trois de l'autre.

## Slide 8 — Aléatoire, graine 5 : ABC|DE, coupe 3

![Aléatoire, graine 5 : ABC|DE, coupe 3](assets/steps/02-random-lucky.png)

La recette un est l'aléatoire. Mélangez les cinq noms comme des cartes, et donnez-en deux à un côté. Un nombre appelé la graine fixe le mélange : la même graine donne toujours la même partition. La graine cinq met D et E ensemble. Seules C–D et C–E sont coupées : trois.

## Slide 9 — Glouton : ABC|DE, coupe 3

![Glouton : ABC|DE, coupe 3](assets/steps/03-greedy.png)

La recette deux est gloutonne : à chaque étape, elle prend ce qui paraît le meilleur sur le moment. Elle garde l'arête la plus lourde, A–B, d'un seul côté. D, qui n'a aucun fil vers A ou B, démarre l'autre côté. Chaque autre cellule rejoint le côté où elle coupe le moins. La coupe vaut encore trois.

## Slide 10 — Croissance depuis D : ABC|DE, coupe 3

![Croissance depuis D : ABC|DE, coupe 3](assets/steps/04-grow-d.png)

La recette trois est la croissance : un côté s'étend depuis un nœud de départ, comme une goutte d'encre sur le papier. Partons de D. L'arête la plus lourde qui sort de D va vers E, donc E le rejoint. Deux cellules suffisent, donc le côté s'arrête. A, B et C forment l'autre côté : encore une coupe de trois.

## Slide 11 — Les trois trouvent une coupe de 3. Coup de chance ?

![Les trois trouvent une coupe de 3. Coup de chance ?](assets/steps/05-takeaway.png)

Les trois méthodes trouvent une coupe de trois. Faites une pause et devinez : était-ce de la chance ?

<!-- /algorithm-walkthrough -->

## Slide 12 — Exemple détaillé : une graine malchanceuse

![Aléatoire, graine 3 : B et D d'un côté, A, C et E de l'autre](assets/worked-unlucky-1.png)

Un seul mélange malchanceux peut rendre la coupe plus de cinq fois pire. Donc oui, c'était en partie de la chance. Avec la graine trois, B et D tombent d'un côté, et A, C et E de l'autre.

## Slide 13 — Additionner la coupe

![Aléatoire, graine 3 : les arêtes coupées additionnées](assets/worked-unlucky-2.png)

Additionnons la coupe, arête par arête. A–B cinq, B–C quatre, C–D deux, et D–E cinq. Cela fait seize.

## Slide 14 — La pire partition valide

![Aléatoire, graine 3 : valide, mais le pire départ](assets/worked-unlucky.png)

Les deux arêtes lourdes sont coupées : c'est la pire partition valide qui existe. Sur seize graines, la coupe va de trois à seize. Seules trois de ces graines trouvent la meilleure coupe, trois.

## Slide 15 — La croissance dépend du nœud de départ

![Croissance depuis A, étape 1 : le côté démarre avec A](assets/grow-a-1.png)

La croissance n'a pas de hasard, mais elle a un choix : le nœud de départ. Partons de A au lieu de D.

## Slide 16 — Croissance depuis A, étape par étape

![Croissance depuis A, étape 2 : B le rejoint, le côté est plein](assets/grow-a-2.png)

L'arête la plus lourde qui sort de A va vers B, avec un poids de cinq, donc B rejoint A. Avec deux cellules, le côté est plein, et il s'arrête.

## Slide 17 — Croissance depuis A : AB|CDE, coupe 5

![Croissance depuis A : la coupe fait cinq](assets/grow-a.png)

C, D et E forment l'autre côté, donc A–C et B–C sont coupées. Un plus quatre font cinq, ce qui est pire que trois. Partir de C est encore pire : une coupe de neuf.

## Slide 18 — Garder le meilleur départ valide

La solution est simple : essayer plusieurs départs, garder le meilleur. Construisez quelques graines aléatoires, le glouton, et la croissance depuis chaque nœud. Jetez toute partition qui enfreint la règle de taille, puis gardez la plus petite coupe. Ici, le glouton et les cinq croissances donnent trois, cinq, cinq, neuf, trois et trois. Le meilleur est donc trois : A, B et C contre D et E. Faites une pause et devinez : une coupe plus petite peut-elle être le mauvais choix ?

```text
best_start(graph):
  starts = random(seed) pour quelques graines
         + greedy
         + grow(x) pour chaque nœud x
  jeter chaque départ qui n'est pas valide
  renvoyer le départ de plus petite taille de coupe
```

## Slide 19 — Piège 1 : pas de limite de taille

![Graphe en étoile : l'ancien glouton sans limite de taille](assets/star-cap-1.png)

Trois pièges peuvent tromper une méthode qui a l'air raisonnable. Et oui, une coupe plus petite peut être le mauvais choix. Voici une étoile : A au milieu, relié à cinq autres cellules. Un ancien glouton sans limite de taille ajoutait toujours des cellules près de A. Il finissait avec cinq cellules contre une, et une coupe de cinq.

## Slide 20 — Piège 1 : la limite de taille règle le problème

![Graphe en étoile : l'ancien glouton sans limite de taille, puis le glouton avec la limite](assets/star-cap.png)

Avec six cellules, il en faut trois par côté, donc cette partition n'est pas valide. Notre glouton arrête chaque côté à trois cellules, et obtient quinze. Aucune partition valide de cette étoile ne fait mieux.

## Slide 21 — Piège 2 : une égalité peut décider du résultat

![Graphe à égalité : l'ancre A–B donne une coupe de neuf](assets/tie-graph-1.png)

Dans ce graphe, A–B et D–E pèsent cinq toutes les deux. Le glouton doit en choisir une pour démarrer. La règle prend le plus petit nom, A–B, et cela donne une coupe de neuf.

## Slide 22 — Piège 2 : l'autre ancre

![Graphe à égalité : l'ancre A–B donne une coupe de neuf, l'ancre D–E une coupe de quatre](assets/tie-graph.png)

Démarrer de D–E donne une coupe de quatre. Une simple règle de départage a donc plus que doublé la coupe. La croissance depuis C trouve aussi quatre.

## Slide 23 — Piège 3 : le fil le plus lourd n'est pas toujours à l'intérieur

![Graphe pont : le glouton s'ancre sur le pont](assets/bridge-graph-1.png)

Voici deux triangles, reliés par un seul pont, C–D, de poids quatre. Chaque arête de triangle pèse trois. Le glouton démarre de l'arête la plus lourde, qui est ici le pont lui-même. C et D commencent donc du même côté, et la coupe finit à douze.

## Slide 24 — Piège 3 : la croissance garde les triangles

![Graphe pont : le glouton s'ancre sur le pont, la croissance depuis A garde les deux triangles](assets/bridge-graph.png)

La croissance depuis A garde son triangle ensemble, et ne coupe que le pont : quatre. Faites une pause et devinez : la croissance est-elle toujours meilleure que le glouton ?

## Slide 25 — Parcours lab dans le navigateur

![Lab dans le navigateur, état de départ](assets/lab-starter.png)

À vous maintenant de construire les partitions. Et non, la croissance n'est pas toujours meilleure : sur notre premier graphe, le glouton trouvait trois, et la croissance depuis A seulement cinq. Dans le lab du navigateur, vous cliquez sur les cellules pour les changer de côté, et vous voyez les deux nombres changer. Vous pouvez aussi lancer l'aléatoire, le glouton et la croissance. Les défis vérifient la partition que vous avez construite, pas le bouton sur lequel vous avez cliqué.

## Slide 26 — Parcours implémentation

![Une vraie session de terminal](assets/real-shell.png)

Si vous aimez programmer, écrivez les trois recettes en Python. Le fichier d'exemples donne les règles exactes, égalités comprises. Lancez d'abord le vérificateur pour afficher toutes les bonnes réponses. Puis lancez-le sur votre propre fichier. Il passe aussi le graphe à l'envers, donc une règle de départage manquante se voit comme un échec.

```bash
# afficher toutes les bonnes réponses
python3 examples/initial_bipartition_check.py --show

# vérifier vos propres fonctions
python3 examples/initial_bipartition_check.py --impl my_init.py
```

## Slide 27 — À retenir

L'aléatoire est rapide, mais il dépend de la chance. Le glouton garde les arêtes lourdes dedans, mais égalités et ponts le trompent. La croissance dépend de son nœud de départ. Donnez l'équilibre avec chaque coupe, et ne laissez aucun côté dépasser sa limite. Départagez par le nom, pas par l'ordre du fichier d'entrée. Donc : essayer plusieurs départs, garder le meilleur départ valide.

## Slide 28 — À vous de jouer

Choisissez un parcours : le lab dans le navigateur, Python, ou les deux. Cochez chaque case de la liste de contrôle, puis faites le court quiz. La suite, c'est Kernighan–Lin, qui part de votre partition et l'améliore. Faites une pause et devinez : de combien peut-il réduire la coupe malchanceuse de seize ? Le lab quatre vous le montrera.
