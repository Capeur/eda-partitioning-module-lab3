# Initial bipartition

**Module id:** module01-03-initial-bipartition
**Lab:** initial-bipartition
**Tracks:** A (implement) · B (browser lab)

## Slide 1 — Initial bipartition

Before a computer can improve how a chip is split, it needs a first split. That first split is called the initial bipartition. You will meet three ways to build one: random, greedy and grow. You will see the same small graph get a cut of three, or a cut of sixteen. And you will learn the simple habit that fixes it: try several starts, and keep the best.

## Slide 2 — From a chip to a graph

![Cells and wires on a chip, then the same thing drawn as a graph](assets/chip-to-graph.png)

A chip is made of small building blocks called cells, joined by wires. We draw each cell as a dot, called a node. A line between two nodes is an edge: it means the two cells are wired together. The number on an edge is its weight: how many wires join the pair. Our example has five cells, A to E. The heaviest edges, A–B and D–E, have five wires each.

## Slide 3 — Two numbers: cut and balance

![A split with cut three that is legal, and everything on one side with cut zero that is not](assets/cut-and-balance.png)

Splitting a chip into two sides is called a bipartition. Edges that cross between the two sides are cut, and they are drawn in red. The cutsize adds up their weights: here, two plus one makes three. Putting every cell on one side gives a cut of zero, but that split is useless. So we also check balance: how many cells each side holds. A split is legal when no side holds more than three of the five cells.

## Slide 4 — Why a starting split?

Labs four and five teach two famous methods, called KL and FM. They improve a split by moving cells from one side to the other. But they can only improve: they need a legal split to start from. Think of picking two teams for a game. First you need any two teams, then you swap players to make the game fair. A good first split leaves less swapping to do.

<!-- algorithm-walkthrough -->

## Slide 5 — Need a legal starting split

![Need a legal starting split](assets/steps/01-empty.png)

Here is our graph again, before any split. It has five cells, so the sides will hold two cells and three cells. Every method reports two numbers: the cutsize and the balance. Let's build a first split in three different ways.

## Slide 6 — Random seed 5: lucky ABC|DE cut 3

![Random seed 5: lucky ABC|DE cut 3](assets/steps/02-random-lucky.png)

Method one is random. Write the five names on cards, shuffle them, and deal two cards to one side. The other three cards go to the other side. A computer shuffles using a number called the seed. The same seed always gives the same shuffle. With seed five, D and E land together. Only C–D and C–E are cut, so the cutsize is three. That is the best split this graph has, found by pure luck.

## Slide 7 — Greedy: ABC|DE cut 3

![Greedy: ABC|DE cut 3](assets/steps/03-greedy.png)

Method two is greedy: at each step, it takes what looks best right now. It starts by putting both ends of the heaviest edge on one side. A–B and D–E both weigh five, so a fixed rule picks the smaller name: A–B. D starts the other side: it has no wire to A or B, and it comes before E. C joins A and B, with five wires there against two to D. Last, E joins D, which cuts only the edge of weight one to C. The cutsize is three.

## Slide 8 — Grow from D: ABC|DE cut 3

![Grow from D: ABC|DE cut 3](assets/steps/04-grow-d.png)

Method three is grow. Pick a start node, and grow a side around it, like a drop of ink spreading on paper. At each step, add the node behind the heaviest edge that leaves the side. Start from D. The heaviest edge out of D goes to E, with weight five. Now the side holds two of the five cells, which is enough, so it stops. A, B and C form the other side, and the cutsize is three again.

## Slide 9 — Try several starts, keep the best

![Try several starts, keep the best](assets/steps/05-takeaway.png)

So far, all three methods found the same split. But that was partly luck. Other seeds and other start nodes give cuts from three up to sixteen. Each of those splits is legal, so none of them is wrong. That is why we build several starts, and keep the one with the smallest cut.

<!-- /algorithm-walkthrough -->

## Slide 10 — Worked example: an unlucky seed

![Random seed 3: the cut added up edge by edge](assets/worked-unlucky.png)

Now let's see how bad luck can get. With seed three, the shuffle deals B and D to one side. A, C and E end up on the other side. Let's add up the cut, edge by edge. A–B five, B–C four, C–D two and D–E five: sixteen in total. Both heavy edges are cut, so this is the worst legal split of all. Out of the sixteen seeds we tried, only three give the best cut of three.

## Slide 11 — Grow depends on the start node

![Grow from A, step by step](assets/grow-a.png)

Grow has no luck in it, but it has a choice: the start node. Start from A instead of D. The heaviest edge out of A goes to B, with weight five, so B joins A. With two cells, the side is full, and it stops. Now C, D and E form the other side, so A–C and B–C are cut. One plus four makes five, which is worse than three. Starting from C is even worse: a cutsize of nine.

## Slide 12 — Keep the best legal start

The fix is simple: never trust a single start. Build several: a few random seeds, greedy, and grow from every node. Throw away any split that breaks the size rule. Keep the one with the smallest cut. On our graph, greedy and the five grows give three, five, five, nine, three and three. The best is three: A, B and C against D and E.

```text
best_start(graph):
  starts = random(seed) for a few seeds
         + greedy
         + grow(x) for every node x
  drop every start that is not legal
  return the start with the smallest cutsize
```

## Slide 13 — A size limit keeps the split legal

![Star graph: the old greedy with no size limit, then greedy with the limit](assets/star-cap.png)

Here is a star: A sits in the middle, wired to every other cell. A–B weighs nine, and the four other edges weigh five. With six cells, each side must hold exactly three. An older greedy had no size limit, so it kept adding cells next to A. It ended with five cells against one: cutsize five, but not legal. Our greedy stops each side at three cells, and gets fifteen. No legal split of this star does better.

## Slide 14 — A tie can decide the answer

![Tie graph: anchor A–B gives cut nine, anchor D–E gives cut four](assets/tie-graph.png)

In this graph, A–B and D–E both weigh five again. Greedy must pick one of them to start from. The rule picks the smaller name, A–B, and that gives a cutsize of nine. Starting from D–E instead gives a cutsize of four. So a simple tie rule more than doubled the cut. Grow from C also finds four, which is one more reason to try several starts.

## Slide 15 — The heaviest wire is not always inside

![Bridge graph: greedy anchors the bridge, grow from A keeps both triangles](assets/bridge-graph.png)

Here are two triangles, joined by one bridge, C–D, with weight four. Every triangle edge weighs three. The natural split puts one triangle on each side, and cuts only the bridge. But greedy starts from the heaviest edge, and here that is the bridge itself. So C and D begin on the same side, and the cut ends up at twelve. Grow from A keeps its triangle together, and cuts only the bridge: four.

## Slide 16 — Browser lab track

![Browser lab starter](assets/lab-starter.png)

In the browser lab, you work on the same small graph. You can move cells from one side to the other, and watch the cutsize and the balance change. You can also run random, greedy and grow, and compare their cuts. The challenges check the split you built, not the button you clicked. For example, find the start node that gives the smallest cut.

## Slide 17 — Implement track

![Real shell session](assets/real-shell.png)

If you like programming, write the three methods in Python. The examples file gives the exact rules, including how to break ties. First, run the checker to print every correct answer. Then write your own functions, and run the checker on your file. It also feeds the graph in reverse order, so a missing tie rule shows up as a failure.

```bash
# print every correct answer
python3 examples/initial_bipartition_check.py --show

# check your own functions
python3 examples/initial_bipartition_check.py --impl my_init.py
```

## Slide 18 — Pitfalls to watch

Watch out for four common mistakes. Reporting the cutsize without the balance. Letting one side grow past its limit, which makes the cut look better than it really is. Trusting a single random seed: on our graph, the cut ranged from three to sixteen. And breaking ties by the order of the input, so the answer changes when the file changes.

## Slide 19 — Recap: three ways to start

Methods like KL and FM need a legal first split. Random shuffles and deals: it is fast, but it depends on luck. Greedy keeps the heaviest edge inside, then puts each cell where it cuts less. Grow spreads from a start node, so the start node matters. Ties and size limits can change the answer. So build several starts, keep only the legal ones, and pick the smallest cut.

## Slide 20 — Your turn

Now it's your turn. Pick a track: the browser lab, the Python track, or both. Tick each box of the checklist as you go. Then take the short quiz to check the main ideas. Next comes Kernighan–Lin, which starts from your split and makes it better.
