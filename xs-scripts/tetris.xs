// xs file for Aoe2 Tetris

// Swaps the values stored in variables with ids `id0` and `id1`.
void swap(int id0 = 0, int id1 = 0) {
    int value0 = xsTriggerVariable(id0);
    int value1 = xsTriggerVariable(id1);
    xsSetTriggerVariable(id0, value1);
    xsSetTriggerVariable(id1, value0);
}
