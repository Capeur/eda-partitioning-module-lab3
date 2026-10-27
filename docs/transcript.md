# Initial bipartition

**Module id:** module01-03-initial-bipartition
**Lab:** initial-bipartition
**Tracks:** A (implement) · B (browser lab)

## Slide 1 — Initial bipartition

Before a computer can improve how a chip is split, it needs a first split, called the initial bipartition. You will meet three ways to build one: random, greedy and grow. On one small graph, they give cuts from three to sixteen. The habit that fixes it: try several starts, keep the best.

## Slide 2 — From a chip to a graph

![Cells joined by wires on a chip](assets/chip-to-graph-1.png)

A chip is made of small building blocks called cells, joined by wires. Our example has five cells, named A to E. Some pairs share many wires, others only one.

## Slide 3 — Cells become dots, wires become lines

![The same cells and wires drawn as a graph](assets/chip-to-graph.png)

We draw each cell as a dot, called a node. A line between two nodes is an edge. Its number, the weight, counts the wires between the pair. A–B and D–E are the heaviest, with five wires each.

## Slide 4 — Two numbers: cut and balance

![A split with cut three](assets/cut-and-balance-1.png)

Splitting the cells into two sides is called a bipartition. Edges that cross between the two sides are cut, and drawn in red. The cutsize adds up their weights: here, two plus one makes three.

## Slide 5 — Balance: no side too big

![A split with cut three that is legal, and everything on one side with cut zero that is not](assets/cut-and-balance.png)

Putting every cell on one side gives a cut of zero, but that split is useless. So we also check balance: how many cells each side holds. A split is legal when no side holds more than three of the five.

## Slide 6 — Why a starting split?

Labs four and five teach two famous methods, called KL and FM. They improve a split by moving cells from one side to the other. But KL and FM need a legal split to start from. Think of picking two teams: first any two teams, then swaps to make the game fair. A good first split leaves less swapping to do. Pause and guess: could a split made at random be as good as this one, with cut three?

<!-- algorithm-walkthrough -->

## Slide 7 — Three ways to build a first split

![Three ways to build a first split](assets/steps/01-empty.png)

Three short recipes can build a first split: random, greedy and grow. And yes, a random split can reach cut three, if it is lucky. Every recipe puts two cells on one side, and three on the other.

## Slide 8 — Random seed 5: lucky ABC|DE cut 3

![Random seed 5: lucky ABC|DE cut 3](assets/steps/02-random-lucky.png)

Recipe one is random. Shuffle the five names like cards, and deal two of them to one side. A number called the seed fixes the shuffle, so the same seed always gives the same split. Seed five deals D and E together. Only C–D and C–E are cut: three.

## Slide 9 — Greedy: ABC|DE cut 3

![Greedy: ABC|DE cut 3](assets/steps/03-greedy.png)

Recipe two is greedy: at each step, it takes what looks best right now. It keeps the heaviest edge, A–B, inside one side. D, which has no wire to A or B, starts the other side. Each other cell joins the side where it cuts less. The cut is three again.

## Slide 10 — Grow from D: ABC|DE cut 3

![Grow from D: ABC|DE cut 3](assets/steps/04-grow-d.png)

Recipe three is grow: a side spreads from one start node, like a drop of ink on paper. Start from D. The heaviest edge leaving D goes to E, so E joins. Two cells are enough, so the side stops. A, B and C form the other side: cut three again.

## Slide 11 — All three found cut 3. Was that luck?

![All three found cut 3. Was that luck?](assets/steps/05-takeaway.png)

All three found cut three. Pause and guess: was that luck?

<!-- /algorithm-walkthrough -->

## Slide 12 — Worked example: an unlucky seed

![Random seed 3: B and D on one side, A, C and E on the other](assets/worked-unlucky-1.png)

A single unlucky shuffle can make the cut more than five times worse. So yes, it was partly luck. With seed three, B and D land on one side, and A, C and E on the other.

## Slide 13 — Adding up the cut

![Random seed 3: the cut edges added up](assets/worked-unlucky-2.png)

Let's add up the cut, edge by edge. A–B five, B–C four, C–D two, and D–E five. That makes sixteen.

## Slide 14 — The worst legal split

![Random seed 3: legal, but the worst start](assets/worked-unlucky.png)

Both heavy edges are cut, so this is the worst legal split of all. Over sixteen seeds, the cut goes from three to sixteen. Only three of those seeds hit the best cut, three.

## Slide 15 — Grow depends on the start node

![Grow from A, step 1: the side starts with A](assets/grow-a-1.png)

Grow has no luck in it, but it has a choice: the start node. Let's start from A instead of D.

## Slide 16 — Grow from A, step by step

![Grow from A, step 2: B joins, the side is full](assets/grow-a-2.png)

The heaviest edge leaving A goes to B, with weight five, so B joins A. With two cells, the side is full, and it stops.

## Slide 17 — Grow from A: AB|CDE cut 5

![Grow from A: the cut adds up to five](assets/grow-a.png)

C, D and E form the other side, so A–C and B–C are cut. One plus four makes five, which is worse than three. Starting from C is even worse: a cut of nine.

## Slide 18 — Keep the best legal start

The fix is simple: try several starts, keep the best. Build a few random seeds, greedy, and grow from every node. Drop any split that breaks the size rule, then keep the smallest cut. Here, greedy and the five grows give three, five, five, nine, three and three. So the best is three: A, B and C against D and E. Pause and guess: can a smaller cut ever be the worse choice?

```text
best_start(graph):
  starts = random(seed) for a few seeds
         + greedy
         + grow(x) for every node x
  drop every start that is not legal
  return the start with the smallest cutsize
```

## Slide 19 — Trap 1: no size limit

![Star graph: the old greedy with no size limit](assets/star-cap-1.png)

Three traps can fool a method that looks sensible. And yes, a smaller cut can be the worse choice. Here is a star: A in the middle, wired to five other cells. An older greedy had no size limit, so it kept adding cells next to A. It ended with five cells against one, and a cut of five.

## Slide 20 — Trap 1: the size limit fixes it

![Star graph: the old greedy with no size limit, then greedy with the limit](assets/star-cap.png)

With six cells, each side must hold exactly three, so that split is not legal. Our greedy stops each side at three cells, and gets fifteen. No legal split of this star does better.

## Slide 21 — Trap 2: a tie can decide the answer

![Tie graph: anchor A–B gives cut nine](assets/tie-graph-1.png)

In this graph, A–B and D–E both weigh five. Greedy must pick one of them to start from. The rule picks the smaller name, A–B, and that gives a cut of nine.

## Slide 22 — Trap 2: the other anchor

![Tie graph: anchor A–B gives cut nine, anchor D–E gives cut four](assets/tie-graph.png)

Starting from D–E instead gives a cut of four. So a tie rule more than doubled the cut. Grow from C also finds four.

## Slide 23 — Trap 3: the heaviest wire is not always inside

![Bridge graph: greedy anchors the bridge](assets/bridge-graph-1.png)

Here are two triangles, joined by one bridge, C–D, with weight four. Every triangle edge weighs three. Greedy starts from the heaviest edge, which is the bridge itself. So C and D begin on the same side, and the cut ends at twelve.

## Slide 24 — Trap 3: grow keeps the triangles

![Bridge graph: greedy anchors the bridge, grow from A keeps both triangles](assets/bridge-graph.png)

Grow from A keeps its triangle together, and cuts only the bridge: four. Pause and guess: is grow always better than greedy?

## Slide 25 — Browser lab track

![Browser lab starter](assets/lab-starter.png)

Now you get to build the splits yourself. And no, grow is not always better: on our first graph, greedy found three, and grow from A only five. In the browser lab, you click cells to move them between sides, and watch both numbers change. You can also run random, greedy and grow. The challenges check the split you built, not the button you clicked.

## Slide 26 — Implement track

![Real shell session](assets/real-shell.png)

If you like programming, write the three recipes in Python. The examples file gives the exact rules, ties included. Run the checker once to print every correct answer. Then run it on your own file. It also feeds the graph in reverse order, so a missing tie rule shows up as a failure.

```bash
# print every correct answer
python3 examples/initial_bipartition_check.py --show

# check your own functions
python3 examples/initial_bipartition_check.py --impl my_init.py
```

## Slide 27 — Remember

Random is fast, but it depends on luck. Greedy keeps heavy edges inside, but ties and bridges can fool it. Grow depends on its start node. Report the balance with every cut, and never let a side pass its limit. Break ties by name, not by the order of the input file. So try several starts, keep the best legal one.

## Slide 28 — Your turn

Pick a track: the browser lab, Python, or both. Tick each box of the checklist, then take the short quiz. Next comes Kernighan–Lin, which starts from your split and makes it better. Pause and guess: how much can it shrink the unlucky cut of sixteen? Lab four will show you.
