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

/// The number of elements in the xs array.
const int NUM_XS_ARRAY_ELEMENTS = 8;

/// The id of the variable that holds the player's score.
const int SCORE_ID = 1;

/// The initial player score.
const int SCORE_INIT = 0;

/// The id of the variable that holds the player's level.
const int LEVEL_ID = 2;
/// The initial level.

const int LEVEL_INIT = 0;

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

/// The initial row when a new Tetromino is spawned: one above the highest
/// visible row.
const int PLACE_ROW = 19;

/// The initial column when a new Tetromino is spawned: the left-center column.
const int PLACE_COL = 4;

/// The initial upwards facing direction of a new Tetromino when spawned.
const int PLACE_DIR = 0;

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

/// Constants to represent the directions in which Tetrominos can move and face.
/// The same as the enum values assigned in `direction.py`.
const int UP = 0;
const int RIGHT = 1;
const int DOWN = 2;
const int LEFT = 3;

/// The number of facing directions.
const int NUM_DIRS = 4;

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

/// Write a chat message containing the values of the array.
///
/// Parameters:
///     arrayId: The id of the array to print.
void _chatArray(int arrayId = 0) {
    string output = "[";
    string delim = "";
    int n = xsArrayGetSize(arrayId);
    int k = 0;
    while (k != n) {
        int value = xsArrayGetInt(arrayId, k);
        output = output + delim + value;
        delim = ", ";
        k = k + 1;
    }
    output = output + "]";
    xsChatData("Array ID: %d", arrayId);
    xsChatData("Array Length: %d", n);
    xsChatData(output);
}

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
    int c = 0;
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
    int r = 0;
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

/// Returns `true` if the board is empty at the indicated tile and direction.
///
/// Parameters:
///     r: The row index, in `0..TETRIS_ROWS`.
///     c: The column index, in `0..TETRIS_COLS`.
///     d: The facing direction, in `0..NUM_DIRS`.
bool _isTileEmpty(int r = 0, int c = 0, int d = 0) {
    return (_tileContains(r, c, d, 0));
}

/// Clears the game board.
/// Essentially sets `board[r][c][d] = 0` for all rows, columns, and directions.
void _clearBoard() {
    int r = 0;
    for (r = 0; < TETRIS_ROWS) {
        int c = 0;
        for (c = 0; < TETRIS_COLS) {
            int d = 0;
            for (d = 0; < NUM_DIRS) {
                _setBoardValue(r, c, d, 0);
            }
        }
    }
}

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
    int d = 0;
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
    int c = 0;
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
    int r = 0;
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
    int r = 0;
    for (r = 0; < TETRIS_ROWS) {
        int c = 0;
        for (c = 0; < TETRIS_COLS) {
            int d = 0;
            for (d = 0; < NUM_DIRS) {
                _setUpdateValue(r, c, d, 0, true);
                int t = 1;
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
    int r = 0;
    for (r = 0; < TETRIS_ROWS) {
        int c = 0;
        for (c = 0; < TETRIS_COLS) {
            int d = 0;
            for (d = 0; < NUM_DIRS) {
                int t = 0;
                for (t = 0; < NUM_TETROMINOS + 1) {
                    _setUpdateValue(r, c, d, t, b);
                }
            }
        }
    }
}

/// Initializes the Tetromino Sequence.
///
/// Note this funciton does not shuffle the sequences. Shuffling is performed
/// by the scenario triggers.
void _initSequence() {
    // Creates the array and assigns it to the xs-state.
    int seqId = xsArrayCreateInt(2 * NUM_TETROMINOS, 0, "Tetromion Sequence");
    _setState(TETROMINO_SEQUENCE_INDEX, seqId);
    // Assigns initial values to the array.
    int k = 0;
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

/// Initializes the array of xs data and stores it's id in the variable
/// with id `XS_ARRAY_VAR_ID`.
void initXsArray() {
    int arrayId = xsArrayCreateInt(NUM_XS_ARRAY_ELEMENTS, 0, "xs State Array");
    xsSetTriggerVariable(XS_ARRAY_VAR_ID, arrayId);
    _initBoard();
    _initUpdate();
    _initSequence();
}

/// Swaps the values stored in variables with ids `id0` and `id1`.
void _swap(int id0 = 0, int id1 = 0) {
    int value0 = xsTriggerVariable(id0);
    int value1 = xsTriggerVariable(id1);
    xsSetTriggerVariable(id0, value1);
    xsSetTriggerVariable(id1, value0);
}

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
// TODO needs to be called before the render functions...
void beginGameMid() {
    /// There is always room to place the starting Tetromino on a new board.
    /// No need to check if the starting piece and initial drop are legal.
    _setState(ROW_INDEX, PLACE_ROW + 1);
    _setState(COL_INDEX, PLACE_COL);
    _setState(DIR_INDEX, PLACE_DIR);
    _setUpdateValue(
        _activeRow(), _activeCol(), _activeFacing(), 0, false
    );
    _setUpdateValue(
        _activeRow(), _activeCol(), _activeFacing(), _activeTetromino(), true
    );
}

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

/// Returns `true` if the move left action is allowed.
bool _canMoveLeft() {
    // TODO handle multiple offsets
    return (_getSelectedBuilding() == MOVE_LEFT && _activeCol() > 0);
}

/// Returns `true` if the move right action is allowed.
bool _canMoveRight() {
    // TODO handle multiple offsets
    return (
        _getSelectedBuilding() == MOVE_RIGHT && _activeCol() < TETRIS_COLS - 1
    );
}

/// Returns `true` if the rotate clockwise action is allowed.
bool _canRotateClockwise() {
    // TODO handle offsets
    return (_getSelectedBuilding() == ROTATE_CLOCKWISE);
}

/// Returns `true` if the rotate counterclockwise action is allowed.
bool _canRotateCounterclockwise() {
    // TODO handle offsets
    return (_getSelectedBuilding() == ROTATE_COUNTERCLOCKWISE);
}

/// Returns `true` if the soft drop action is allowed.
bool _canSoftDrop() {
    return (false);
}

/// Returns `true` if the hard drop action is allowed.
bool _canHardDrop() {
    return (false);
}

/// Returns `true` if the hold action is allowed.
bool _canHold() {
    return (false);
}

/// Updates the game state.
/// Call in a trigger after storing user input in the `Selected` variable
/// and before executing the render triggers.
void update() {
    // if any entry in the update array is nonempty here, then there's a problem
    // TODO implement
    if (_canMoveLeft()) {
        _setUpdateValue(
            _activeRow(), _activeCol(), _activeFacing(), 0, true
        );
        _setUpdateValue(
            _activeRow(),
            _activeCol() - 1,
            _activeFacing(),
            _activeTetromino(),
            true
        );
        _setState(COL_INDEX, _activeCol() - 1);
    } else if (_canMoveRight()) {
        _setUpdateValue(_activeRow(), _activeCol(), _activeFacing(), 0, true);
        _setUpdateValue(
            _activeRow(),
            _activeCol() + 1,
            _activeFacing(),
            _activeTetromino(),
            true
        );
        _setState(COL_INDEX, _activeCol() + 1);
    } else if (_canRotateClockwise()) {
        int cw = (_activeFacing() + 1) % NUM_DIRS;
        _setUpdateValue(_activeRow(), _activeCol(), _activeFacing(), 0, true);
        _setUpdateValue(_activeRow(), _activeCol(), cw, _activeTetromino(), true);
        _setState(DIR_INDEX, cw);
    } else if (_canRotateCounterclockwise()) {
        // TODO check how `%` works with negative numbers.
        int ccw = _activeFacing() - 1;
        if (ccw == -1) {
            ccw = 3;
        }
        _setUpdateValue(_activeRow(), _activeCol(), _activeFacing(), 0, true);
        _setUpdateValue(_activeRow(), _activeCol(), ccw, _activeTetromino(), true);
        _setState(DIR_INDEX, ccw);
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

/// TODO specify
bool canRenderNext() {
    // TODO implement
    return (false);
}

/// TODO specify
bool canRenderHold() {
    // TODO implement
    return (false);
}

/// Scratch test function.
void test() {
    // int seqId = _getState(TETROMINO_SEQUENCE_INDEX);
    // _chatArray(seqId);
    // _setBoardValue(BOARD_INDEX, 20, 1, 1, 4);
    // _setBoardValue(BOARD_INDEX, 21, 1, 1, 4);
    // _setBoardValue(BOARD_INDEX, 20, 2, 1, 4);
    // _setBoardValue(BOARD_INDEX, 21, 2, 1, 4);
    // _setBoardValue(BOARD_INDEX, 20, 3, 0, 5);
    // _setBoardValue(BOARD_INDEX, 20, 4, 1, 5);
    // _setBoardValue(BOARD_INDEX, 20, 5, 2, 5);
    // _setBoardValue(BOARD_INDEX, 20, 6, 3, 5);
    // _setBoardValue(BOARD_INDEX, 21, 6, 0, 6);
    // _setBoardValue(BOARD_INDEX, 20, 7, 0, 6);
    // _setBoardValue(BOARD_INDEX, 21, 7, 0, 6);
    // _setBoardValue(BOARD_INDEX, 21, 8, 0, 6);
}
