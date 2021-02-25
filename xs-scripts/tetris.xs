/// xs file for Aoe2 Tetris.

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

/// Each `are_emptyn` function returns `true` if all of the tiles are empty.
///
/// There are multiple functions to support checking multiple points without
/// needing to pass array arguments.
///
/// Parameters:
///     `idn`: The id of the variable holding the tile index.
///     `placen`: The digit place holding the column, in `0..=4`.
bool are_empty1(int id1 = 0, int place1 = 0) {
    return (digitEquals(id1, place1, 0));
}
bool are_empty2(int id1 = 0, int place1 = 0, int id2 = 0, int place2 = 0) {
    return (are_empty1(id1, place1) && are_empty1(id2, place2));
}
bool are_empty3(
    int id1 = 0, int place1 = 0,
    int id2 = 0, int place2 = 0,
    int id3 = 0, int place3 = 0
) {
    return (are_empty2(id1, place1, id2, place2) && are_empty1(id3, place3));
}
bool are_empty4(
    int id1 = 0, int place1 = 0,
    int id2 = 0, int place2 = 0,
    int id3 = 0, int place3 = 0,
    int id4 = 0, int place4 = 0
) {
    return (
        are_empty3(id1, place1, id2, place2, id3, place3)
            && are_empty1(id4, place4)
    );
}
