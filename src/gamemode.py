
class Gamemode():

    OSU   =  0
    TAIKO =  1
    CATCH =  2
    MANIA =  3

    def __init__(self, value: int):
        if not self.__is_valid(value):
            raise ValueError(f'Invalid gamemode identifier   value = {value}')

        self.value = value


    def __eq__(self, other: "int | Gamemode | None"):
        if type(other) == int:
            return self.value == other

        if type(other) == Gamemode:
            return self.value == other.value

        if type(other) == type(None):
            return False

        raise TypeError(f'Must compare to gamemode indentifier   type = {type(other)}')


    def __ne__(self, other: int):
        return not self.__eq__(other)


    def __str__(self):
        data = {
            Gamemode.OSU   : 'osu!std',
            Gamemode.TAIKO : 'osu!taiko',
            Gamemode.CATCH : 'osu!catch',
            Gamemode.MANIA : 'osu!mania',
        }
        return data[self.value]


    def __is_valid(self, value: int):
        data = [
            Gamemode.OSU,
            Gamemode.TAIKO,
            Gamemode.CATCH,
            Gamemode.MANIA
        ]
        return value in data
