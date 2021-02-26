"""Interfaces between scenario triggers and the Tetris xs script."""


from typing import Optional, Sequence


class ScriptCaller:
    """
    An instance manages calls to an xs script.

    The method `init_xs_array` must be called before any other xs function.
    All other methods raise an assertion error in a debug build if this
    method has not been called.
    """

    def __init__(self):
        """
        Initializes a new script caller.

        Parameters:
            variables: The scenario variables with which the script calls
                can interact.
        """
        self._suffix = -1  # Increments at the start of every method.

    def init_xs_array(self):
        """
        Initializes the scenario's xs state array.

        Must be called in a trigger effect immediately upon the scenario's
        launch.
        """
        self._suffix += 1
        return "\n".join(
            [
                f"void _{self._suffix}() " + "{",
                "    initXsArray();",
                "}",
            ]
        )

    def _call_function(
        self, name: str, params: Optional[Sequence[str]] = None
    ) -> str:
        """
        Returns a string to Call the xs script function with name `name`
        and parameters with string values given in `params`.
        Essentially calls `name(param[0], param[1], ..., param[n])`.

        Checks that self._suffix is nonnegative in order to ensure that
        the xs state array is initialized.

        Parameters:
            name: The name of the xs function in `Tetris.xs`.
            params: The parameters to pass to the function.
        Returns:
            A string for a trigger condition or effect to call the xs
            function `name` with the parameters `params`.
        """
        assert self._suffix > -1
        if not params:
            params = []
        self._suffix += 1
        return "\n".join([
            f"void _{self._suffix}() " + "{",
            f"    {name}({', '.join(params)});",
            "}",
        ])

    def begin_game(self):
        """"""
        return self._call_function("beginGame")
