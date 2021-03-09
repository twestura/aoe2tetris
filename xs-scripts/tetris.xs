/// xs file for Aoe2 Tetris.
///
/// Maybe one day xs will have structs. And monads. :)

// FE documentation:
// https://www.forgottenempires.net/age-of-empires-ii-definitive-edition/xs-scripting-in-age-of-empires-ii-definitive-edition

// Aoe3 xs documentation:
// https://eso-community.net/viewtopic.php?p=436182

// There is array functionality that isn't listed in the FE documentation.
// There are five types: bool, float, int, string, and Vector.
// ```
// xsArraySetType(arrayID, index, value)
// xsArrayGetType(arrayID, index)
// xsArrayGetSize(arrayID)
// ```

// =============================================================================
// Constant Globals
// =============================================================================

/// The id of the variable that holds the player's score.
const int SCORE_ID = 0;

/// The initial player score.
const int SCORE_INIT = 0;

/// The id of the variable that holds the player's level.
const int LEVEL_ID = 1;
/// The initial level.

/// The initial starting level without clearing any rows.
const int LEVEL_INIT = 1;

/// The id of the variable that holds the number of cleared lines.
const int LINES_ID = 2;

/// The initial number of cleared lines.
const int LINES_INIT = 0;

/// The number of rows in a game of Tetris.
const int TETRIS_ROWS = 40;

/// The number of columns in a game of Tetris.
const int TETRIS_COLS = 10;

/// The index of the first visible row in a game of Tetris.
const int VISIBLE = 20;

/// Constants to represent Tetromino shapes.
/// The same as the enum values assigned in `tetromino.py`.
const int I = 5;
const int J = 7;
const int L = 1;
const int O = 4;
const int S = 3;
const int T = 6;
const int Z = 2;

/// The number of distinct Tetrominos.
const int NUM_TETROMINOS = 7;

/// The number of tiles covered by each Tetromino.
const int NUM_TILES = 4;

/// Constants to represent the directions in which Tetrominos can move and face.
/// The same as the enum values assigned in `direction.py`.
const int UP = 0;
const int RIGHT = 1;
const int DOWN = 2;
const int LEFT = 3;

/// The number of facing directions.
const int NUM_DIRS = 4;

/// Constants to represent the directions in which Tetrominos can rotate.
const int CLOCKWISE = 0;
const int COUNTERCLOCKWISE = 1;

/// Constants to represent game actions triggered by users pressing hotkeys to
/// select buildings.
/// The same as the enum values assigned in `action.py`.
const int NO_ACTION = 0;
const int MOVE_LEFT = 1;
const int MOVE_RIGHT = 2;
const int ROTATE_CLOCKWISE = 3;
const int ROTATE_COUNTERCLOCKWISE = 4;
const int SOFT_DROP = 5;
const int HARD_DROP = 6;
const int HOLD = 7;
const int NEW_GAME = 8;

/// The initial row when a new Tetromino is spawned: one above the highest
/// visible row.
const int PLACE_ROW = 19;

/// The initial column when a new Tetromino is spawned: the left-center column.
const int PLACE_COL = 4;

/// The initial upwards facing direction of a new Tetromino when spawned.
const int PLACE_DIR = UP;

/// The number of rotation tests for all Tetrominos other than `O`.
const int NUM_ROTATION_TESTS = 5;

/// For every Soft Drop, the player's score increases by
/// the player's current level multiplied by `SOFT_DROP_MULTIPLIER`.
const int SOFT_DROP_MULTIPLIER = 1;

/// For every line passed in a Hard Drop, the player's score increases by
/// the player's current level multiplied by `HARD_DROP_MULTIPLIER`.
const int HARD_DROP_MULTIPLIER = 2;

/// The number of lines to clear in order to level up.
const int LINES_PER_LEVEL = 10;

/// The number of game ticks to delay while watching Tetrominos explode.
const int EXPLODE_DELAY = 8;

/// The number of seconds in two hours.
const int TWO_HOURS = 7200;

// =============================================================================
// Mutable Globals
// =============================================================================

/// The array id of the game board array.
int boardArrayId = -1;

/// The array id of the update array.
int updateArrayId = -1;

/// The array id of the tetromino offsets array.
int tetrominoOffsetsId = -1;

/// The array id of the I tetromino rotation offsets.
int rotateIId = -1;

/// The array id of the J, L, S, T, and Z tetromino rotation offsets.
int rotateXId = -1;

/// The row of the active Tetromino's center.
int activeRow = PLACE_ROW;

/// The column of the active Tetromino's center.
int activeCol = PLACE_COL;

/// The facing direction of the active Tetromino.
int activeFacing = PLACE_DIR;

/// The array id containing the Tetromino sequence.
int tetrominoSeqId = -1;

/// The index of the current active Tetromino in the Tetromino sequence.
/// In `0..NUM_TETROMINOS`.
int tetrominoSeqIndex = 0;

/// The selected hotkey and action to perform on the current game tick.
int selected = NO_ACTION;

/// `true` when the second half of the Tetromino sequence should be shuffled,
/// on the current game tick, `false` otherwise.
bool canShuffleSecondSeq = false;

/// `true` if the previous score action qualifies for a difficulty bonus,
/// `false` otherwise.
bool difficult = false;

/// `true` if the game is over, `false` if the game is ongoing.
bool gameOver = false;

/// `true` to render the next boards, `false` otherwise.
bool renderNext = false;

/// `true` if the active tetromino may be held, `false` if not.
bool isHoldLegal = false;

/// `true` if the hold board should be re-rendered on the current game tick,
/// `false` if not.
bool renderHold = false;

/// Equals the int value of the held tetromino if a tetromino is held,
/// equals `0` if no tetromino is held.
int heldTetromino = 0;

/// Equals the int value of the tetromino that was held before the currently
/// help Tetromino.
int prevHeld = 0;

/// The time remaining before the active tetromino is moved down automatically.
/// Nonnegative.
/// At most one timer is nonzero.
int timer = 0;

/// `true` if the player has cleared 4 rows, `false` otherwise.
/// Signals the game to react to the event of scoring a Tetris.
bool reactTetris = false;

/// Timer to count down the number of seconds remaining until an exploded row
/// is cleared of explosions.
/// Nonnegative.
/// At most one timer is nonzero.
int explodeTimer = 0;

/// `true` to pause for 1 tick after locking down a Tetromino, `false` if not
/// to pause.
bool placePause = false;

/// Signal flag to react to a successful move.
/// `true` if the reaction should be played during the current game tick,
/// `false` if not.
bool hasMoved = false;

/// Signal flag to react to a hold.
/// `true` if the reaction should be played during the current game tick,
/// `false` if not.
bool hasHeld = false;

/// Signal flag to react to a failed hold.
/// `true` if the reaction should be played during the current game tick,
/// `false` if not.
bool hasFailedHold = false;

/// Array Id of the signal array for exploding a row.
int explodeArrayId = 0;

/// Array Id of the signal array for clearing the explosions.
int clearExplodeArrayId = 0;

/// `true` if the 2 hour Easter egg has played, `false` otherwise.
bool hasPlayedEasterEgg = false;

/// `true` if a Tetromino locked down on the current game tick,
/// `false` otherwise.
bool hasLockedDown = false;

// =============================================================================
// Utility Functions
// =============================================================================

/// Writes a chat message containing the values of the array.
///
/// Parameters:
///     arrayId: The id of the array to chat.
void _chatArray(int arrayId = 0) {
    string output = "[";
    string delim = "";
    int n = xsArrayGetSize(arrayId);
    for (k = 0; < n) {
        output = output + delim + xsArrayGetInt(arrayId, k);
        delim = ", ";
    }
    output = output + "]";
    xsChatData("Array ID: %d", arrayId);
    xsChatData("Array Length: %d", n);
    xsChatData(output);
}

/// Returns a string representation of vector `v`.
string _vecStr(Vector v = Vector(0.0, 0.0, 0.0)) {
    float x = xsVectorGetX(v);
    float y = xsVectorGetY(v);
    float z = xsVectorGetZ(v);
    return ("(" + x + ", " + y + ", " + z + ")");
}

/// Writes a chat message containing the values of the array of Vectors.
///
/// Parameters:
///     arrayId: The id of the array to chat.
void _chatVectorArray(int arrayId = 0) {
    string output = "[";
    string delim = "";
    int n = xsArrayGetSize(arrayId);
    for (k = 0; < n) {
        output = output + delim + _vecStr(xsArrayGetVector(arrayId, k));
        delim = ", ";
    }
    output = output + "]";
    xsChatData("Array ID: %d", arrayId);
    xsChatData("Array Length: %d", n);
    xsChatData(output);
}

/// Returns a `Vector` with the first two coordinates of `v` rotated
/// 90 degrees clockwise.
///
/// Parameters:
///     v: The `Vector` to rotate.
Vector _rotateCW(Vector v = Vector(0.0, 0.0, 0.0)) {
    float r = xsVectorGetX(v);
    float c = xsVectorGetY(v);
    return (xsVectorSet(c, 0.0 - r, 0.0));
}

/// Returns a `Vector` with the first two coordinates of `v` rotated
/// 90 degrees counterclockwise.
///
/// Parameters:
///     v: The `Vector` to rotate.
Vector _rotateCCW(Vector v = Vector(0.0, 0.0, 0.0)) {
    float r = xsVectorGetX(v);
    float c = xsVectorGetY(v);
    return (xsVectorSet(0.0 - c, r, 0.0));
}

/// Returns a `Vector` rotate to turn from facing `UP` to facing direction `d`.
///
/// Parameters:
///     v: The `Vector` to rotate.
///     d: The target direction.
Vector _rotateVector(Vector v = Vector(0.0, 0.0, 0.0), int d = 0) {
    if (d == RIGHT) {
        return (_rotateCW(v));
    }
    if (d == DOWN) {
        return (_rotateCW(_rotateCW(v)));
    }
    if (d == LEFT) {
        return (_rotateCCW(v));
    }
    return (v);
}

/// Roturns the number of clockwise 90 degree turns a unit takes to rotate.
///
/// ```
/// _rotationDelta(CLOCKWISE) == 1
/// _rotationDelta(COUNTERCLOCKWISE) == 3
/// ```
///
/// Parameters:
///     r: The rotation direction. One of `CLOCKWISE` or `COUNTERCLOCKWISE`.
int _rotationDelta(int r = 0) {
    if (r == CLOCKWISE) {
        return (1);
    }
    return (3);
}

/// Returns the direction `d` rotated in direction `r`.
/// Parameters:
///     d: The facing direction, in `0..=3`.
///     r: The rotation direction. One of `CLOCKWISE` or `COUNTERCLOCKWISE`.
int _rotateDirection(int d = 0, int r = 0) {
    return ((d + _rotationDelta(r)) % NUM_DIRS);
}

// =============================================================================
// Timer
// =============================================================================

/// Resets `timer` to the initial value based on `level`.
/// The timer is increments once every game second.
///
/// Parameters:
///     level: The level at which to base the timer. Strictly positive.
void _resetTimer(int level = 0) {
    if (level == 1) {
        timer = 8 * 2;
    } else if (level <= 3) {
        timer = 8;
    } else if (level <= 5) {
        timer = 7;
    } else if (level <= 6) {
        timer = 6;
    } else if (level <= 7) {
        timer = 5;
    } else if (level <= 8) {
        timer = 4;
    } else if (level <= 9) {
        timer = 3;
    } else if (level <= 10) {
        timer = 2;
    } else {
        timer = 1;
    }
}


// =============================================================================
// Board Array
// =============================================================================

/// Initializes an empty tile in a game board row
//  and returns the tile's array id.
/// See the specification of `_initBoard`.
/// is initialized to `false`.
///
/// Parameters:
///     r: The row index.
///     c: The column index.
int _initBoardTile(int r = 0, int c = 0) {
    return (
        xsArrayCreateInt(NUM_DIRS, 0, "Tile board[" + r + "][" + c + "]")
    );
}

/// Initializes an empty row in a game board and returns the row's array id.
/// See the specification of `_initBoard`.
///
/// Parameters:
///     r: The row index.
int _initBoardRow(int r = 0) {
    int rowId = xsArrayCreateInt(TETRIS_COLS, 0, "Board Row " + r);
    for (c = 0; < TETRIS_COLS) {
        int tileId = _initBoardTile(r, c);
        xsArraySetInt(rowId, c, tileId);
    }
    return (rowId);
}

/// Initializes an empty game board and set the id of this board's array
/// to `boardArrayId`.
/// A game board consists of nested arrays in order to hold the piece and facing
/// of every tile in the game.
///
/// The board is an int array of length `TETRIS_ROWS`. Each entry holds the id
/// of a row array.
/// Each row array is an int array of length `TETRIS_COLS`. Each row-array entry
/// holds the id of board tile array.
/// Each tile array is an integer value representing either `0` if there is a
/// there is no piece at the tile facing in that direction, or the value
/// of a Tetromino if there is a piece facing in that direction.
/// At most one of the array values in a tile may be non-zero.
///
/// Intuitively, board[row][column][direction] is `0` when empty or an in
/// in `1..=7` if there is a Tetromino there.
void _initBoard() {
    int boardId = xsArrayCreateInt(TETRIS_ROWS, 0, "Outer Board Array");
    boardArrayId = boardId;
    for (r = 0; < TETRIS_ROWS) {
        int rowId = _initBoardRow(r);
        xsArraySetInt(boardId, r, rowId);
    }
}

/// Returns a value from the state board.
///
/// Parameters:
///     r: The row index, in `0..TETRIS_ROWS`.
///     c: The column index, in `0..TETRIS_COLS`.
///     d: The facing direction, in `0..NUM_DIRS`.
int _getBoardValue(int r = 0, int c = 0, int d = 0) {
    int rowId = xsArrayGetInt(boardArrayId, r);
    int tileId = xsArrayGetInt(rowId, c);
    return (xsArrayGetInt(tileId, d));
}

/// Sets a value in the state board.
///
/// Parameters:
///     r: The row index, in `0..TETRIS_ROWS`.
///     c: The column index, in `0..TETRIS_COLS`.
///     d: The facing direction, in `0..NUM_DIRS`.
///     t: The value to set, in `0..=7`.
void _setBoardValue(int r = 0, int c = 0, int d = 0, int t = 0) {
    int rowId = xsArrayGetInt(boardArrayId, r);
    int tileId = xsArrayGetInt(rowId, c);
    xsArraySetInt(tileId, d, t);
}

/// Returns `true` if the board contains the Tetromino `t` at the
/// indicated tile and direction.
///
/// Parameters:
///     r: The row index, in `0..TETRIS_ROWS`.
///     c: The column index, in `0..TETRIS_COLS`.
///     d: The facing direction, in `0..NUM_DIRS`.
///     t: The value to compare to.
bool _tileContains(int r = 0, int c = 0, int d = 0, int t = 0) {
    return (_getBoardValue(r, c, d) == t);
}

/// Returns `true` if the board is empty at the indicated tile.
///
/// Parameters:
///     r: The row index, in `0..TETRIS_ROWS`.
///     c: The column index, in `0..TETRIS_COLS`.
bool _isTileEmpty(int r = 0, int c = 0) {
    for (d = 0; < NUM_DIRS) {
        if (_tileContains(r, c, d, 0) == false) {
            return (false);
        }
    }
    return (true);
}

/// Returns `true` if the row and column coordinate `(r, c)` is in bounds
/// and the board tile at coordinate `(r, c)` in direction `d` is empty.
///
/// Parameters:
///     r: The row index to check.
///     c: The column index to check.
bool _isInBoundsAndEmpty(int r = 0, int c = 0,) {
    if (r < 0 || r >= TETRIS_ROWS || c < 0 || c >= TETRIS_COLS) {
        return (false);
    }
    return (_isTileEmpty(r, c));
}

/// Clears the game board.
/// Essentially sets `board[r][c][d] = 0` for all rows, columns, and directions.
void _clearBoard() {
    for (r = 0; < TETRIS_ROWS) {
        for (c = 0; < TETRIS_COLS) {
            for (d = 0; < NUM_DIRS) {
                _setBoardValue(r, c, d, 0);
            }
        }
    }
}

// =============================================================================
// Update Array
// =============================================================================

/// Initializes an boolean array for a tile direction in the update array.
/// See the specification of `_initUpdate`.
/// The length of the array is one more than the number of Tetrominos, to
/// account for the invisible object case.
///
/// Parameters:
///     r: The row index.
///     c: The column index.
///     d: The direction.
int _initUpdateDir(int r = 0, int c = 0, int d = 0) {
    return (
        xsArrayCreateBool(
            NUM_TETROMINOS + 1, false, "Update[" + r + "][" + c + "][" + d + "]"
        )
    );
}

/// Initializes an empty tile in the update array and returns the tile's id.
/// See the specification of `_initUpdate`.
///
/// Parameters:
///     r: The row index.
///     c: The column index.
int _initUpdateTile(int r = 0, int c = 0) {
    int tileId = xsArrayCreateInt(
        NUM_DIRS, 0, "Tile update[" + r + "][" + c + "]"
    );
    for (d = 0; < NUM_DIRS) {
        int dirId = _initUpdateDir(r, c, d);
        xsArraySetInt(tileId, d, dirId);
    }
    return (tileId);
}

/// Initializes an empty row in the update array and returns the row's id.
/// See the specification of `_initUpdate`.
///
/// Parameters:
///     r: The row index.
int _initUpdateRow(int r = 0) {
    int rowId = xsArrayCreateInt(TETRIS_COLS, 0, "Update Row " + r);
    for (c = 0; < TETRIS_COLS) {
        int tileId = _initUpdateTile(r, c);
        xsArraySetInt(rowId, c, tileId);
    }
    return (rowId);
}

/// Initializes the game's update array.
///
/// The update array is a 4d-array with dimensions for row, column, direction,
/// and Tetromino.
///
/// A value of `true` indicates that the unit at that index must
/// be re-rendered. The array is set to all `false` at the beginning of each
/// game loop, and values are set to `true` during the update processing.
/// When a new game is launched, all entries of `Update` are set to `true`.
void _initUpdate() {
    int updateId = xsArrayCreateInt(TETRIS_ROWS, 0, "Outer Update Array");
    updateArrayId = updateId;
    for (r = 0; < TETRIS_ROWS) {
        int rowId = _initUpdateRow(r);
        xsArraySetInt(updateArrayId, r, rowId);
    }
}

/// Returns a value from the update array.
///
/// Parameters:
///     r: The row index, in `0..TETRIS_ROWS`.
///     c: The column index, in `0..TETRIS_COLS`.
///     d: The facing direction, in `0..NUM_DIRS`.
///     t: The Tetromino, in `0..=NUM_TETROMINOS`.
bool _getUpdateValue(int r = 0, int c = 0, int d = 0, int t = 0) {
    int rowId = xsArrayGetInt(updateArrayId, r);
    int tileId = xsArrayGetInt(rowId, c);
    int dirId = xsArrayGetInt(tileId, d);
    return (xsArrayGetBool(dirId, t));
}

/// Sets a value in the update array.
///
/// Parameters:
///     r: The row index, in `0..TETRIS_ROWS`.
///     c: The column index, in `0..TETRIS_COLS`.
///     d: The facing direction, in `0..NUM_DIRS`.
///     t: The Tetromino, in `0..=NUM_TETROMINOS`.
///     b: The value to set.
void _setUpdateValue(
    int r = 0, int c = 0, int d = 0, int t = 0, bool b = false
) {
    int rowId = xsArrayGetInt(updateArrayId, r);
    int tileId = xsArrayGetInt(rowId, c);
    int dirId = xsArrayGetInt(tileId, d);
    xsArraySetBool(dirId, t, b);
}

/// Sets all invisible object renderings to `true` and all other renderings
/// to `false`.
void _clearUpdate() {
    for (r = 0; < TETRIS_ROWS) {
        for (c = 0; < TETRIS_COLS) {
            for (d = 0; < NUM_DIRS) {
                _setUpdateValue(r, c, d, 0, true);
                for (t = 1; < NUM_TETROMINOS + 1) {
                    _setUpdateValue(r, c, d, t, false);
                }
            }
        }
    }
}

/// Sets all entries of the update array to `b`.
///
/// Parameters:
///     b: The value to set to all entires of the update array.
void _setAllUpdate(bool b = false) {
    for (r = 0; < TETRIS_ROWS) {
        for (c = 0; < TETRIS_COLS) {
            for (d = 0; < NUM_DIRS) {
                for (t = 0; < NUM_TETROMINOS + 1) {
                    _setUpdateValue(r, c, d, t, b);
                }
            }
        }
    }
}

// =============================================================================
// Clear Rows
// =============================================================================

/// Returns `true` if all tiles in `row` are occupied, `false` if any are empty.
///
/// Parameters:
///     row: The row index to check, in `0..TETRIS_ROWS`.
bool _isRowFilled(int row = 0) {
    for (col = 0; < TETRIS_COLS) {
        if (_isTileEmpty(row, col)) {
            return (false);
        }
    }
    return (true);
}

/// Returns the number of tiles filled in the row with index `row`.
///
/// Parameters:
///     row: The row index to check, in `0..TETRIS_ROWS`.
int _numFilled(int row = 0) {
    int total = 0;
    for (col = 0; < TETRIS_COLS) {
        if (_isTileEmpty(row, col) == false) {
            total++;
        }
    }
    return (total);
}

/// Clears the row at index `row` and moves all rows above it one row down.
///
/// Parameters:
///     row: The row index to begin moving, in `0..TETRIS_ROWS`.
///         Requires `isRowFilled(row) == true`.
void _moveRowsDown(int row = 0) {
    int r = row;
    while (r > 0) {
        for (c = 0; < TETRIS_COLS) {
            for (d = 0; < NUM_DIRS) {
                int value = _getBoardValue(r - 1, c, d);
                _setBoardValue(r, c, d, value);
                for (t = 0; <= NUM_TETROMINOS) {
                    if (t != value) {
                        _setUpdateValue(r, c, d, t, false);
                    }
                }
                _setUpdateValue(r, c, d, value, true);
            }
        }
        r--;
    }
    for (ctop = 0; < TETRIS_COLS) {
        for (dtop = 0; < NUM_DIRS) {
            _setBoardValue(0, ctop, dtop, 0);
            _setUpdateValue(0, ctop, dtop, 0, true);
            for (ttop = 1; <= NUM_TETROMINOS) {
                _setUpdateValue(0, ctop, dtop, ttop, false);
            }
        }
    }
}

// =============================================================================
// Tetromino Sequence
// =============================================================================

/// Initializes the Tetromino Sequence.
///
/// Note this funciton does not shuffle the sequences. Shuffling is performed
/// by the scenario triggers.
void _initSequence() {
    tetrominoSeqId = xsArrayCreateInt(
        2 * NUM_TETROMINOS, 0, "Tetromino Sequence"
    );
    for (k = 0; < NUM_TETROMINOS) {
        xsArraySetInt(tetrominoSeqId, k, k + 1);
        xsArraySetInt(tetrominoSeqId, k + NUM_TETROMINOS, k + 1);
    }
}

/// Returns the value at `index` of the Tetromino sequence.
///
/// Parameters:
///     index: The index from which to retrieve a value.
///         Requires `0 <= index < 2 * NUM_TETROMINOS`.
int _getSequence(int index = 0) {
    return (xsArrayGetInt(tetrominoSeqId, index));
}

/// Returns the value at `index` of the Tetromino sequence to `value`.
///
/// Parameters:
///     index: The index from which to retrieve a value.
///         Requires `0 <= index < 2 * NUM_TETROMINOS`.
///     value: The value to assign in the sequence.
void _setSequence(int index = 0, int value = 0) {
    xsArraySetInt(tetrominoSeqId, index, value);
}

/// Swaps the values of the Tetromino sequence at the given indices.
///
/// Parameter:
///     seqNum: `0` for the sequence of the first 7 Tetrominos,
///             `1` for the sequence of the second 7 Tetrominos.
///     i: An index to swap, in `0..=6`.
///     j: An index to swap, in `0..=6`.
void swapSeqValues(int seqNum = 0, int i = 0, int j = 0) {
    int offset = seqNum * NUM_TETROMINOS;
    int index0 = offset + i;
    int index1 = offset + j;
    int x = _getSequence(index0);
    int y = _getSequence(index1);
    _setSequence(index0, y);
    _setSequence(index1, x);
}

/// Returns `true` if the second Tetromino sequence should be randomized,
/// `false` otherwise.
bool canGenerateSecondSequence() {
    return (canShuffleSecondSeq);
}

// =============================================================================
// Position State Information
// =============================================================================

/// Returns the value at the active index of the Tetromino sequence.
int _activeTetromino() {
    return (_getSequence(tetrominoSeqIndex));
}

/// Writes a debug chat message to display position information for the
/// active Tetromino.
void _chatPositionInfo() {
    xsChatData(
        "Active: ("
        + activeRow
        + ", "
        + activeCol
        + ") "
        + activeFacing
        + " - "
        + _activeTetromino()
    );
}

// =============================================================================
// Tetromino Offsets
// =============================================================================

// The Tetromino value - 1 is the index in the array of the offsets.
// Each offset array is an array of vectors, where the first two coordinates of
// each vector are set to the row and column offsets. The 3rd coordinate is
// unused.
// `offsets = [offsetsL, offsetsZ, ... offsetsJ];`

/// Returns the array id of the offsets for Tetromino t.
///
/// Parameters:
///     t: The Tetromion, in `1..=7`.
int _getOffsets(int t = 0) {
    return (xsArrayGetInt(tetrominoOffsetsId, t - 1));
}

/// Returns the array if of the offsets for the active Tetromino.
int _getActiveOffsets() {
    return (_getOffsets(_activeTetromino()));
}

/// Initalizes the Tetromino offset arrays.
void _initOffsetArrays() {
    tetrominoOffsetsId = xsArrayCreateInt(
        NUM_TETROMINOS, 0, "Tetromino Offset Array"
    );
    for (t = 1; <= NUM_TETROMINOS) {
        int offsetArrayId = xsArrayCreateVector(
            NUM_TILES, Vector(0.0, 0.0, 0.0), "Offset Array " + t
        );
        int index = t - 1;
        xsArraySetInt(tetrominoOffsetsId, index, offsetArrayId);
    }

    // Sets the I offsets.
    int arrayI = _getOffsets(I);
    xsArraySetVector(arrayI, 0, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayI, 2, Vector(0.0, 1.0, 0.0));
    xsArraySetVector(arrayI, 3, Vector(0.0, 2.0, 0.0));

    // Sets the J offsets.
    int arrayJ = _getOffsets(J);
    xsArraySetVector(arrayJ, 0, Vector(-1.0, -1.0, 0.0));
    xsArraySetVector(arrayJ, 1, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayJ, 3, Vector(0.0, 1.0, 0.0));

    // Sets the L offsets.
    int arrayL = _getOffsets(L);
    xsArraySetVector(arrayL, 0, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayL, 2, Vector(0.0, 1.0, 0.0));
    xsArraySetVector(arrayL, 3, Vector(-1.0, 1.0, 0.0));

    // Sets the O offsets.
    int arrayO = _getOffsets(O);
    xsArraySetVector(arrayO, 1, Vector(-1.0, 0.0, 0.0));
    xsArraySetVector(arrayO, 2, Vector(-1.0, 1.0, 0.0));
    xsArraySetVector(arrayO, 3, Vector(0.0, 1.0, 0.0));

    // Sets the S offsets.
    int arrayS = _getOffsets(S);
    xsArraySetVector(arrayS, 0, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayS, 2, Vector(-1.0, 0.0, 0.0));
    xsArraySetVector(arrayS, 3, Vector(-1.0, 1.0, 0.0));

    // Sets the T offsets.
    int arrayT = _getOffsets(T);
    xsArraySetVector(arrayT, 0, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayT, 2, Vector(0.0, 1.0, 0.0));
    xsArraySetVector(arrayT, 3, Vector(-1.0, 0.0, 0.0));

    // Sets the Z offsets.
    int arrayZ = _getOffsets(Z);
    xsArraySetVector(arrayZ, 0, Vector(-1.0, -1.0, 0.0));
    xsArraySetVector(arrayZ, 1, Vector(-1.0, 0.0, 0.0));
    xsArraySetVector(arrayZ, 3, Vector(0.0, 1.0, 0.0));
}

/// Chats the contents of the offset arrays for debugging.
void chatOffsetArrays() {
    for (t = 0; < NUM_TETROMINOS) {
        xsChatData("Array " + t);
        int arrayId = xsArrayGetInt(tetrominoOffsetsId, t);
        for (j = 0; < NUM_TILES) {
            Vector v = xsArrayGetVector(arrayId, j);
            xsChatData("(" + t + ", " + j + "): " + _vecStr(v));
        }
    }
}

// =============================================================================
// Rotation Offsets
// =============================================================================

/// Initializes the rotation array for the I Tetromino.
void _initRotationI() {
    int rotationHeader = xsArrayCreateInt(NUM_DIRS, 0, "Rotate I Offsets");
    rotateIId = rotationHeader;

    int arrayU = xsArrayCreateInt(2, 0, "Rotate I Up");
    xsArraySetInt(rotationHeader, UP, arrayU);
    // UCW
    int arrayUCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate I Up CW"
    );
    xsArraySetInt(arrayU, CLOCKWISE, arrayUCW);
    xsArraySetVector(arrayUCW, 0, Vector(0.0, 1.0, 0.0));
    xsArraySetVector(arrayUCW, 1, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayUCW, 2, Vector(0.0, 2.0, 0.0));
    xsArraySetVector(arrayUCW, 3, Vector(1.0, -1.0, 0.0));
    xsArraySetVector(arrayUCW, 4, Vector(-2.0, 2.0, 0.0));
    // UCCW
    int arrayUCCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate I Up CCW"
    );
    xsArraySetInt(arrayU, COUNTERCLOCKWISE, arrayUCCW);
    xsArraySetVector(arrayUCCW, 0, Vector(1.0, 0.0, 0.0));
    xsArraySetVector(arrayUCCW, 1, Vector(1.0, -1.0, 0.0));
    xsArraySetVector(arrayUCCW, 2, Vector(1.0, 2.0, 0.0));
    xsArraySetVector(arrayUCCW, 3, Vector(-1.0, -1.0, 0.0));
    xsArraySetVector(arrayUCCW, 4, Vector(2.0, 2.0, 0.0));

    int arrayR = xsArrayCreateInt(2, 0, "Rotate I Right");
    xsArraySetInt(rotationHeader, RIGHT, arrayR);
    // RCW
    int arrayRCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate I Right CW"
    );
    xsArraySetInt(arrayR, CLOCKWISE, arrayRCW);
    xsArraySetVector(arrayRCW, 0, Vector(1.0, 0.0, 0.0));
    xsArraySetVector(arrayRCW, 1, Vector(1.0, -1.0, 0.0));
    xsArraySetVector(arrayRCW, 2, Vector(1.0, 2.0, 0.0));
    xsArraySetVector(arrayRCW, 3, Vector(-1.0, -1.0, 0.0));
    xsArraySetVector(arrayRCW, 4, Vector(2.0, 2.0, 0.0));
    // RCCW
    int arrayRCCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate I Right CCW"
    );
    xsArraySetInt(arrayR, COUNTERCLOCKWISE, arrayRCCW);
    xsArraySetVector(arrayRCCW, 0, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayRCCW, 1, Vector(0.0, 1.0, 0.0));
    xsArraySetVector(arrayRCCW, 2, Vector(0.0, -2.0, 0.0));
    xsArraySetVector(arrayRCCW, 3, Vector(-1.0, 1.0, 0.0));
    xsArraySetVector(arrayRCCW, 4, Vector(2.0, -2.0, 0.0));

    int arrayD = xsArrayCreateInt(2, 0, "Rotate I Down");
    xsArraySetInt(rotationHeader, DOWN, arrayD);
    // DCW
    int arrayDCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate I Down CW"
    );
    xsArraySetInt(arrayD, CLOCKWISE, arrayDCW);
    xsArraySetVector(arrayDCW, 0, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayDCW, 1, Vector(0.0, 1.0, 0.0));
    xsArraySetVector(arrayDCW, 2, Vector(0.0, -2.0, 0.0));
    xsArraySetVector(arrayDCW, 3, Vector(-1.0, 1.0, 0.0));
    xsArraySetVector(arrayDCW, 4, Vector(2.0, -2.0, 0.0));
    // DCCW
    int arrayDCCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate I Down CCW"
    );
    xsArraySetInt(arrayD, COUNTERCLOCKWISE, arrayDCCW);
    xsArraySetVector(arrayDCCW, 0, Vector(-1.0, 0.0, 0.0));
    xsArraySetVector(arrayDCCW, 1, Vector(-1.0, 1.0, 0.0));
    xsArraySetVector(arrayDCCW, 2, Vector(-1.0, -2.0, 0.0));
    xsArraySetVector(arrayDCCW, 3, Vector(1.0, 1.0, 0.0));
    xsArraySetVector(arrayDCCW, 4, Vector(-2.0, -2.0, 0.0));

    int arrayL = xsArrayCreateInt(2, 0, "Rotate I Left");
    xsArraySetInt(rotationHeader, LEFT, arrayL);
    // LCW
    int arrayLCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate I Left CW"
    );
    xsArraySetInt(arrayL, CLOCKWISE, arrayLCW);
    xsArraySetVector(arrayLCW, 0, Vector(-1.0, 0.0, 0.0));
    xsArraySetVector(arrayLCW, 1, Vector(-1.0, 1.0, 0.0));
    xsArraySetVector(arrayLCW, 2, Vector(-1.0, -2.0, 0.0));
    xsArraySetVector(arrayLCW, 3, Vector(1.0, 1.0, 0.0));
    xsArraySetVector(arrayLCW, 4, Vector(-2.0, -2.0, 0.0));
    // LCCW
    int arrayLCCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate I Left CCW"
    );
    xsArraySetInt(arrayL, COUNTERCLOCKWISE, arrayLCCW);
    xsArraySetVector(arrayLCCW, 0, Vector(0.0, 1.0, 0.0));
    xsArraySetVector(arrayLCCW, 1, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayLCCW, 2, Vector(0.0, 2.0, 0.0));
    xsArraySetVector(arrayLCCW, 3, Vector(1.0, -1.0, 0.0));
    xsArraySetVector(arrayLCCW, 4, Vector(-2.0, 2.0, 0.0));
}

/// Initializes the rotation arrays for the J, L, S, T, and Z Tetrominos.
void _initRotationX() {
    int rotationHeader = xsArrayCreateInt(NUM_DIRS, 0, "Rotate X Offsets");
    rotateXId = rotationHeader;

    int arrayU = xsArrayCreateInt(2, 0, "Rotate X Up");
    xsArraySetInt(rotationHeader, UP, arrayU);
    // UCW
    int arrayUCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate X Up CW"
    );
    xsArraySetInt(arrayU, CLOCKWISE, arrayUCW);
    xsArraySetVector(arrayUCW, 1, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayUCW, 2, Vector(-1.0, -1.0, 0.0));
    xsArraySetVector(arrayUCW, 3, Vector(2.0, 0.0, 0.0));
    xsArraySetVector(arrayUCW, 4, Vector(2.0, -1.0, 0.0));
    // UCCW
    int arrayUCCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate X Up CCW"
    );
    xsArraySetInt(arrayU, COUNTERCLOCKWISE, arrayUCCW);
    xsArraySetVector(arrayUCCW, 1, Vector(0.0, 1.0, 0.0));
    xsArraySetVector(arrayUCCW, 2, Vector(-1.0, 1.0, 0.0));
    xsArraySetVector(arrayUCCW, 3, Vector(2.0, 0.0, 0.0));
    xsArraySetVector(arrayUCCW, 4, Vector(2.0, 1.0, 0.0));

    int arrayR = xsArrayCreateInt(2, 0, "Rotate X Right");
    xsArraySetInt(rotationHeader, RIGHT, arrayR);
    // RCW
    int arrayRCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate X Right CW"
    );
    xsArraySetInt(arrayR, CLOCKWISE, arrayRCW);
    xsArraySetVector(arrayRCW, 1, Vector(0.0, 1.0, 0.0));
    xsArraySetVector(arrayRCW, 2, Vector(1.0, 1.0, 0.0));
    xsArraySetVector(arrayRCW, 3, Vector(-2.0, 0.0, 0.0));
    xsArraySetVector(arrayRCW, 4, Vector(-2.0, 1.0, 0.0));
    // RCCW
    int arrayRCCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate X Right CCW"
    );
    xsArraySetInt(arrayR, COUNTERCLOCKWISE, arrayRCCW);
    xsArraySetVector(arrayRCCW, 1, Vector(0.0, 1.0, 0.0));
    xsArraySetVector(arrayRCCW, 2, Vector(1.0, 1.0, 0.0));
    xsArraySetVector(arrayRCCW, 3, Vector(-2.0, 0.0, 0.0));
    xsArraySetVector(arrayRCCW, 4, Vector(-2.0, 1.0, 0.0));

    int arrayD = xsArrayCreateInt(2, 0, "Rotate X Down");
    xsArraySetInt(rotationHeader, DOWN, arrayD);
    // DCW
    int arrayDCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate X Down CW"
    );
    xsArraySetInt(arrayD, CLOCKWISE, arrayDCW);
    xsArraySetVector(arrayDCW, 1, Vector(0.0, 1.0, 0.0));
    xsArraySetVector(arrayDCW, 2, Vector(-1.0, 1.0, 0.0));
    xsArraySetVector(arrayDCW, 3, Vector(2.0, 0.0, 0.0));
    xsArraySetVector(arrayDCW, 4, Vector(2.0, 1.0, 0.0));
    // DCCW
    int arrayDCCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate X Down CCW"
    );
    xsArraySetInt(arrayD, COUNTERCLOCKWISE, arrayDCCW);
    xsArraySetVector(arrayDCCW, 1, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayDCCW, 2, Vector(-1.0, -1.0, 0.0));
    xsArraySetVector(arrayDCCW, 3, Vector(2.0, 0.0, 0.0));
    xsArraySetVector(arrayDCCW, 4, Vector(2.0, -1.0, 0.0));

    int arrayL = xsArrayCreateInt(2, 0, "Rotate X Left");
    xsArraySetInt(rotationHeader, LEFT, arrayL);
    // LCW
    int arrayLCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate X Left CW"
    );
    xsArraySetInt(arrayL, CLOCKWISE, arrayLCW);
    xsArraySetVector(arrayLCW, 1, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayLCW, 2, Vector(1.0, -1.0, 0.0));
    xsArraySetVector(arrayLCW, 3, Vector(-2.0, 0.0, 0.0));
    xsArraySetVector(arrayLCW, 4, Vector(-2.0, -1.0, 0.0));
    // LCCW
    int arrayLCCW = xsArrayCreateVector(
        NUM_ROTATION_TESTS, Vector(0.0, 0.0, 0.0), "Rotate X Left CCW"
    );
    xsArraySetInt(arrayL, COUNTERCLOCKWISE, arrayLCCW);
    xsArraySetVector(arrayLCCW, 1, Vector(0.0, -1.0, 0.0));
    xsArraySetVector(arrayLCCW, 2, Vector(1.0, -1.0, 0.0));
    xsArraySetVector(arrayLCCW, 3, Vector(-2.0, 0.0, 0.0));
    xsArraySetVector(arrayLCCW, 4, Vector(-2.0, -1.0, 0.0));
}

/// Returns the array id of the test offset vectors to use in rotations.
///
/// Parameters:
///     t: The Tetromino, one of `I`, `J`, `L`, `S`, `T`, and `Z`, but not `O`.
///     d: The current facing direction.
///     r: The rotation direction, one of `CLOCKWISE` or `COUNTERCLOCKWISE`.
int _getRotationTests(int t = 0, int d = 0, int r = 0) {
    int arrayHeaderId = 0;
    if (t == I) {
        arrayHeaderId = rotateIId;
    } else {
        arrayHeaderId = rotateXId;
    }
    int directionArrayId = xsArrayGetInt(arrayHeaderId, d);
    return (xsArrayGetInt(directionArrayId, r));
}

/// Initializes the arrays of Tetromino rotation offsets.
void _initRotationArrays() {
    _initRotationI();
    _initRotationX();
}

/// Returns `true` if the active Tetromino passes the rotation test at index
/// `t` of the array with id `arrayId`.
///
/// Parameters:
///     arrayId: The id of the array containing the tests.
///     d: The target facing direction of the Tetromino.
///     t: The test index, in `0..=4`.
bool _testOneRotation(int arrayId = 0, int d = 0, int t = 0) {
    int row = activeRow;
    int col = activeCol;
    int offsetArrayId = _getOffsets(_activeTetromino());
    Vector testOffset = xsArrayGetVector(arrayId, t);
    int dr = xsVectorGetX(testOffset);
    int dc = xsVectorGetY(testOffset);
    for (k = 0; < NUM_TILES) {
        Vector v = xsArrayGetVector(offsetArrayId, k);
        Vector v2 = _rotateVector(v, d);
        int r = xsVectorGetX(v2) + row + dr;
        int c = xsVectorGetY(v2) + col + dc;
        if (_isInBoundsAndEmpty(r, c) == false) {
            return (false);
        }
    }
    return (true);
}

/// Returns the index of the test that passes, or `-1` if no test passes.
/// The array to test against the currently active Tetromino.
/// Requries the active Tetromino is not an `O`.
///
/// Parameters:
///     r: The direction in which to rotate the active Tetromino.
///         One of `CLOCKWISE` or `COUNTERCLOCKWISE`.
int _testRotations(int r = 0) {
    int d = activeFacing;
    int arrayId = _getRotationTests(_activeTetromino(), d, r);
    int newDir = _rotateDirection(d, r);
    for (t = 0; < NUM_ROTATION_TESTS) {
        if (_testOneRotation(arrayId, newDir, t)) {
            return (t);
        }
    }
    return (-1);
}

// =============================================================================
// Explosion Array
// =============================================================================

/// Initializes the `explode` and `clearExplode` arrays.
void _initExplosionArrays() {
    explodeArrayId = xsArrayCreateBool(VISIBLE, false, "Explode Signal Array");
    clearExplodeArrayId = xsArrayCreateBool(
        VISIBLE, false, "Clear Explode Signal Array"
    );
}

/// Returns `row` translated from the intervale `20..40` to `0..20`.
/// Requires `row in 20..40`.
int _rowToExplode(int row = 0) {
    return (row - VISIBLE);
}

/// Sets the row at index `row` to react to an explosion during the current
/// game tick.
void _setExplode(int row = 0) {
    xsArraySetBool(explodeArrayId, _rowToExplode(row), true);
}

/// Returns `true` if the row at index `row` can start exploding during the
/// current game tick.
bool canExplode(int row = 0) {
    return (xsArrayGetBool(explodeArrayId, _rowToExplode(row)));
}

/// Sets the row at index `row` to stop exploding during the current
/// game tick.
void _setClearExplode(int row = 0) {
    xsArraySetBool(clearExplodeArrayId, _rowToExplode(row), true);
}

/// Returns `true` if the row at index `row` can stop exploding during the
/// current game tick.
bool canClearExplode(int row = 0) {
    if (explodeTimer != 1) {
        return (false);
    }
    return (xsArrayGetBool(clearExplodeArrayId, _rowToExplode(row)));
}

/// Sets all values in the `explode` and `clearExplode` arrays to `false`.
void _clearExplodeArrays() {
    for (row = VISIBLE; < TETRIS_ROWS) {
        int r = _rowToExplode(row);
        xsArraySetBool(explodeArrayId, r, false);
        if (explodeTimer == 0) {
            xsArraySetBool(clearExplodeArrayId, r, false);
        }
    }
}

// =============================================================================
// Scenario Initialization
// =============================================================================

/// Initializes the state data for the xs script.
void initXsState() {
    _initBoard();
    _initUpdate();
    _initSequence();
    _initOffsetArrays();
    _initRotationArrays();
    _initExplosionArrays();
    prevHeld = 0;
    heldTetromino = 0;
    hasPlayedEasterEgg = false;
}

// =============================================================================
// Begin Game
// =============================================================================

/// Initializes the variables used at the start of the game.
void _initGameVariables() {
    xsSetTriggerVariable(SCORE_ID, SCORE_INIT);
    xsSetTriggerVariable(LEVEL_ID, LEVEL_INIT);
    xsSetTriggerVariable(LINES_ID, LINES_INIT);
}

/// Initializes the game state for starting a game of Tetris.
void beginGame() {
    _initGameVariables();
    _resetTimer(LEVEL_INIT);
    _clearBoard();
    _clearUpdate();
    _clearExplodeArrays();
    for (k = 0; < NUM_TETROMINOS) {
        _setSequence(k, k + 1);
        _setSequence(k + NUM_TETROMINOS, k + 1);
    }
    tetrominoSeqIndex = 0;
    difficult = false;
    gameOver = false;
    renderNext = true;
    renderHold = true;
    isHoldLegal = true;
    prevHeld = heldTetromino;
    heldTetromino = 0;
    explodeTimer = 0;
    placePause = false;
    reactTetris = false;
    hasMoved = false;
    hasHeld = false;
    hasFailedHold = false;
    hasLockedDown = false;
}

/// Initializes the state necessary for placing a Tetromino on the board.
/// Requries the update board already is cleared and the Tetromino sequences
/// are already generated.
void beginGameMid() {
    /// There is always room to place the starting Tetromino on a new board.
    /// No need to check if the starting piece and initial drop are legal.
    activeRow = PLACE_ROW + 1;
    activeCol = PLACE_COL;
    activeFacing = PLACE_DIR;

    // For each coordinate in the offset plus the active position, and
    // direction, sets the Invisible Object replacement to `false` and the
    // render object of the current Tetromino to `true`.
    int offsetArrayId = _getOffsets(_activeTetromino());
    for (k = 0; < NUM_TILES) {
        Vector v = xsArrayGetVector(offsetArrayId, k);
        int r = xsVectorGetX(v) + activeRow;
        int c = xsVectorGetY(v) + activeCol;
        _setUpdateValue(r, c, activeFacing, 0, false);
        _setUpdateValue(r, c, activeFacing, _activeTetromino(), true);
    }
}

// =============================================================================
// Game Loop
// =============================================================================

/// Selects the building corresponding to the `action` hotkey index.
///
/// Parameters:
///     action: The hotkey number for the action.
///         Action numbers are the same as those in `action.py`.
///         Requires `action` is in `0..=8`.
void selectBuilding(int action = 0) {
    selected = action;
}

/// Initializes the game state at the start of each game loop.
///
/// Resets the selection variable to be unselected.
/// Clears the second sequence's shuffle state.
/// Clears the render update board.
void initGameLoop() {
    selectBuilding(NO_ACTION);
    canShuffleSecondSeq = false;
    renderNext = false;
    renderHold = false;
    reactTetris = false;
    hasMoved = false;
    hasHeld = false;
    hasFailedHold = false;
    hasLockedDown = false;
    _setAllUpdate(false);
    _clearExplodeArrays();
}

/// Returns `true` if the selected action is to start a new game.
bool canStartNewGame() {
    return (selected == NEW_GAME);
}

/// Returns `true` if the game is over, `false` if the game is ongoing.
bool isGameOver() {
    return (gameOver);
}

/// Returns `true` if the active Tetromino can be translated by the offsets.
///
/// Parameters:
///     dr: The number of rows to move, either `0` or `1`.
///     dc: The number of columns to move, one of `-1`, `0`, or `1`.
bool _canTranslate(int dr = 0, int dc = 0) {
    int offsetArrayId = _getOffsets(_activeTetromino());
    for (k = 0; < NUM_TILES) {
        Vector v = xsArrayGetVector(offsetArrayId, k);
        if (_activeTetromino() != O) {
            v = _rotateVector(v, activeFacing);
        }
        int r = xsVectorGetX(v) + activeRow + dr;
        int c = xsVectorGetY(v) + activeCol + dc;
        if (_isInBoundsAndEmpty(r, c) == false) {
            return (false);
        }
    }
    return (true);

}

/// Returns `true` if the move left action is allowed.
bool _canMoveLeft() {
    return (gameOver == false && selected == MOVE_LEFT && _canTranslate(0, -1));
}

/// Returns `true` if the move right action is allowed.
bool _canMoveRight() {
    return (gameOver == false && selected == MOVE_RIGHT && _canTranslate(0, 1));
}

/// Returns `true` if the rotate clockwise action is allowed.
bool _canRotateClockwise() {
    if (gameOver) {
        return (false);
    }
    if (selected != ROTATE_CLOCKWISE) {
        return (false);
    }
    if (_activeTetromino() == O) {
        return (true);
    }
    return (_testRotations(CLOCKWISE) != -1);
}

/// Returns `true` if the rotate counterclockwise action is allowed.
bool _canRotateCounterclockwise() {
    if (gameOver) {
        return (false);
    }
    if (selected != ROTATE_COUNTERCLOCKWISE) {
        return (false);
    }
    if (_activeTetromino() == O) {
        return (true);
    }
    return (_testRotations(COUNTERCLOCKWISE) != -1);
}

/// Returns `true` if the soft drop action is allowed.
bool _canSoftDrop() {
    return (gameOver == false && selected == SOFT_DROP && _canTranslate(1, 0));
}

/// Returns `true` if the hard drop action is allowed.
bool _canHardDrop() {
    return (gameOver == false && selected == HARD_DROP);
}

/// Returns `true` if the hold action is allowed.
bool _canHold() {
    return (gameOver == false && selected == HOLD && isHoldLegal);
}

/// Sets the update array to replace the rendering of the active tetromino
/// with invisible objects.
void _clearActiveTetrominoRender() {
        int offsetsId = _getOffsets(_activeTetromino());
        for (k = 0; < NUM_TILES) {
            Vector v = xsArrayGetVector(offsetsId, k);
            if (_activeTetromino() != O) {
                v = _rotateVector(v, activeFacing);
            }
            int r = xsVectorGetX(v) + activeRow;
            int c = xsVectorGetY(v) + activeCol;
            _setUpdateValue(r, c, activeFacing, 0, true);
        }
}

/// Translates the position of the active Tetromino and sets the render values
/// in the update array.
///
/// Requires: The translation is legal.
///
/// Parameters:
///     dr: The row offset by which to translate the active Tetromino.
///     dc: The column offset by which to translate the active Tetromino.
void _translatePosition(int dr  = 0, int dc = 0) {
        _clearActiveTetrominoRender();
        int t = _activeTetromino();
        int offsetArrayId = _getActiveOffsets();
        for (k = 0; < NUM_TILES) {
            Vector v = xsArrayGetVector(offsetArrayId, k);
            if (t != O) {
                v = _rotateVector(v, activeFacing);
            }
            int r = xsVectorGetX(v) + activeRow;
            int c = xsVectorGetY(v) + activeCol;
            _setUpdateValue(r + dr, c + dc, activeFacing, 0, false);
            _setUpdateValue(r + dr, c + dc, activeFacing, t, true);
        }
        activeRow = activeRow + dr;
        activeCol = activeCol + dc;
}

/// Rotates the active Tetromino in direction `r`.
///
/// Requires: The rotation is legal.
///
/// Parameters:
///     r: The direction in which to rotate.
///         One of `CLOCKWISE` or `COUNTERCLOCKWISE`.
void _rotatePosition(int r = 0) {
    int offsetArrayId = _getActiveOffsets();
    int newDir = _rotateDirection(activeFacing, r);
    int t = _activeTetromino();
    if (t == O) {
        for (kO = 0; < NUM_TILES) {
            Vector vO = xsArrayGetVector(offsetArrayId, kO);
            int rO = xsVectorGetX(vO) + activeRow;
            int cO = xsVectorGetY(vO) + activeCol;
            _setUpdateValue(rO, cO, activeFacing, 0, true);
            _setUpdateValue(rO, cO, newDir, t, true);
        }
    } else {
        int testIndex = _testRotations(r);
        int testArrayId = _getRotationTests(t, activeFacing, r);
        Vector offset = xsArrayGetVector(testArrayId, testIndex);
        int dr = xsVectorGetX(offset);
        int dc = xsVectorGetY(offset);
        for (k = 0; < NUM_TILES) {
            Vector vUp = xsArrayGetVector(offsetArrayId, k);
            Vector vOld = _rotateVector(vUp, activeFacing);
            int rOld = xsVectorGetX(vOld) + activeRow;
            int cOld = xsVectorGetY(vOld) + activeCol;
            _setUpdateValue(rOld, cOld, activeFacing, 0, true);
            Vector vNew = _rotateVector(vUp, newDir);
            int rNew = xsVectorGetX(vNew) + activeRow + dr;
            int cNew = xsVectorGetY(vNew) + activeCol + dc;
            _setUpdateValue(rNew, cNew, newDir, 0, false);
            _setUpdateValue(rNew, cNew, newDir, t, true);
        }
        activeRow = activeRow + dr;
        activeCol = activeCol + dc;
    }
    activeFacing = newDir;
}

/// Returns `true` if the active `Tetromino` can drop into row `r`.
/// Requires `r > _activeRow()` and for all `r' in _activeRow()..r`,
/// `_canDrop(r') == true`.
bool _canDrop(int r = 0) {
    int offsetsId = _getActiveOffsets();
    // row of its indices.
    int dr = r - activeRow;
    for (k = 0; < NUM_TILES) {
        Vector v = xsArrayGetVector(offsetsId, k);
        if (_activeTetromino() != O) {
            v = _rotateVector(v, activeFacing);
        }
        int row = activeRow + xsVectorGetX(v) + dr;
        int col = activeCol + xsVectorGetY(v);
        if (_isInBoundsAndEmpty(row, col) == false) {
            return (false);
        }
    }
    return (true);
}

/// into which the Tetromino may drop.
int _numDropRows() {
    int r = activeRow + 1;
    // The active Tetrmino can drop its center to all rows in `_activeRow()..r`.
    while (_canDrop(r)) {
        r++;
    }
    return (r - 1 - activeRow);
}

/// Updates the score when `numCleared` lines are cleared.
///
/// Parameters:
///     numCleared: The number of lines cleared, in `0..=4`.
void _updateScore(int numCleared = 0) {
        // TODO T-Spin checks
        // Note that the level is the level before the line clear.
        int oldScore = xsTriggerVariable(SCORE_ID);
        int oldLevel = xsTriggerVariable(LEVEL_ID);
        bool newDifficult = false;
        if (numCleared == 1) {
            xsSetTriggerVariable(SCORE_ID, oldScore + oldLevel * 100);
        } else if (numCleared == 2) {
            xsSetTriggerVariable(SCORE_ID, oldScore + oldLevel * 300);
        } else if (numCleared == 3) {
            xsSetTriggerVariable(SCORE_ID, oldScore + oldLevel * 500);
        } else if (numCleared == 4) {
            int scoreClear4 = 800;
            if (difficult) {
                scoreClear4 = scoreClear4 * 3 / 2;
            }
            xsSetTriggerVariable(SCORE_ID, oldScore + oldLevel * scoreClear4);
            newDifficult = true;
        }
        xsSetTriggerVariable(
            LINES_ID, xsTriggerVariable(LINES_ID) + numCleared
        );
        xsSetTriggerVariable(
            LEVEL_ID,
            (xsTriggerVariable(LINES_ID) + LINES_PER_LEVEL) / LINES_PER_LEVEL
        );
        difficult = newDifficult;
}

/// Checks if any lines are cleared, and if so, explodes them.
/// Returns the number of lines cleared.
int _checkClearLines() {
    int numCleared = 0;
    int row = TETRIS_ROWS - 1;
    int filled = _numFilled(row);
    while (row > 0 && numCleared < 4 && filled > 0) {
        if (filled == TETRIS_COLS) {
            numCleared++;
            _setExplode(row);
            _setClearExplode(row);
        }
        row--;
        filled = _numFilled(row);
    }
    if (numCleared == 4) {
        reactTetris = true;
    }
    _updateScore(numCleared);
    return (numCleared);
}

/// Clears lines and updates the game score after a Tetromino is locked
/// on the board.
void _clearLines() {
    int numCleared = 0;
    int row = TETRIS_ROWS - 1;
    while (row > 0 && numCleared < 4) {
        int filled = _numFilled(row);
        if (filled == 0) {
            break;
        }
        if (filled == TETRIS_COLS) {
            _moveRowsDown(row);
            numCleared++;
        } else {
            row--;
        }
    }
}

/// Activates the next Tetromino, ending the game if there is no room
/// to spawn it
/// Resets the timer to the initial time based on the current level.
void _spawnNextTetromino() {
    if (tetrominoSeqIndex == NUM_TETROMINOS - 1) {
        for (seqK = 0; < NUM_TETROMINOS) {
            int value = _getSequence(seqK + NUM_TETROMINOS);
            _setSequence(seqK, value);
            _setSequence(seqK + NUM_TETROMINOS, seqK + 1);
        }
        canShuffleSecondSeq = true;
        tetrominoSeqIndex = 0;
    } else {
        tetrominoSeqIndex = tetrominoSeqIndex + 1;
    }

    // If any of the offsets of placing a new piece or of moving it down
    // one row are occupied, then the player is defeated.
    activeRow = PLACE_ROW;
    activeCol = PLACE_COL;
    activeFacing = PLACE_DIR;

    // Checks for defeats.
    int offsetsId1 = _getActiveOffsets();
    for (k1 = 0; < NUM_TILES) {
        Vector v1 = xsArrayGetVector(offsetsId1, k1);
        int r1 = xsVectorGetX(v1) + activeRow;
        int c1 = xsVectorGetY(v1) + activeCol;
        if (_isInBoundsAndEmpty(r1, c1) == false) {
            gameOver = true;
        }
    }

    // Moves the Tetromino down.
    activeRow = activeRow + 1;
    int offsetsId2 = _getActiveOffsets();
    for (k2 = 0; < NUM_TILES) {
        Vector v2 = xsArrayGetVector(offsetsId2, k2);
        int r2 = xsVectorGetX(v2) + activeRow;
        int c2 = xsVectorGetY(v2) + activeCol;
        if (_isInBoundsAndEmpty(r2, c2) == false) {
            gameOver = true;
        }
        _setUpdateValue(
            r2, c2, activeFacing, _activeTetromino(), true
        );
    }
    renderNext = true;
    _resetTimer(xsTriggerVariable(LEVEL_ID));
}

/// Places the active Tetromino on the board `numRows` below its current
/// position.
///
/// Requires that the Tetromino legally can drop `numRows` rows.
///
/// Parameters:
///     numRows: The number of rows beneath the current position at which to
///         place the active Tetromino on the board. Nonnegative.
void _lockDown(int numRows = 0) {
    _clearActiveTetrominoRender();
    // Sets the update array to render the new position.
    for (k = 0; < NUM_TILES) {
        Vector v = xsArrayGetVector(_getActiveOffsets(), k);
        if (_activeTetromino() != O) {
            v = _rotateVector(v, activeFacing);
        }
        int r = xsVectorGetX(v) + activeRow + numRows;
        int c = xsVectorGetY(v) + activeCol;
        _setUpdateValue(r, c, activeFacing, 0, false);
        _setUpdateValue(r, c, activeFacing, _activeTetromino(), true);
        _setBoardValue(r, c, activeFacing, _activeTetromino());
    }
    isHoldLegal = true;
    hasLockedDown = true;
    activeRow = activeRow + numRows;
    int numCleared = _checkClearLines();
    if (numCleared > 0) {
        explodeTimer = EXPLODE_DELAY;
    } else {
        placePause = true;
    }
}

/// Updates the game state.
/// Call in a trigger after storing user input in the `Selected` variable
/// and before executing the render triggers.
void update() {
    if (placePause) {
        placePause = false;
        _spawnNextTetromino();
    } else if (explodeTimer > 1) {
        explodeTimer--;
    } else if (explodeTimer == 1) {
        explodeTimer--;
        _clearLines();
        _spawnNextTetromino();
    } else {
        if (_canMoveLeft()) {
            _translatePosition(0, -1);
            hasMoved = true;
            if (timer == 0) {
                timer = 1;
            }
        } else if (_canMoveRight()) {
            _translatePosition(0, 1);
            hasMoved = true;
            if (timer == 0) {
                timer = 1;
            }
        } else if (_canRotateClockwise()) {
            _rotatePosition(CLOCKWISE);
            hasMoved = true;
            if (timer == 0) {
                timer = 1;
            }
        } else if (_canRotateCounterclockwise()) {
            _rotatePosition(COUNTERCLOCKWISE);
            hasMoved = true;
            if (timer == 0) {
                timer = 1;
            }
        } else if (_canSoftDrop()) {
            _translatePosition(1, 0);
            int scoreSoft = xsTriggerVariable(SCORE_ID);
            int levelSoft = xsTriggerVariable(LEVEL_ID);
            xsSetTriggerVariable(
                SCORE_ID, scoreSoft + SOFT_DROP_MULTIPLIER * levelSoft
            );
            hasMoved = true;
            _resetTimer(levelSoft);
        } else if (_canHardDrop()) {
            int numRows = _numDropRows();
            xsSetTriggerVariable(
                SCORE_ID,
                xsTriggerVariable(SCORE_ID)
                + HARD_DROP_MULTIPLIER
                * xsTriggerVariable(LEVEL_ID)
                * numRows
            );
            _lockDown(numRows);
        } else if (_canHold()) {
            _clearActiveTetrominoRender();
            prevHeld = heldTetromino;
            heldTetromino = _activeTetromino();
            if (prevHeld != 0) {
                _setSequence(tetrominoSeqIndex, prevHeld);
                tetrominoSeqIndex = tetrominoSeqIndex - 1;
            }
            isHoldLegal = false;
            hasHeld = true;
            renderHold = true;
            _spawnNextTetromino();
        } else if (gameOver == false && selected == HOLD && isHoldLegal == false) {
            hasFailedHold = true;
        }
        if (timer == 0) {
            if (_canTranslate(1, 0)) {
                _translatePosition(1, 0);
                _resetTimer(xsTriggerVariable(LEVEL_ID));
            } else {
                _lockDown(0);
            }
        } else {
            timer = timer - 1;
        }
    }
}

// =============================================================================
// Rendering and Reactions
// =============================================================================

/// Returns `true` if the tile at position `(row, col)` facing direction `d`
/// can be rendered with a Tetromino of shape `t`.
///
/// The tile can be rendered if it is updated during the current game tick.
/// Requires that `update` is already called for the current game tick.
///
/// Parameters
///     r: The row index, in `0..TETRIS_ROWS`.
///     c: The column index, in `0..TETRIS_COLS`.
///     d: The facing direction, in `0..NUM_DIRS`.
///     t: The value to render, in `0..=7`.
bool canRenderTile(int r = 0, int c = 0, int d = 0, int t = 0) {
    return (_getUpdateValue(r, c, d, t));
}

/// Returns `true` if the next piece indicated by `index` should have its units
/// replaced with units of shape `t`, `false` if not.
/// The next board should be updated to display Tetromino `t` if `t` is at
/// the board's sequence index and the board does not currently
/// contain that Tetromino.
///
/// Parameters:
///     index: Either 0, 1, or 2, indicating which of the next 3 pieces
///         to place.
///     t: The Tetromino value for the piece to render. In `1..=7`.
bool canRenderNext(int index = 0, int t = 0) {
    if (renderNext == false) {
        return (false);
    }
    int currentIndex = tetrominoSeqIndex + index;
    int currentTetromino = _getSequence(currentIndex);
    int nextIndex = currentIndex + 1;
    int nextTetromino = _getSequence(nextIndex);
    return (t == nextTetromino && currentTetromino != nextTetromino);
}

/// Returns `true` if the Hold unit should have its units replaced with
/// units of shape `t`, `false` if not.
///
/// Parameters:
///     t: The Tetromino value for the piece to render, or `0` if the hold
///         should be rendered with Invisible Objects. In `0..=7`.
bool canRenderHold(int t = 0) {
    if (renderHold == false) {
        return (false);
    }
    // Only re-renders if the Tetromino is different.
    return (heldTetromino == t && prevHeld != t);
}

/// Returns `true` if a player scores a Tetris on this game tick.
bool canReactTetris() {
    return (reactTetris);
}

/// Returns `true` if the game can react to a move action on this game tick.
bool canReactMove() {
    return (hasMoved);
}

/// Returns `true` if the game can react to a hold action on this game tick.
bool canReactHold() {
    return (hasHeld);
}

/// Returns `true` if the game can react to a failed hold action on this game
/// tick.
bool canReactHoldFail() {
    return (hasFailedHold);
}

/// Returns `true` if the game can react to the game ending on this game tick.
bool canReactGameOver() {
    return (gameOver && (xsGetTime() < TWO_HOURS || hasPlayedEasterEgg));
}

/// Returns `true` if the game can react to the game ending on this game tick
/// by using a special easter-egg reaction.
bool canReactGameOverEasterEgg() {
    return (
        gameOver && hasPlayedEasterEgg == false && xsGetTime() >= TWO_HOURS
    );
}

/// Acknowledges that the game has reacted to an Easter Egg game over.
void ackGameOverEasterEgg() {
    hasPlayedEasterEgg = true;
}

/// Returns `true` if the game can react to a Tetromino locking down on this
/// game tick, `false` if not.
bool canReactLockdown() {
    return (hasLockedDown);
}

/// Scratch test function.
void test() {

}
