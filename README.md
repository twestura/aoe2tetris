# Aoe2 Tetris

An implementation of Tetris that is playable as an Age of Empires II scenario.
The download link will be available on [https://www.ageofempires.com/mods](https://www.ageofempires.com/mods).

## Hotkeys

The game uses the "Select All" hotkeys to implement player hotkeys without moving the camera.
The hotkeys and their actions are described in the following table and topic paragraphs.

| Action                     | Hotkey                     | Value |
| -------------------------- | -------------------------- | ----- |
| Move Left                  | Select All Archery Ranges  | 1     |
| Move Right                 | Select All Blacksmiths     | 2     |
| Rotate Clockwise           | Select All Stables         | 3     |
| Rotate Counterclockwise    | Select All Kreposts        | 4     |
| Soft Drop                  | Select All Monasteries     | 5     |
| Hard Drop                  | Select All Castles         | 6     |
| Hold                       | Select All Siege Workshops | 7     |
| Begin Game or Reset        | Select All Universities    | 8     |

The player has two of each building on the map.
The buildings begin the scenario being owned by the player, but are switched to the Gaia player at the beginning of the scenario.
Switching them from the player to Gaia ensures that the player does not recapture them without the use of the Change Ownership Effect.

There are two of each building on the map, one controlled by the player and the other controlled by Gaia.
The buildings are placed out of the way so they aren't visible near the main Tetris game.

Consider setting the line of sight of the buildings to 0 (and perhaps starting them as belonging to the Gaia player) so that the player never has vision of their location.

If players click buildings themselves, they may select multiple at once.
This behavior may be handled simply by establishing a priority, where one select is detected per game tick, with the highest priority selection disregarding all other selections.

Object Select Conditions are used to determine which building is selected and which hotkey is pressed.
The ownership of the selected building then is swapped with the other building (Player 1 to Gaia and Gaia to Player 1) in order to deselect the building.

A visual mod will remove the bottom-left of the UI and the selection sounds of the buildings.
Otherwise they may be distracting for the player.

## Pieces, Colors, Units, and Civilizations

A Tetris piece is called a Tetromino and consists of a color and a shape.
Each piece is represented in this scenario by a distinct color and unique unit.

| Name  | Color  | Unit (Civilization)       |
| ----- | -----  | -------------------       |
| Z     | Red    | Berserk (Vikings)         |
| S     | Green  | Huskarl (Goths)           |
| O     | Yellow | Throwing Axeman (Franks)  |
| I     | Cyan   | Teutonic Knight (Teutons) |
| T     | Purple | Samurai (Japanese)        |
| J     | Blue   | Woad Raider (Celts)       |
| L     | Orange | Longbowman (Britons)      |

## Game Tick Rate

The scenario is intended to be run at x8 speed, allowing for 8 game seconds per 1 IRL second.
That allows the game to process 8 user inputs per second.
The game engine checks for trigger execution once every game second.

## Tetromino Rotation Rules

Some links to Tetromino rotation rules.

* [https://tetris.wiki/Super_Rotation_System](https://tetris.wiki/Super_Rotation_System)
* [https://harddrop.com/wiki/SRS](https://harddrop.com/wiki/SRS)

## Score

Tetris scoring rules: [https://tetris.wiki/Scoring](https://tetris.wiki/Scoring)

TODO T-Spins

## Losing Condition

The game is over when a new Tetromino is blocked and cannot spawn.

### Storing the Hotkey Presses

At the beginning of the game loop, the first triggers work to collect the player's hotkey press and store them in a variable.
The value of that variable is then reset to 0 at the end of the game loop.
The value for a corresponding key press is stored based on the table.
Only one key is pressed per turn, with the highest building in the table (the one with the lowest value) being used if multiple hotkeys are pressed at once.

## State Machine

At the start of a scenario, the player will be prompted to press a button to begin playing a game of Tetris.

When the game is finished, the final game state is frozen with the score.
The player can then play again.

States are changed based on the press (or absence of a press) of a hotkey activating triggers one each game tick.

## Game Board

The playable area of the game board consists of Invisible Objects.
The board displays 20 rows and 10 columns.
Each tile on the board consists of 4 Invisible Objects, each facing one direction.

Pieces are placed by setting these Invisible Objects to units using the Replace Object effect.

There are also three groups of 8 Invisible Objects on the right side of the board to display the next 3 Tetrominos.
And there is a final group of 8 Invisible Objects on the left side of the board to display the hold Tetromino.

## Tetromino Generation

We use the Fisher Yates algorithm to permute a list of 7 pieces randomly.
A simple implementation of this algorithm in Python is as follows.

```python
def fisher_yates(seq: List[Any]):
    """Randomly permutes `seq` in place."""
    # inv: seq[j:] is randomized.
    for j in range(len(seq)-1, 0, -1):
        i = random.randInt(0, j)
        seq[i], seq[j] = seq[j], seq[i]
```

Random integers are needed in order to implement the inner part of the algorithm's loop.
In order to generate random integers we use a sequence of triggers with the `Chance` condition.

The scenario editor consists of a list of triggers that are checked once every game second, essentially following this pseudocode:

```text
for t in trigger_list:
    if t.is_active and all(c.is_satisfied for c in t.conditions):
        for e in t.effects:
            e.execute()
```

Importantly, if we activate/deactivate a trigger, the effect takes place during the current game tick's iteration of this loop.
For example the following code displays `C` (on the current tick), then `D` (on the current tick), then `A` (on the subsequent tick).

```text
Trigger A -> disabled, displays "A"
Trigger B -> enabled, activates A, activates D
Trigger C -> enabled, displays "C"
Trigger D -> disabled, displays "D"
```

To generate random numbers, we use triggers with `Chance` conditions set up in a tree to generate probabilities.
The `Chance` conditions are the inner nodes of the tree, and the leaves are integers.
For each node, the `Chance` probability `p` is a number between `0` and `100`.
This number `p` is the probability of choosing the left path in the tree, and `100 - p` is the probability of choosing the right path in the tree.
The product of the probabilities from the root to a leaf is the probability of choosing that integer.

For example, to generate a random number from 0, 1, or 2, we used the following tree.

```text
    67
   /  \
  50   2
 /  \
0    1
```

The probability of generating each number is:

0. `0.67 * 0.5 = 0.33`
1. `0.67 * (1 - 0.5) = 0.33`
2. `1 - 0.67 = 0.33`

We generate the random numbers and perform the Fisher Yates algorithm in one game tick, iterating through the trigger list.

## Objectives

The player's current score, level, and number of lines cleared are displayed on the right side of the screen in the Objectives panel.

## Rotations

The rotations array holds multiple coordinates as vectors.

```python
xsArray[ROTATE_I_INDEX] = [facingI_U, facingI_R, facingI_D, facingI_L]
facingI_U[CLOCKWISE] = [(0, 1), (0, -1), (0, 2), (1, -1), (-2, 1),]
xsArray[ROTATE_X_INDEX] = [facingX_U, facingX_R, facingX_D, facingX_L]
```
