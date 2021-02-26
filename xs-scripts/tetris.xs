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

/// The number of elements in the xs array.
const int NUM_XS_ARRAY_ELEMENTS = 2;

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

/// Constants to represent Tetromino shapes.
/// The same as the enum values assigned in `tetromino.py`.
const int I = 5;
const int J = 7;
const int L = 1;
const int O = 4;
const int S = 3;
const int T = 6;
const int Z = 2;

/// Constants to represent the directions in which Tetrominos can move and face.
/// The same as the enum values assigned in `direction.py`.
const int UP = 0;
const int RIGHT = 1;
const int DOWN = 2;
const int LEFT = 3;

/// The number of facing directions.
const int NUM_DIRS = 4;

/// The xs-index of the game board array.
const int BOARD_INDEX = 0;

/// The xs-index of the previous board state.
const int PREV_INDEX = 1;

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

/// Returns the string name of a board based on its index.
/// `boardName(BOARD_INDEX) == "Board"`
/// `boardName(PREV_INDEX) == "Prev"`
///
/// Parameters:
///     boardIndex: Either `BOARD_INDEX` or `PREV_INDEX`
string _boardName(int boardIndex = 0) {
    if (boardIndex == BOARD_INDEX) {
        return ("Board");
    } else {
        return ("Prev");
    }
    return ("This line should not be reached.");
}

/// Initializes an empty tile in a game board row
//  and returns the tile's array id.
/// See the specification of `_initBoard`.
///
/// Parameters:
///     boardIndex: Either `BOARD_INDEX` or `PREV_INDEX`.
///     r: The row index.
///     c: The column index.
int _initBoardTile(int boardIndex = 0, int r = 0, int c = 0) {
    string name = _boardName(boardIndex);
    int tileId = xsArrayCreateInt(
        NUM_DIRS, 0, "Tile " + name + "[" + r + "][" + c + "]"
    );
    return (tileId);
}

/// Initializes an empty row in a game board and returns the row's array id.
/// See the specification of `_initBoard`.
///
/// Parameters:
///     boardIndex: Either `BOARD_INDEX` or `PREV_INDEX`.
///     r: The row index.
int _initBoardRow(int boardIndex = 0, int r = 0) {
    string name = _boardName(boardIndex);
    int rowId = xsArrayCreateInt(TETRIS_COLS, 0, name + " Row " + r);
    int c = 0;
    for (c = 0; < TETRIS_COLS) {
        int tileId = _initBoardTile(boardIndex, r, c);
        xsArraySetInt(rowId, c, tileId);
    }
    return (rowId);
}

/// Initializes an empty game board and set the id of this board's array
/// to the xs-index `boardIndex`.
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
///     boardIndex: Either `BOARD_INDEX` or `PREV_INDEX`. Controls which board
///         is initialized.
void _initBoard(int boardIndex = 0) {
    string name = _boardName(boardIndex);
    int boardId = xsArrayCreateInt(TETRIS_ROWS, 0, "Outer " + name + " Array");
    _setState(boardIndex, boardId);
    int r = 0;
    for (r = 0; < TETRIS_ROWS) {
        int rowId = _initBoardRow(boardIndex, r);
        xsArraySetInt(boardId, r, rowId);
    }
}

/// Returns a value from the state board or previous state board.
///
/// Parameters:
///     boardIndex: Either `BOARD_INDEX` or `PREV_INDEX`. Controls which board
///         is initialized.
///     r: The row index, in `0..TETRIS_ROWS`.
///     c: The column index, in `0..TETRIS_COLS`.
///     d: The facing direction, in `0..NUM_DIRS`.
int _getBoardValue(int boardIndex = 0, int r = 0, int c = 0, int d = 0) {
    int boardId = _getState(boardIndex);
    int rowId = xsArrayGetInt(boardId, r);
    int tileId = xsArrayGetInt(rowId, c);
    return (xsArrayGetInt(tileId, d));
}

/// Sets a value in the state board or previous state board.
///
/// Parameters:
///     boardIndex: Either `BOARD_INDEX` or `PREV_INDEX`. Controls which board
///         is initialized.
///     r: The row index, in `0..TETRIS_ROWS`.
///     c: The column index, in `0..TETRIS_COLS`.
///     d: The facing direction, in `0..NUM_DIRS`.
///     t: The value to set, in `0..=7`.
void _setBoardValue(
    int boardIndex = 0, int r = 0, int c = 0, int d = 0, int t = 0
) {
    int boardId = _getState(boardIndex);
    int rowId = xsArrayGetInt(boardId, r);
    int tileId = xsArrayGetInt(rowId, c);
    xsArraySetInt(tileId, d, t);
}

/// Clears the board with outer array id `boardId`.
/// Essentially sets `board[r][c][d] = 0` for all rows, columns, and directions.
///
/// Parameters:
///    boardId: The outer array id of the board to clear.
void _clearBoard(int boardId = 0) {
    int r = 0;
    for (r = 0; < TETRIS_ROWS) {
        int c = 0;
        for (c = 0; < TETRIS_COLS) {
            int d = 0;
            for (d = 0; < NUM_DIRS) {
                _setBoardValue(boardId, r, c, d);
            }
        }
    }
}

/// Sets all tile values to empty in the current and previous boards in order
/// to clear them before starting a new game.
void _clearBoards() {
    _clearBoard(_getState(BOARD_INDEX));
    _clearBoard(_getState(PREV_INDEX));
}

/// Initializes the array of xs data and stores it's id in the variable
/// with id `XS_ARRAY_VAR_ID`.
void initXsArray() {
    int arrayId = xsArrayCreateInt(NUM_XS_ARRAY_ELEMENTS, 0, "xs State Array");
    xsSetTriggerVariable(XS_ARRAY_VAR_ID, arrayId);
    _initBoard(BOARD_INDEX);
    _initBoard(PREV_INDEX);
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
    _clearBoards();
    // TODO implement
}

/// Returns `true` if the move left action is allowed.
bool _canMoveLeft() {
    return (false);
}

/// TODO specify and implement
bool _canMoveRight() {
    return (false);
}

/// TODO specify and implement
bool _canRotateClockwise() {
    return (false);
}

/// TODO specify and implement
bool _canRotateCounterclockwise() {
    return (false);
}

/// TODO specify and implement
bool _canSoftDrop() {
    return (false);
}

/// TODO specify and implement
bool _canHardDrop() {
    return (false);
}

/// TODO specify and implement
bool _canHold() {
    return (false);
}

/// Updates the game state.
/// Call in a trigger after storing user input in the `Selected` variable
/// and before executing the render triggers.
void update() {
    // TODO implement
}

/// TODO specify
bool canRenderTile() {
    // TODO implement
    return (false);
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

/// Function for testing xs scripts.
void test() {
    // xsChatData("Hello!", 0);
    _initBoard();
}
