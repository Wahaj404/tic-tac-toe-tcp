class Board:
    def __init__(self, s=None):
        self.grid = [[' ' for _ in range(3)] for _ in range(3)]
        if s is None:
            return
        if len(s) != 9:
            raise ValueError('Invalid string for grid initialization')
        for i in range(3):
            for j in range(3):
                self[i, j] = s[i * 3 + j]

    def __setitem__(self, coord, token):
        if token not in 'xo':
            raise ValueError(f'{token} is an invalid value for grid box')
        i, j = coord
        if self.grid[i][j] != ' ':
            raise ValueError(f'{coord} is already marked')
        self.grid[i][j] = token

    def __getitem__(self, coord):
        i, j = coord
        return self.grid[i][j]

    def __str__(self):
        return str(self.grid)

    def __repr__(self):
        return ''.join(token for row in self.grid for token in row)

    def _check_rows(self):
        for i in range(3):
            if self.grid[i][0] != ' ' and (self.grid[i][0] == self.grid[i][1] == self.grid[i][2]):
                return self.grid[i][0]
        return None

    def _check_cols(self):
        for i in range(3):
            if self.grid[0][i] != ' ' and (self.grid[0][i] == self.grid[1][i] == self.grid[2][i]):
                return self.grid[0][i]
        return None

    def _check_diags(self):
        if self.grid[0][0] != ' ' and (self.grid[0][0] == self.grid[1][1] == self.grid[2][2]):
            return self.grid[0][0]
        if self.grid[2][0] != ' ' and (self.grid[2][0] == self.grid[1][1] == self.grid[0][2]):
            return self.grid[0][0]
        return None

    def winner(self):
        w = self._check_rows()
        if w is None:
            w = self._check_cols()
        if w is None:
            w = self._check_diags()
        return w
