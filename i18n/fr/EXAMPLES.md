# Exemples — Bipartition initiale

Parcours A (implémentation). Les graphes sont dans `examples/`, la clé de correction est `examples/initial_bipartition_check.py`.
Tous les nombres ci-dessous ont été affichés par ce vérificateur (`python3 examples/initial_bipartition_check.py --show`).
Lancez-le depuis le dossier du module ; il n'a besoin que de la bibliothèque standard de Python.

## Objectif

Les algorithmes de raffinement (Kernighan–Lin au Lab 04, Fiduccia–Mattheyses au Lab 05) ne font qu'*améliorer* une
partition. Il leur faut d'abord une **partition de départ valide**. Construisez trois sortes de départ, indiquez la
**taille de coupe et l'équilibre** de chacune, et observez à quel point le départ change le résultat.

## Définitions

- **Partition** : chaque nœud est sur exactement un de deux côtés, appelés `"0"` et `"1"`. `AB|CDE` veut dire A, B d'un
  côté et C, D, E de l'autre. Échanger les étiquettes donne la même partition.
- **Taille de coupe** (cutsize) : poids total des arêtes dont les deux extrémités sont de part et d'autre.
- **Équilibre** (balance) : tailles des deux côtés. Ici chaque nœud a une taille de 1, donc les tailles sont des nombres
  de nœuds. `ratio` = petit côté / grand côté, `imbalance` (déséquilibre) = |différence| / total (les deux viennent de
  `balance_metrics` dans `common/graphutil.py`).
- **Départ valide** : les deux côtés sont non vides et **aucun côté n'est plus grand que ceil(n / 2)**. Pour 5 nœuds,
  les côtés peuvent être 2|3 (pas 1|4, pas 0|5). Pour 6 nœuds, seul 3|3 est valide.
- **cap** = ceil(n / 2) nœuds par côté. **half** = floor(n / 2) nœuds.

Pourquoi cette limite : mettre tous les nœuds du même côté donne une taille de coupe de 0, ce qui a l'air parfait et ne
sert à rien. Une coupe n'a de valeur que si on la compare entre des partitions valides.

## API (ce que cherche `--impl`)

`nodes` est une liste de noms, `edges` une liste de tuples `(u, v, w)` avec `u < v`. Chaque fonction renvoie
`{node: "0" | "1"}`. Vos fonctions peuvent recevoir les nœuds et les arêtes dans n'importe quel ordre ; la réponse ne
doit pas en dépendre.

```python
random_bipartition(nodes, seed)        # mélange avec graine, distribue la moitié
greedy_bipartition(nodes, edges)       # s'ancre sur l'arête la plus lourde
grow_bipartition(nodes, edges, start)  # s'étend depuis un nœud
is_legal(nodes, assignment)            # True quand la partition est valide
```

Vous pouvez copier `mulberry32` depuis le vérificateur. Le `random` de Python et le `Math.random` de JavaScript ne
donnent jamais les mêmes nombres : le vérificateur et le lab dans le navigateur partagent donc ce petit générateur.

## Pseudo-code

### Départ aléatoire

```text
random(seed):
  order = les nœuds triés par nom
  rng = mulberry32(seed) ; jeter ses deux premiers nombres
  pour i = n-1 jusqu'à 1 :
      j = floor(rng() * (i + 1))
      échanger order[i] et order[j]
  côté 0 = les floor(n/2) premiers nœuds de order, côté 1 = le reste
```

Pourquoi jeter deux nombres : les premières sorties des petites graines se ressemblent. Sans cela, les graines 0, 1, 2, 3
donneraient la même partition sur le petit graphe.

### Départ glouton (règle exacte)

```text
greedy:
  cap = ceil(n/2)
  1. ancre = l'arête la plus lourde. Égalité : plus petit (u, v). Ses deux extrémités vont au côté 0.
  2. graine du côté 1 = le nœud non placé dont le poids total vers les nœuds placés est le plus petit.
     Égalité : plus petit nom. Il va au côté 1.
  3. tant qu'il reste des nœuds :
       x = le nœud non placé dont le poids total vers les nœuds placés est le plus grand. Égalité : plus petit nom.
       cout0 = poids de x vers le côté 1   (coupe ajoutée si x rejoint le côté 0)
       cout1 = poids de x vers le côté 0   (coupe ajoutée si x rejoint le côté 1)
       seul un côté qui a moins de cap nœuds peut être choisi
       mettre x sur le côté permis le moins cher ; coût égal : côté 0
```

### Départ par croissance (règle exacte)

```text
grow(start):
  half = floor(n/2)
  grown = [start]
  tant que len(grown) < half :
      ajouter le nœud hors de grown atteint par l'arête unique la plus lourde qui sort de grown
      Égalité : plus petit nom. Si aucune arête ne sort, ajouter le plus petit nom non placé.
  côté 0 = grown, côté 1 = le reste
```

### Essayer plusieurs départs

```text
best_start : construire random(seed) pour quelques graines, greedy, et grow(x) pour chaque nœud x.
Jeter les partitions non valides, garder la plus petite taille de coupe. Égalité : la première construite.
```

## Résultats de référence

### Petit graphe

A–B 5, A–C 1, B–C 4, C–D 2, D–E 5, C–E 1. Poids total 18. Il n'existe que dix partitions valides (2|3 sur 5 nœuds) :

| Partition | Coupe | | Partition | Coupe |
|---|---|---|---|---|
| ABC\|DE | **3** | | AC\|BDE | 12 |
| AB\|CDE | 5 | | AE\|BCD | 12 |
| ADE\|BC | 9 | | AD\|BCE | 13 |
| ABE\|CD | 11 | | ACD\|BE | 15 |
| ABD\|CE | 12 | | ACE\|BD | 16 |

**Aléatoire**, graines de 0 à 15 (côtés toujours 2|3, donc valides) :

| Graine | Partition | Coupe | | Graine | Partition | Coupe |
|---|---|---|---|---|---|---|
| 0 | ABE\|CD | 11 | | 8 | AD\|BCE | 13 |
| 1 | AB\|CDE | 5 | | 9 | ACD\|BE | 15 |
| 2 | AE\|BCD | 12 | | 10 | AC\|BDE | 12 |
| 3 | ACE\|BD | 16 | | 11 | AB\|CDE | 5 |
| 4 | ABD\|CE | 12 | | 12 | ACD\|BE | 15 |
| 5 | ABC\|DE | **3** | | 13 | ADE\|BC | 9 |
| 6 | ABD\|CE | 12 | | 14 | ABC\|DE | **3** |
| 7 | AD\|BCE | 13 | | 15 | ABC\|DE | **3** |

Ce qu'il faut retenir : le même graphe donne des coupes de 3 à 16 selon la seule graine. Les graines 5, 14 et 15 trouvent la
meilleure partition. La meilleure coupe obtenue jusque-là, graine après graine : la graine 0 donne 11, la graine 1 donne 5,
la graine 5 donne 3. Un seul départ aléatoire, c'est de la chance.

**Glouton** :

| Étape | Ce qui se passe | Côtés maintenant |
|---|---|---|
| 1 | Ancre. A–B et D–E pèsent 5 toutes les deux ; le plus petit (u, v) est A–B. | A B \| |
| 2 | Graine du côté 1. Poids vers {A, B} : C 5, D 0, E 0. Le plus petit est D (égalité D, E : par nom). | A B \| D |
| 3 | Prochain x = C (poids 7 vers les nœuds placés). cout0 = 2 (vers D), cout1 = 5 (vers A, B). Côté 0. | A B C \| D |
| 4 | Prochain x = E. cout0 = 5 (vers D), cout1 = 1 (vers C). Le côté 0 est déjà à la limite de 3, donc côté 1 de toute façon. | A B C \| D E |

Résultat : **ABC|DE, coupe 3**, tailles 3|2, ratio 0,67, déséquilibre 0,20.

**Croissance**, depuis chaque nœud de départ (half = 2, donc un seul nœud est ajouté) :

| Départ | Arête la plus lourde qui sort du départ | Partition | Coupe |
|---|---|---|---|
| A | A–B 5, donc on ajoute B | AB\|CDE | 5 |
| B | B–A 5, donc on ajoute A | AB\|CDE | 5 |
| C | C–B 4, donc on ajoute B | ADE\|BC | 9 |
| D | D–E 5, donc on ajoute E | ABC\|DE | **3** |
| E | E–D 5, donc on ajoute D | ABC\|DE | **3** |

Ce qu'il faut retenir : la croissance depuis D prend E (poids 5) et s'arrête, donc A, B, C restent ensemble de l'autre côté et
seuls les fils légers C–D (2) et C–E (1) sont coupés. La croissance depuis C prend B (poids 4) et laisse A seul de l'autre côté :
A–B (5), A–C (1), C–D (2) et C–E (1) sont toutes coupées, soit 9.

**Meilleur de plusieurs départs** (sans aléatoire) : le glouton et les cinq croissances donnent des coupes de 3, 5, 5, 9, 3, 3.
Le meilleur est le glouton avec une coupe de 3, partition ABC|DE.

### Graphe supplémentaire 1 : `star_graph.json` — la limite de taille

A–B 9, et A relié à chacun de C, D, E, F avec un poids de 5. Six nœuds, donc seul 3|3 est valide. Poids total 29.

| Départ | Partition | Tailles | Coupe | Valide ? |
|---|---|---|---|---|
| glouton (avec limite) | ABD\|CEF | 3\|3 | 15 | oui |
| ANCIEN glouton (sans limite) | ABDEF\|C | 5\|1 | 5 | **non** |

Ce qu'il faut retenir : l'ancienne règle continue à poser les nœuds à côté de A, parce que cela n'ajoute aucune coupe. La coupe
paraît trois fois meilleure, mais un côté contient cinq nœuds sur six. Une coupe de 5 ne bat pas une coupe de 15 quand le 5
n'est pas un départ valide. (La coupe la plus basse d'une partition 3|3 est 15, donc le glouton avec limite est optimal ici.)

### Graphe supplémentaire 2 : `tie_graph.json` — une égalité décide du résultat

A–B 5, A–E 3, B–F 3, C–D 1, D–E 5, E–F 1. A–B et D–E pèsent toutes les deux 5.

| Ancre | Partition | Coupe |
|---|---|---|
| A–B (plus petit nom, la règle) | ABE\|CDF | 9 |
| D–E (l'autre égalité) | ABF\|CDE | 4 |

Inverser l'ordre des nœuds et des arêtes que vous passez ne doit pas changer le résultat : la règle dit « plus petit (u, v) », pas
« premier de la liste ». La croissance depuis C ou depuis F trouve aussi ABF|CDE, coupe 4. Meilleur du glouton et des six
croissances : **4**, par la croissance depuis C.

### Graphe supplémentaire 3 : `bridge_graph.json` — le fil le plus lourd n'est pas toujours à l'intérieur

Deux triangles A–B–C et D–E–F, chaque arête de triangle pèse 3, reliés par le pont C–D de poids 4. Poids total 22.

| Départ | Partition | Coupe |
|---|---|---|
| glouton | AEF\|BCD | 12 |
| croissance depuis A ou B | ABC\|DEF | **4** |
| croissance depuis C ou D | ACD\|BEF | 12 |
| croissance depuis E | ABF\|CDE | 12 |
| croissance depuis F | ABE\|CDF | 12 |

Ce qu'il faut retenir : l'arête la plus lourde est le *pont*, donc le glouton s'ancre sur C–D et met un nœud de chaque triangle du
même côté. La croissance depuis C prend aussi D en premier (4 bat 3), puis A (égalité à quatre à 3, plus petit nom), ce qui donne
ACD. La croissance depuis A prend B (A–B et A–C sont à égalité à 3, plus petit nom), puis C, et garde le triangle entier. Meilleur du
glouton et des six croissances : **4**, par la croissance depuis A.

### L'ancien glouton, pour comparer

Le glouton du code partagé des labs avant cette mise à niveau est écrit dans le vérificateur sous le nom `greedy_legacy`. Ce n'est
pas une référence. Il n'avait pas de limite de taille, et il forçait le premier nœud restant par ordre alphabétique (C sur le petit
graphe) du côté 1 sans regarder aucun poids.

| Graphe | ANCIEN glouton | Nouveau glouton |
|---|---|---|
| petit | AB\|CDE, coupe 5 | ABC\|DE, coupe 3 |
| petit, lettres renommées A↔E et B↔D | AB\|CDE, coupe **3** | coupe 3 |
| étoile | ABDEF\|C, tailles 5\|1, coupe 5 (non valide) | ABD\|CEF, tailles 3\|3, coupe 15 |

Le même graphe avec d'autres lettres donnait une autre coupe à l'ancien glouton : son « coupe 5 » dépendait des noms, pas du graphe.
La nouvelle règle ne lit les noms que pour départager.

Les outils de benchmark du Lab 12 utilisent encore l'ancien aléatoire et l'ancien glouton, leurs nombres diffèrent donc de ceux des tableaux ci-dessus.

## À essayer

```bash
python3 examples/initial_bipartition_check.py                    # tout PASS pour la référence
python3 examples/initial_bipartition_check.py --show             # affiche tous les tableaux ci-dessus
python3 examples/initial_bipartition_check.py --impl my_init.py  # vérifie vos propres fonctions
python3 examples/initial_bipartition_check.py --vs-node          # le PRNG et le mélange sont les mêmes que dans le lab (node requis)
```

Commencez par `random_bipartition` (tableau des graines), puis `is_legal`, puis `grow_bipartition`, puis `greedy_bipartition`.
Une fonction que vous n'avez pas encore écrite affiche `SKIP`.

## Questions pour démarrer (demandez pourquoi)

1. Les graines 0 et 5 donnent des coupes de 11 et 3 sur le petit graphe. En une phrase, pourquoi la même méthode peut-elle donner les deux ?
2. La croissance depuis C donne une coupe de 9 et depuis D une coupe de 3. Quelle arête décide de la première étape dans chaque cas ?
3. Sur l'étoile, l'ancien glouton a une coupe plus petite (5) que le nouveau (15). Pourquoi est-ce le nouveau que vous donneriez à Kernighan–Lin ?
4. Sur le graphe à égalité, la coupe vaut 9 avec l'ancre A–B et 4 avec l'ancre D–E. Écrivez une règle de départage qui ne dépend pas des lettres. Votre règle donne-t-elle 4 ?
5. Sur le graphe pont, le glouton obtient 12 et la croissance depuis A obtient 4. Quelle est la faiblesse de « s'ancrer sur l'arête la plus lourde » ?

## Livrables attendus

- La partition, la taille de coupe et les tailles de chaque départ des tableaux ci-dessus, affichées par votre code.
- Une phrase par départ qui explique pourquoi sa coupe est aussi basse ou aussi haute.

## Pour aller plus loin

- Écrivez `best_start` (graines aléatoires 0 à 3, glouton, chaque croissance) : trouve-t-il la coupe 4 sur le graphe à égalité ?
- Faites utiliser à la limite les tailles des nœuds plutôt que leur nombre (donnez une taille de 3 à C et regardez quelles partitions restent valides).
