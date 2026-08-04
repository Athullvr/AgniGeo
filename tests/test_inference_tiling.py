from scripts.run_inference import tile_windows


def test_tile_windows_cover_edges():
    windows = list(tile_windows(10, 10, 6, 2))
    assert windows[0] == (0, 0, 6, 6)
    assert any(row + rows == 10 and col + cols == 10 for row, col, rows, cols in windows)
