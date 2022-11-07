
# Router placement

### Problem statement for Final Round, Hash Code 2017


## Introduction

Who doesn't love wireless Internet? Millions of people rely on it for productivity and fun in countless cafes,
railway stations and public areas of all sorts. For many institutions, ensuring wireless Internet access is now
almost as important a feature of building facilities as the access to water and electricity.
Typically, buildings are connected to the Internet using a fiber backbone. In order to provide wireless
Internet access, wireless routers are placed around the building and connected using fiber cables to the
backbone. The larger and more complex the building, the harder it is to pick router locations and decide
how to lay down the connecting cables.

## Task

Given a building plan, decide where to put wireless routers and how to connect them to the fiber backbone
to maximize coverage and minimize cost.

## Problem description

### Building

The building is represented as a rectangular grid of cells of H rows and W columns. The cells within the grid
are referenced using a pair of 0-based coordinates [ _r_ , _c_ ], denoting respectively the row and the column of
the cell. The cell [0,0] is in the upper-left corner of the grid.
**For example** ​, the grid below has 4 rows and 5 columns. The cell marked with “X” is [0, 3].
...X.
.....
.....
.....
Each cell is either:
● a ​ **wall** ​cell, represented as “​#​” in the input file
● a ​ **target** cell, represented as “​.​” in the input file - these are cells in which we need to have wireless
coverage
● a ​ **void** cell, represented as “​-​” in the input file - these are cells in which we don’t need to have
wireless coverage
© Google 2017, All rights reserved.


```
Each cell (except the cells at the edges of the building) has 8 neighboring cells.
For example ​, the cell marked with “X” below has the following neighboring cells:
.....
.​...​.
.​.​X​.​.
.​...​.
.....
```
### Routers

```
Each router covers a square area of at most ( 2 × R + 1 )^2 cells around it with Internet access, unless the
signal is stopped by a wall cell. Concretely, for a router placed at cell [a, b], the cell [x, y] is covered,
provided that:
● | a − x |≤ R , and
● | b − y |≤ R , and
● there is ​ no wall cell inside the smallest enclosing rectangle of [a, b] and [x, y]. That is, there is no
wall cells [w, v] where both min ( a , x )≤ w ≤ max ( a , x ) and min ( b , y )≤ v ≤ max ( b , y ).
For example ​, the signal from a router placed in the cell “S” can cover the cell “X” if there are no wall cells
in the area marked below. (R = 7 in this example)
..........
..​S.......
..​........
..​........
..​.......X
For example ​, if R = 3, the following cells would be covered by a router placed in the cell “S”.
.#...​...​........
.#...​...​#.......
.####​...​#.......
....#​..S...​.....
....#​......​.....
....#​...​#.......
....#​...​#.......
Routers can be placed in target or void cells (routers ​ cannot ​ be placed in wall cells).
```
### Backbone

Routers can be only placed in a cell that is already connected to the fiber backbone (​ _backbone is a cable_
​ _that delivers Internet to the router itself_ ). In the beginning, exactly one cell in the building is connected to the
backbone. The initial backbone cell can be of any type (target, void or wall cell).
© Google 2017, All rights reserved.


```
Cells of any type (target, void or wall cells) can be connected to the backbone. To connect a new cell to the
backbone, one of its eight neighboring cells must already be connected to the backbone.
For example ​, if “b” is the initial cell connected to the backbone, and “r” is a cell where we want to place a
router, one of the possible ways of connecting the router to the backbone is connecting all cells marked
below.
--#..​r​.#
-b​#..​..#
--#....#
```
### Budget

```
Placing a single router costs the price of ​ P ​ r ​. Connecting a single cell to the backbone costs the price of ​ P ​ b ​.
The maximum spend on routers and backbone is ​ B ​.
For example ​, if “b” is the initial cell connected to the backbone, we place a single router in the cell “r” and
we connect the four cells marked below to the backbone, total cost is 1 × Pr + 4 × Pb. This value has to be
lower than or equal to ​ B ​.
--#..​r​.#
-b​#..​..#
--#....#
```
## Input data set

```
The input data is provided as a data set file - a plain text file containing exclusively ASCII characters with a
single “\n” character at the end of each line (UNIX-​style line endings).
```
### File format

All numbers mentioned in the input are natural numbers that fit within the indicated ranges. When multiple
numbers appear in a single line, they are separated by a single space.
The first line contains the following numbers:
​ ● **_H_** ( 1 ≤ _H_ ≤ 1000 )- the number of rows of the grid
​ ● **_W_** ( 1 ≤ _W_ ≤ 1000 ) - the number of columns of the grid
​ ● **_R_** ( 1 ≤ _R_ ≤ 10 ) - radius of a router range
The next line contains the following numbers:
​​ ​ ● **_Pb_** ( 1 ≤ _Pb_ ≤ 5 ) - price of connecting one cell to the backbone
​​ ​ ● **_Pr_** ( 5 ≤ _Pr_ ≤ 100 ) - price of one wireless router
​ ​ ● **_B_** ( 1 ≤ _B_ ≤ 109 ) ​ **_-_** maximum budget
The next line contains the following numbers:
​​ ​ ​ ● **_br_** , ​ **_bc_** ( 0 ≤ _br_ < _H_ , 0 ≤ _bc_ < _W_ )- row and column of the initial cell that is already connected to the
backbone
© Google 2017, All rights reserved.


​ The subsequent ​ **_H_** lines describe the grid of the building, one row after another from row 0 to row _H_ − 1.
The description of each row contains ​ **_W_** characters specifying the type of each cell, one column after
another from column 0 to column _W_ − 1. Each character is either “#” (denoting a wall cell), “.” (denoting a
target cell) or “-” (denoting a void cell).

### Example

```
8 22 3
1 100 220
2 7
----------------------
-########----########-
-#......######......#-
-#..................#-
-#..................#-
-#..................#-
-####################-
----------------------
8 rows, 22 columns, router range radius is 3
backbone costs 1, router costs 100, budget is 220
the initial cell connected to backbone is [2, 7]
Example input file.
```
## Submissions

### File format

```
The submission file must start with a line containing a single number ​ N ( 0 ≤ N < W × H ) - the number of
cells connected to the backbone.
N next lines must specify the cells connected to the backbone, without repetitions and not including the
initial cell connected to the backbone that is specified in the problem statement. Each cell in the list must be
either neighbors with the initial backbone cell, or must appear in the list after one of its neighbors. Each line
in the list has to contain two numbers: ​ r , ​ c ( 0 ≤ r < H , 0 ≤ c < W )- respectively the row and the column of
each cell connected to the backbone.
The next line must contain a single number ​ M ( 0 ≤ M ≤ W × H ) - the number of cells where routers are
placed.
M next lines must specify the cells where routers are placed without repetitions. Each of these lines must
contain two numbers: ​ r , ​ c ( 0 ≤ r < H , 0 ≤ c < W )- respectively the row and the column of each cell where a
router is placed.
```
### Example

```
3
3 6
3 8
3 9
2
3 6
3 9
three cells connected to the backbone
cell [3, 6] neighbors the initial backbone cell [2, 7] so can be connected
cell [3, 8] also neighbors the initial backbone cell [2, 7]
cell [3, 9] neighbors the cell [3, 8] already connected to backbone
two routers
[3, 6] is connected to backbone and not a wall so router can be put there
[3, 9] is also connected to backbone and not a wall
Example submission file.
© Google 2017, All rights reserved.
```

```
In the ​ example ​ above, the cells marked below are
connected to backbone, ‘b’ is the initial backbone cell, ‘r’
are the cells where routers are placed.
----------------------
-########----########-
-#.....b######......#-
-#....​r​.​.r​..........#-
-#..................#-
-#..................#-
-####################-
----------------------
The two routers placed in this ​ example ​ cover the target
cells marked below:
----------------------
-########----########-
-#.​.....​######......#-
-#.​..........​.......#-
-#.​..........​.......#-
-#.​..........​.......#-
-####################-
----------------------
```
### Validation

```
The output file is valid if it meets the file format specified above and the following criteria:
● all routers are placed in cells connected to the backbone
● no routers are placed in wall cells
● the budget is not exceeded, that is, N × Pb + M × Pr ≤ B.
```
### Scoring

Each submission earns 1000 points for each target cell covered with Internet access and 1 point for each
unit of remaining budget.
​ If the number of target cells covered is ​ **_t_** , the score is computed as follows:
_score_ = 1000 × _t_ +( _B_ −( _N_ × _Pb_ + _M_ × _Pr_ ))
In the ​ **example** above, the total number of target cells covered is 35. The budget is 220, there are 3
additional cells connected to the backbone and 2 routers.
The score of the example submission is therefore 1000 × 35 +( 220 − 3 × 1 − 2 × 100 ) which equals ​ **35017** ​.
**Note that there are multiple data sets representing separate instances of the problem. The final score for your team
will be the sum of your best scores on the individual data sets.**
© Google 2017, All rights reserved.


