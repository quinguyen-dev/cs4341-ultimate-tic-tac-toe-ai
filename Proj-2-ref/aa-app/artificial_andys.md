# Artificial Andys

## Team Members

David Danielian
Qui Nguyen
Michael O'Connor

### Team Contributions

Every member of the team participated in the theoretical development and pseudo-code creation for the project. Each solution for the major components were discussed and debated among the members equally.

David: Created the “player” class which is responsible for checking the game state, reading moves and writing moves to communicate with the referee. After minimax and alpha-beta pruning was written, modified code to implement iterative deepening to search more efficiently within the time limit.

Michael:
I implemented the board class that handles the digital representation of the game board and the necessary methods to update and evaluate the board after every move. I also developed the heuristic algorithm that assigns values to a given board state by assessing the state for several conditions such as: local board closures, local and global adjacency, local and global win blocks, etc. Additionally, I set up the time limit for the searching algorithm.

Qui: I implemented the AI class that handles the searching algorithm and determines our next best move. The algorithm that we used was minimax-ing with alpha beta pruning. Additionally, I wrote a majority of our docstrings and interfaced the Board, Player, and AI classes together. I also wrote most of the utility functions and added the State class.

## Compile and Run Instructions

The project was created using Python 3.10.7 so this is prerequisite for compilation.
The project can be run by calling `python3 aa-main.py` in the appropriate directory
The referee code should be pass the name `artificial_andys`

## Search Strategy

The AI class implements iterative deepening for exploration and minimax with alpha-beta pruning for move selection
The algorithm will take the current board state and expand each possible legal move for a set depth to grow the tree to a maximum depth, but during the exploration minimax with alpha-beta will prune unproductive branches to identify the best possible move.
Every iteration produces a "best move" that is stored and compared every iteration so even if we run out of time during an iteration we still have a rational move given the discovered information

## Heuristic Strategies

Our heuristics were primarily divided into heuristics that evaluated a 3x3 board (or local board) and heuristics that kept track of progress for the overall board (or global board).

### Local Boards

#### Board Closure

Win a local board is won, lost, or results in a draw, the board is considered closed to further moves. The algorithm needs to decide if closing the board results in a win for the current player. Closing boards is the only way to "make a move" on the global board and get closer to winning. So, ew provide the algorithm incentive to win, some incentive for drawing, and no incentive for losing

#### Blocking Opponent

Blocking an opponent win on a local board prevents them from being able to make a move on the global board and therefore prevents them from winning. This defensive strategy enables us to delay the opponent as we set up our own win

#### Adjacency

The only way to win a local board is to get 3 pieces in a row, column, or diagonal. Therefore, we introduced a heuristic to prioritize placing a mark near another mark of the same kind as long as that row, column, or diagonal has not already been blocked from winning by an opponent's previous move.

### Global Boards

#### Blocking Opponent

Blocking an opponent win on a global board prevents a loss for the entire game. This is an extremely important calculation for the agent to make as it is the only way to insure that the game will continue.

#### Adjacency

Following the same logic for the local boards, the agent needs to make 3 adjacent moves on the global space.

#### Opportunity

Making moves on the global board is much less common compared to the moves being made on the local boards. We provide a small incentive for the agent to make moves on boards with the highest number of chances to win, i.e. we prioritize the center board and the corner boards as this gives the agent more opportunities to win.

## Evaluation Function

The evaluation function is calculated for every move until either we have reached the pre-defined depth setup by the iterative deepening control loop or if time has run out. At that point, it will assign a value to the current node that propagates back up to its ancestor nodes. The value that it assigns is a weighted sum of the heuristics discussed above. All heuristics that deal with the global board are weighted higher on the basis that the global board is what decides a win or loss.

## Utility Function

The utility function is integrated into the evaluation function. Win a move results in a global win for the current player, a large value is added to the heuristic score that is large enough to make the other values essentially irrelevant. In our case, we add the value 10000 to heuristic scores that are averaging around ~200 depending on the depth.

## Results

Testing our program took on two forms.

### Against Itself

When testing to ensure that all possible moves were valid and that the program could function against a "optimal" agent, we played it against itself. This essentially allowed our agent to make twice as many moves, which made it easier to identify patterns of behavior.
These results helped by catching edge cases and identifying strange behaviors due to heuristic weighting or search protocol.

### Testing Against a Random Agent

Testing against a random agent enabled us to verify that our heuristics were better than randomly choosing, which indicates that they are functioning. We are happy to say that our agent has not yet lost to a random agent.
It seems effective aat blocking opponent wins on local boards.
However, when moves result in wildcard placements (when a move allows the next player to play anywhere on the board), the algorithm has trouble predicting moves with high accuracy within the time limit.
