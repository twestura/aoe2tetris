/// xs file for Aoe2 Tetris.
///
/// This script uses an array to store the state of a game of Tetris.
/// The indicies in this array are referred to as xs-indices throughout
/// this documentation.
/// This array must be initialized using the `initXsArray` function
/// immediately when the Tetris scenario begins.
/// Maybe one day xs will have structs. And monads. :)

// FE documentation:
// https://www.forgottenempires.net/age-of-empires-ii-definitive-edition/xs-scripting-in-age-of-empires-ii-definitive-edition

// Aoe3 xs documentation:
// https://eso-community.net/viewtopic.php?p=436182

// There is array functionality that isn't listed in the FE documentation.
// There are five types: bool, int, float, string, and vector
// xsArraySetType(arrayID, index, value)
// xsArrayGetType(arrayID, index)
// xsArrayGetSize(arrayID)


/// The id of the variable that holds the xs array.
///
/// This implementation of arrays in xs script always assigns 0 as the id of
/// the first created array. But to avoid relying on this behavior, the array
/// id is saved in a scenario variable. The id is accessed in order to obtain
/// the array id using the `_getXsArrayId` function.
/// But more typically the `_getState` and `_setState` functions should be
/// preferred to using the id directly.
const int XS_ARRAY_VAR_ID = 0;

/// The xs-index of the game board array.
const int BOARD_INDEX = 0;

/// The xs-index of the board state array.
const int UPDATE_INDEX = 1;

/// The xs-index of the active Tetromino's row.
const int ROW_INDEX = 2;

/// The xs-index of the active Tetromino's col.
const int COL_INDEX = 3;

/// The xs-index of the active Tetromino's facing direction.
const int DIR_INDEX = 4;

/// The xs-index of the length 14-Tetromino sequence.
const int TETROMINO_SEQUENCE_INDEX = 5;

/// The xs-index of the current index of the Tetromino sequence.
const int TETROMINO_SEQUENCE_INDEX_INDEX = 6;

/// The xs-index of the selected hotkey and action to perform.
const int SELECTED_INDEX = 7;

/// The xs-index of the Tetromino offset arrays.
const int TETROMINO_OFFSETS_INDEX = 8;

/// The xs-index of the I Tetromino rotation offsets.
const int ROTATE_I_INDEX = 9;

/// The xs-index of the J, L, S, T, and Z Tetromino rotation offsets.
const int ROTATE_X_INDEX = 10;

/// The number of elements in the xs array.
const int NUM_XS_ARRAY_ELEMENTS = 11;

/// The id of the variable that holds the player's score.
const int SCORE_ID = 1;

/// The initial player score.
const int SCORE_INIT = 0;

/// The id of the variable that holds the player's level.
const int LEVEL_ID = 2;
/// The initial level.

/// The initial starting level without clearing any rows.
const int LEVEL_INIT = 1;

/// The id of the variable that holds the number of cleared lines.
const int LINES_ID = 3;

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
// xs State Array
// =============================================================================

/// Returns the array id of the xs state array.
int _getXsArrayId() {
    return (xsTriggerVariable(XS_ARRAY_VAR_ID));
}

/// Returns the value at index `index` of the xs-state array.
///
/// Parameters:
///     index: The array index from which to retreive a value.
///         Requires `0 <= index < NUM_XS_ARRAY_ELEMENTS`.
int _getState(int index = 0) {
    int arrayId = _getXsArrayId();
    return (xsArrayGetInt(arrayId, index));
}

/// Sets the state element at index `index` to `value`.
///
/// Parameters:
///     index: The array index from which to retreive a value.
///         Requires `0 <= index < NUM_XS_ARRAY_ELEMENTS`.
///     value: The value to assign in the state array.
void _setState(int index = 0, int value = 0) {
    int arrayId = _getXsArrayId();
    xsArraySetInt(arrayId, index, value);

}

/// Chats the xs state array.
void _chatStateArray() {
    _chatArray(_getXsArrayId());
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
/// to the xs-index `BOARD_INDEX`.
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
///
/// Parameters:
///     boardIndex: Either `BOARD_INDEX` or `UPDATE_INDEX`. Controls which board
///         is initialized.
void _initBoard() {
    int boardId = xsArrayCreateInt(TETRIS_ROWS, 0, "Outer Board Array");
    _setState(BOARD_INDEX, boardId);
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
    int boardId = _getState(BOARD_INDEX);
    int rowId = xsArrayGetInt(boardId, r);
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
    int boardId = _getState(BOARD_INDEX);
    int rowId = xsArrayGetInt(boardId, r);
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
    _setState(UPDATE_INDEX, updateId);
    for (r = 0; < TETRIS_ROWS) {
        int rowId = _initUpdateRow(r);
        xsArraySetInt(updateId, r, rowId);
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
    int updateId = _getState(UPDATE_INDEX);
    int rowId = xsArrayGetInt(updateId, r);
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
    int updateId = _getState(UPDATE_INDEX);
    int rowId = xsArrayGetInt(updateId, r);
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
                for (t0 = 0; <= NUM_TETROMINOS) {
                    _setUpdateValue(r, c, d, t0, false);
                }
                _setUpdateValue(r, c, d, value, true);
                _setUpdateValue(r - 1, c, d, 0, true);
                for (t1 = 1; <= NUM_TETROMINOS) {
                    _setUpdateValue(r - 1, c, d, t1, false);
                }
            }
        }
        r--;
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
    // Creates the array and assigns it to the xs-state.
    int seqId = xsArrayCreateInt(2 * NUM_TETROMINOS, 0, "Tetromino Sequence");
    _setState(TETROMINO_SEQUENCE_INDEX, seqId);
    // Assigns initial values to the array.
    for (k = 0; < NUM_TETROMINOS) {
        xsArraySetInt(seqId, k, k + 1);
        xsArraySetInt(seqId, k + NUM_TETROMINOS, k + 1);
    }
}

/// Returns the value at `index` of the Tetromino sequence.
///
/// Parameters:
///     index: The index from which to retrieve a value.
///         Requires `0 <= index < 2 * NUM_TETROMINOS`.
int _getSequence(int index = 0) {
    int seqId = _getState(TETROMINO_SEQUENCE_INDEX);
    return (xsArrayGetInt(seqId, index));
}

/// Returns the value at `index` of the Tetromino sequence to `value`.
///
/// Parameters:
///     index: The index from which to retrieve a value.
///         Requires `0 <= index < 2 * NUM_TETROMINOS`.
///     value: The value to assign in the sequence.
void _setSequence(int index = 0, int value = 0) {
    int seqId = _getState(TETROMINO_SEQUENCE_INDEX);
    xsArraySetInt(seqId, index, value);
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

// =============================================================================
// Position State Information
// =============================================================================

/// Returns the value at the active index of the Tetromino sequence.
int _activeTetromino() {
    int index = _getState(TETROMINO_SEQUENCE_INDEX_INDEX);
    return (_getSequence(index));
}

/// Returns the row coordinate of the active Tetromino.
int _activeRow() {
    return (_getState(ROW_INDEX));
}

/// Returns the column coordinate of the active Tetromino.
int _activeCol() {
    return (_getState(COL_INDEX));
}

/// Returns the facing direction of the active Tetromino.
int _activeFacing() {
    return (_getState(DIR_INDEX));
}

/// Writes a debug chat message to display position information for the
/// active Tetromino.
void _chatPositionInfo() {
    xsChatData(
        "Active: ("
        + _activeRow()
        + ", "
        + _activeCol()
        + ") "
        + _activeFacing()
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
// xsState[TETROMINO_OFFSETS_INDEX] = [offsetsL, offsetsZ, ... offsetsJ];

/// Returns the array id of the offsets for Tetromino t.
///
/// Parameters:
///     t: The Tetromion, in `1..=7`.
int _getOffsets(int t = 0) {
    int containerId = _getState(TETROMINO_OFFSETS_INDEX);
    int index = t - 1;
    return (xsArrayGetInt(containerId, index));
}

/// Initalizes the Tetromino offset arrays.
void _initOffsetArrays() {
    int arrayId = xsArrayCreateInt(NUM_TETROMINOS, 0, "Tetromino Offset Array");
    _setState(TETROMINO_OFFSETS_INDEX, arrayId);
    for (t = 1; <= NUM_TETROMINOS) {
        int offsetArrayId = xsArrayCreateVector(
            NUM_TILES, Vector(0.0, 0.0, 0.0), "Offset Array " + t
        );
        int index = t - 1;
        xsArraySetInt(arrayId, index, offsetArrayId);
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
    int offsetArrayContainerId = _getState(TETROMINO_OFFSETS_INDEX);
    for (t = 0; < NUM_TETROMINOS) {
        xsChatData("Array " + t);
        int arrayId = xsArrayGetInt(offsetArrayContainerId, t);
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
    _setState(ROTATE_I_INDEX, rotationHeader);

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
    _setState(ROTATE_X_INDEX, rotationHeader);

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
        arrayHeaderId = _getState(ROTATE_I_INDEX);
    } else {
        arrayHeaderId = _getState(ROTATE_X_INDEX);
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
    int row = _activeRow();
    int col = _activeCol();
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
    int d = _activeFacing();
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
// Scenario Initialization
// =============================================================================

/// Initializes the array of xs data and stores it's id in the variable
/// with id `XS_ARRAY_VAR_ID`.
void initXsArray() {
    int arrayId = xsArrayCreateInt(NUM_XS_ARRAY_ELEMENTS, 0, "xs State Array");
    xsSetTriggerVariable(XS_ARRAY_VAR_ID, arrayId);
    _initBoard();
    _initUpdate();
    _initSequence();
    _initOffsetArrays();
    _initRotationArrays();
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
    _clearBoard();
    _clearUpdate();
    _setState(TETROMINO_SEQUENCE_INDEX_INDEX, 0);
}

/// Initializes the state necessary for placing a Tetromino on the board.
/// Requries the update board already is cleared and the Tetromino sequences
/// are already generated.
void beginGameMid() {
    int row = PLACE_ROW + 1;
    int col = PLACE_COL;
    int dir = PLACE_DIR;

    /// There is always room to place the starting Tetromino on a new board.
    /// No need to check if the starting piece and initial drop are legal.
    _setState(ROW_INDEX, row);
    _setState(COL_INDEX, col);
    _setState(DIR_INDEX, dir);

    // For each coordinate in the offset plus the active position, and
    // direction, sets the Invisible Object replacement to `false` and the
    // render object of the current Tetromino to `true`.
    int offsetArrayId = _getOffsets(_activeTetromino());
    for (k = 0; < NUM_TILES) {
        Vector v = xsArrayGetVector(offsetArrayId, k);
        int r = xsVectorGetX(v) + row;
        int c = xsVectorGetY(v) + col;
        _setUpdateValue(r, c, dir, 0, false);
        _setUpdateValue(r, c, dir, _activeTetromino(), true);
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
    _setState(SELECTED_INDEX, action);
}

/// Returns the int representing the hotkey action of the
/// selected building, or `0` if no building is selected.
int _getSelectedBuilding() {
    return (_getState(SELECTED_INDEX));
}

/// Initializes the game state at the start of each game loop.
///
/// Resets the selection variable to be unselected.
/// Saves the previous game state.
void initGameLoop() {
    selectBuilding(0);
    _setAllUpdate(false);
}

/// Returns `true` if the selected action is to start a new game.
bool canStartNewGame() {
    return (_getSelectedBuilding() == NEW_GAME);
}

/// Returns `true` if the active Tetromino can be translated by the offsets.
///
/// Parameters:
///     dr: The number of rows to move, either `0` or `1`.
///     dc: The number of columns to move, one of `-1`, `0`, or `1`.
bool _canTranslate(int dr = 0, int dc = 0) {
    int row = _activeRow();
    int col = _activeCol();
    int d = _activeFacing();
    int offsetArrayId = _getOffsets(_activeTetromino());
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

/// Returns `true` if the move left action is allowed.
bool _canMoveLeft() {
    return (_getSelectedBuilding() == MOVE_LEFT && _canTranslate(0, -1));
}

/// Returns `true` if the move right action is allowed.
bool _canMoveRight() {
    return (_getSelectedBuilding() == MOVE_RIGHT && _canTranslate(0, 1));
}

/// Returns `true` if the rotate clockwise action is allowed.
bool _canRotateClockwise() {
    if (_getSelectedBuilding() != ROTATE_CLOCKWISE) {
        return (false);
    }
    if (_activeTetromino() == O) {
        return (true);
    }
    return (_testRotations(CLOCKWISE) != -1);
}

/// Returns `true` if the rotate counterclockwise action is allowed.
bool _canRotateCounterclockwise() {
    if (_getSelectedBuilding() != ROTATE_COUNTERCLOCKWISE) {
        return (false);
    }
    if (_activeTetromino() == O) {
        return (true);
    }
    return (_testRotations(COUNTERCLOCKWISE) != -1);
}

/// Returns `true` if the soft drop action is allowed.
bool _canSoftDrop() {
    return (_getSelectedBuilding() == SOFT_DROP && _canTranslate(1, 0));
}

/// Returns `true` if the hard drop action is allowed.
bool _canHardDrop() {
    return (_getSelectedBuilding() == HARD_DROP);
}

/// Returns `true` if the hold action is allowed.
bool _canHold() {
    // TODO handle multiple holds without resetting
    return (_getSelectedBuilding() == HOLD);
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
        int offsetArrayId = _getOffsets(_activeTetromino());
        int row = _activeRow();
        int col = _activeCol();
        int d = _activeFacing();
        int t = _activeTetromino();
        // Sets the currently active tiles to be rendered as Invisible Objects.
        for (k0 = 0; < NUM_TILES) {
            Vector v = xsArrayGetVector(offsetArrayId, k0);
            Vector vRotated = _rotateVector(v, d);
            int r0 = xsVectorGetX(vRotated) + row;
            int c0 = xsVectorGetY(vRotated) + col;
            _setUpdateValue(r0, c0, d, 0, true);
        }
        // Sets the newly active tiles to be rendered as units.
        // Overwrites and previous sets of `true` Invisible Objects to `false`
        // from the previous loop.
        for (k1 = 0; < NUM_TILES) {
            Vector v1 = xsArrayGetVector(offsetArrayId, k1);
            Vector v1Rotated = _rotateVector(v1, d);
            int r1 = xsVectorGetX(v1Rotated) + row;
            int c1 = xsVectorGetY(v1Rotated) + col;
            _setUpdateValue(r1 + dr, c1 + dc, d, 0, false);
            _setUpdateValue(r1 + dr, c1 + dc, d, t, true);
        }
        _setState(ROW_INDEX, row + dr);
        _setState(COL_INDEX, col + dc);
}

/// Rotates the active Tetromino in direction `r`.
///
/// Requires: The rotation is legal.
///
/// Parameters:
///     r: The direction in which to rotate.
///         One of `CLOCKWISE` or `COUNTERCLOCKWISE`.
void _rotatePosition(int r = 0) {
    int offsetArrayId = _getOffsets(_activeTetromino());
    int row = _activeRow();
    int col = _activeCol();
    int d = _activeFacing();
    int newDir = _rotateDirection(d, r);
    int t = _activeTetromino();
    if (t == O) {
        for (kO = 0; < NUM_TILES) {
            Vector vO = xsArrayGetVector(offsetArrayId, kO);
            int rO = xsVectorGetX(vO) + row;
            int cO = xsVectorGetY(vO) + col;
            _setUpdateValue(rO, cO, d, 0, true);
            _setUpdateValue(rO, cO, newDir, t, true);
        }
    } else {
        int testIndex = _testRotations(r);
        int testArrayId = _getRotationTests(t, d, r);
        Vector offset = xsArrayGetVector(testArrayId, testIndex);
        int dr = xsVectorGetX(offset);
        int dc = xsVectorGetY(offset);
        for (k = 0; < NUM_TILES) {
            Vector vUp = xsArrayGetVector(offsetArrayId, k);
            Vector vOld = _rotateVector(vUp, d);
            int rOld = xsVectorGetX(vOld) + row;
            int cOld = xsVectorGetY(vOld) + col;
            _setUpdateValue(rOld, cOld, d, 0, true);
            Vector vNew = _rotateVector(vUp, newDir);
            int rNew = xsVectorGetX(vNew) + row + dr;
            int cNew = xsVectorGetY(vNew) + col + dc;
            _setUpdateValue(rNew, cNew, newDir, t, true);
        }
        _setState(ROW_INDEX, row + dr);
        _setState(COL_INDEX, col + dc);
    }
    _setState(DIR_INDEX, newDir);
}

/// Returns `true` if the active `Tetromino` can drop into row `r`.
/// Requires `r > _activeRow()` and for all `r' in _activeRow()..r`,
/// `_canDrop(r') == true`.
bool _canDrop(int r = 0) {
    int offsetsId = _getOffsets(_activeTetromino());
    int d = _activeFacing();
    // row of its indices.
    int dr = r - _activeRow();
    for (k = 0; < NUM_TILES) {
        Vector vUp = xsArrayGetVector(offsetsId, k);
        Vector v = _rotateVector(vUp, d);
        int row = _activeRow() + xsVectorGetX(v) + dr;
        int col = _activeCol() + xsVectorGetY(v);
        if (_isInBoundsAndEmpty(row, col) == false) {
            return (false);
        }
    }
    return (true);
}

/// Returns the number of rows beneath the active Tetromino that have an opening
/// into which the Tetromino may drop.
int _numDropRows() {
    int r = _activeRow() + 1;
    // The active Tetrmino can drop its center to all rows in `_activeRow()..r`.
    while (_canDrop(r)) {
        r++;
    }
    return (r - 1 - _activeRow());
}

/// Updates the game state.
/// Call in a trigger after storing user input in the `Selected` variable
/// and before executing the render triggers.
void update() {
    if (_canMoveLeft()) {
        _translatePosition(0, -1);
    } else if (_canMoveRight()) {
        _translatePosition(0, 1);
    } else if (_canRotateClockwise()) {
        _rotatePosition(CLOCKWISE);
    } else if (_canRotateCounterclockwise()) {
        _rotatePosition(COUNTERCLOCKWISE);
    } else if (_canSoftDrop()) {
        _translatePosition(1, 0);
        int scoreSoft = xsTriggerVariable(SCORE_ID);
        int levelSoft = xsTriggerVariable(LEVEL_ID);
        xsSetTriggerVariable(
            SCORE_ID, scoreSoft + SOFT_DROP_MULTIPLIER * levelSoft
        );
    } else if (_canHardDrop()) {
        int numRows = _numDropRows();
        int scoreHard = xsTriggerVariable(SCORE_ID);
        int levelHard = xsTriggerVariable(LEVEL_ID);
        xsSetTriggerVariable(
            SCORE_ID, scoreHard + HARD_DROP_MULTIPLIER * levelHard * numRows
        );

        // Drops the Tetromino.
        int offsetsId = _getOffsets(_activeTetromino());
        for (k0 = 0; < NUM_TILES) {
            Vector v0 = xsArrayGetVector(offsetsId, k0);
            Vector v0Rotated = _rotateVector(v0, _activeFacing());
            int r0 = xsVectorGetX(v0Rotated) + _activeRow();
            int c0 = xsVectorGetY(v0Rotated) + _activeCol();
            _setUpdateValue(r0, c0, _activeFacing(), 0, true);
        }
        for (k1 = 0; < NUM_TILES) {
            Vector v1 = xsArrayGetVector(offsetsId, k1);
            Vector v1Rotated = _rotateVector(v1, _activeFacing());
            int r1 = xsVectorGetX(v1Rotated) + _activeRow() + numRows;
            int c1 = xsVectorGetY(v1Rotated) + _activeCol();
            _setUpdateValue(r1, c1, _activeFacing(), 0, false);
            _setUpdateValue(r1, c1, _activeFacing(), _activeTetromino(), true);
            _setBoardValue(r1, c1, _activeFacing(), _activeTetromino());
        }
        _setState(ROW_INDEX, _activeRow() + numRows);

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
        // TODO make pieces explode or something fun

        // clear lines and update the score
        // TODO implement

        // Spawns a new Tetromino.
        // For now this is a hack to reuse multiple pieces.
        // Need to re-randomize the sequence as a TODO.
        int seqIndex = _getState(TETROMINO_SEQUENCE_INDEX_INDEX);
        if (seqIndex == NUM_TETROMINOS - 1) {
            for (seqK = 0; < NUM_TETROMINOS) {
                int value0 = _getSequence(seqK);
                int value1 = _getSequence(seqK + NUM_TETROMINOS);
                _setSequence(seqK, value1);
                _setSequence(seqK + NUM_TETROMINOS, value0);
            }
            // TODO generate new sequence... this requires more triggers
            _setState(TETROMINO_SEQUENCE_INDEX_INDEX, 0);
        } else {
            _setState(TETROMINO_SEQUENCE_INDEX_INDEX, seqIndex + 1);
        }
        _setState(ROW_INDEX, PLACE_ROW);
        _setState(COL_INDEX, PLACE_COL);
        _setState(DIR_INDEX, PLACE_DIR);

        // if any of the offsets of placing a new piece or of moving it down
        // one row are occupied, then the player is defeated.

        // TODO check for defeat, then move Tetromino down if not defeated.

        _setState(ROW_INDEX, PLACE_ROW + 1);
        int offsetsId2 = _getOffsets(_activeTetromino());
        for (k2 = 0; < NUM_TILES) {
            Vector v2 = xsArrayGetVector(offsetsId2, k2);
            int r2 = xsVectorGetX(v2) + _activeRow();
            int c2 = xsVectorGetY(v2) + _activeCol();
            _setUpdateValue(
                r2, c2, _activeFacing(), _activeTetromino(), true
            );
        }
    } else if (_canHold()) {
        // TODO implement
    }
}

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
///
/// Parameters:
///     index: Either 1, 2, or 3, indicating which of the next 3 pieces
///         to place.
///     t: The Tetromino value for the piece to render. In `1..=7`.
bool canRenderNext(int index = 0, int t = 0) {
    // TODO implement
    return (false);
}

/// Returns `true` if the Hold unit should have its units replaced with
/// units of shape `t`, `false` if not.
///
/// Parameters:
///     t: The Tetromino value for the piece to render, or `0` if the hold
///         should be rendered with Invisible Objects. In `0..=7`.
bool canRenderHold(int t = 0) {
    // TODO implement
    return (false);
}

/// Scratch test function.
void test() {
    // float mid = 0.0 - 2.0;
    // Vector v = Vector(1.0, -2.0, 0.0);
    // int x = xsVectorGetX(v);
    // int y = xsVectorGetY(v);
    // xsChatData("(" + x + ", " + y + ")");
    // Vector v1 = Vector(1.0, 2.0, 0.0);
    // float x1 = xsVectorGetX(v1);
    // xsChatData("" + (x == x1));
    // int offsetArrayContainerId = _getState(TETROMINO_OFFSETS_INDEX);
    // for (t = 0; < NUM_TETROMINOS) {
    //     xsChatData("Array " + t);
    //     int arrayId = xsArrayGetInt(offsetArrayContainerId, t);
    //     for (j = 0; < NUM_TILES) {
    //         Vector v = xsArrayGetVector(arrayId, j);
    //         xsChatData(_vecStr(v));
    //     }
    // }
    // string s = "\"";
    // xsChatData("\"");
}
