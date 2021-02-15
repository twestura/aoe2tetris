# Aoe2 Tetris

An implementation of Tetris that is playable as an Age of Empires II scenario.

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

## Tetromino Rotation Rules

Some links to Tetromino rotation rules.

* [https://tetris.wiki/Super_Rotation_System](https://tetris.wiki/Super_Rotation_System)
* [https://harddrop.com/wiki/SRS](https://harddrop.com/wiki/SRS)

## Trigger sections

Triggers are broken up into sections for ease of reading and finding them in the scenario editor.

Each section has a name and begins with a section header, which is a blank trigger intentionally left unfinished so that it remains red in the editor's trigger list.
The format is `-- <section-name> --`.

The trigger name for each trigger in a section begins with a prefix in square brackets indicating which section it belongs to.
The format is `<section-prefix> <trigger-name>`.

## Game Tick Rate

The scenario is intended to be run at x8 speed, allowing for 8 game seconds per 1 IRL second.
That allows the game to process 8 user inputs per second.
The game engine checks for trigger execution once every game second.

## State Machine
