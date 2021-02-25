/// xs file for Aoe2 Tetris.

// FE documentation:
// https://www.forgottenempires.net/age-of-empires-ii-definitive-edition/xs-scripting-in-age-of-empires-ii-definitive-edition

// Aoe3 xs documentation:
// https://eso-community.net/viewtopic.php?p=436182

// There is array functionality that isn't listed in the FE documentation.
// There are five types: bool, int, float, string, and vector
// xsArraySetType(arrayID, index, value)
// xsArrayGetType(arrayID, index)
// xsArrayGetSize(arrayID)

/// This is ugly... but the constants are hard-coded so that they don't have
/// to be passed as parameters.
/// The file `variables.py` must use these constants in adding the variables
/// to the trigger manager.
const int TILES0A = 0;
const int TILES0B = 1;
const int TILES1A = 2;
const int TILES1B = 3;
const int TILES2A = 4;
const int TILES2B = 5;
const int TILES3A = 6;
const int TILES3B = 7;
const int TILES4A = 8;
const int TILES4B = 9;
const int TILES5A = 10;
const int TILES5B = 11;
const int TILES6A = 12;
const int TILES6B = 13;
const int TILES7A = 14;
const int TILES7B = 15;
const int TILES8A = 16;
const int TILES8B = 17;
const int TILES9A = 18;
const int TILES9B = 19;
const int TILES10A = 20;
const int TILES10B = 21;
const int TILES11A = 22;
const int TILES11B = 23;
const int TILES12A = 24;
const int TILES12B = 25;
const int TILES13A = 26;
const int TILES13B = 27;
const int TILES14A = 28;
const int TILES14B = 29;
const int TILES15A = 30;
const int TILES15B = 31;
const int TILES16A = 32;
const int TILES16B = 33;
const int TILES17A = 34;
const int TILES17B = 35;
const int TILES18A = 36;
const int TILES18B = 37;
const int TILES19A = 38;
const int TILES19B = 39;
const int TILES20A = 40;
const int TILES20B = 41;
const int TILES21A = 42;
const int TILES21B = 43;
const int TILES22A = 44;
const int TILES22B = 45;
const int TILES23A = 46;
const int TILES23B = 47;
const int TILES24A = 48;
const int TILES24B = 49;
const int TILES25A = 50;
const int TILES25B = 51;
const int TILES26A = 52;
const int TILES26B = 53;
const int TILES27A = 54;
const int TILES27B = 55;
const int TILES28A = 56;
const int TILES28B = 57;
const int TILES29A = 58;
const int TILES29B = 59;
const int TILES30A = 60;
const int TILES30B = 61;
const int TILES31A = 62;
const int TILES31B = 63;
const int TILES32A = 64;
const int TILES32B = 65;
const int TILES33A = 66;
const int TILES33B = 67;
const int TILES34A = 68;
const int TILES34B = 69;
const int TILES35A = 70;
const int TILES35B = 71;
const int TILES36A = 72;
const int TILES36B = 73;
const int TILES37A = 74;
const int TILES37B = 75;
const int TILES38A = 76;
const int TILES38B = 77;
const int TILES39A = 78;
const int TILES39B = 79;
const int SEQ0_ID = 80;
const int SEQ1_ID = 81;
const int SCORE_ID = 82;
const int ROW_ID = 83;
const int COL_ID = 84;
const int FACING_ID = 85;
const int SEQ_INDEX_ID = 86;
const int SELECTED_ID = 87;

/// Constants to represent Tetromino shapes.
/// The same as the enum values assigned in `tetromino.py`.
const int I = 5;
const int J = 7;
const int L = 1;
const int O = 4;
const int S = 3;
const int T = 6;
const int Z = 2;

/// Returns `x` raised to the power `e`.
/// Requires `x` and `e` both nonnegative, and at most one is zero.
int exp(int x = 1, int n = 0) {
    int result = 1;
    int y = x;
    int m = n;
    while (m > 0) {
        if (m % 2 == 1) {
            result = result * y;
        }
        m = m / 2;
        y = y * y;
    }
    return (result);
}

/// Returns the digit `place` digits from the rightmost digit in the variable
/// with id `id`.
///
/// Requries `place` in `0..7`.
///
/// Parameters:
///     id0: the id of the scenario variable to access
///     place: the number of places, starting from 0, from the rightmost digit
///         of that varible's value at which to extract the digit
int getDigit(int id = 0, int place = 0) {
    return (xsTriggerVariable(id) / exp(10, place) % 10);
}

/// Returns `true` if the variable value at the given index has the given value.
///
/// Parameters:
///     id: the id of the scenario variable to check
///     place: the number of digits from the rightmost digit at which to
///         compare values
///     value: the value to which to compare
/// Returns:
///     Whether `value` equals the indicated digit of the variable with id `id`.
bool digitEquals(int id = 0, int place = 0, int value = 0) {
    return (getDigit(id, place) == value);
}

/// Sets the digit at `place` digits from the rightmost digit in the variable
/// with id `id` to `digit`.
///
/// Requires `place` in `0..7`, `digit` in `0..10`.
///
/// Parameters:
///     id0: the id of the scenario variable to mutate
///     place: the number of places, starting from 0, from the rightmost digit
///         of that varible's value at which to extract the digit
///     digit: the single digit number to set in the variable
void setDigit(int id = 0, int place = 0, int digit = 0) {
    int power = exp(10, place);
    int value = xsTriggerVariable(id);
    // Subtracts the old digit and adds the new digit.
    int result = value - (value / power % 10 * power) + (digit * power);
    xsSetTriggerVariable(id, result);
}

/// Swaps the values stored in variables with ids `id0` and `id1`.
void swap(int id0 = 0, int id1 = 0) {
    int value0 = xsTriggerVariable(id0);
    int value1 = xsTriggerVariable(id1);
    xsSetTriggerVariable(id0, value1);
    xsSetTriggerVariable(id1, value0);
}

/// Swaps the digits at indices `i` and `j` of the variable with id `id`.
/// Requires `i` and `j` are in `0..=6`.
void swapDigits(int id = 0, int i = 0, int j = 0) {
    int vali = getDigit(id, i);
    int valj = getDigit(id, j);
    setDigit(id, i, valj);
    setDigit(id, j, vali);
}

/// Each `areEmptyn` function returns `true` if all of the tiles are empty.
///
/// There are multiple functions to support checking multiple points without
/// needing to pass array arguments.
///
/// Parameters:
///     `idn`: The id of the variable holding the tile index.
///     `placen`: The digit place holding the column, in `0..=4`.
bool areEmpty1(int id1 = 0, int place1 = 0) {
    return (digitEquals(id1, place1, 0));
}
bool areEmpty2(int id1 = 0, int place1 = 0, int id2 = 0, int place2 = 0) {
    return (areEmpty1(id1, place1) && areEmpty1(id2, place2));
}
bool areEmpty3(
    int id1 = 0, int place1 = 0,
    int id2 = 0, int place2 = 0,
    int id3 = 0, int place3 = 0
) {
    return (areEmpty2(id1, place1, id2, place2) && areEmpty1(id3, place3));
}
bool areEmpty4(
    int id1 = 0, int place1 = 0,
    int id2 = 0, int place2 = 0,
    int id3 = 0, int place3 = 0,
    int id4 = 0, int place4 = 0
) {
    return (
        areEmpty3(id1, place1, id2, place2, id3, place3)
            && areEmpty1(id4, place4)
    );
}

/// Returns `true` if the move left action is allowed.
bool canMoveLeft() {
    return (false);
}

/// TODO specify and implement
bool canMoveRight() {
    return (false);
}

/// TODO specify and implement
bool canRotateClockwise() {
    return (false);
}

/// TODO specify and implement
bool canRotateCounterclockwise() {
    return (false);
}

/// TODO specify and implement
bool canSoftDrop() {
    return (false);
}

/// TODO specify and implement
bool canHardDrop() {
    return (false);
}

/// TODO specify and implement
bool canHold() {
    return (false);
}
