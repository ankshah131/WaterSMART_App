from matplotlib import cm
from matplotlib.colors import to_hex

def get_palette(name, n):
    """Convert a matplotlib colormap to a list of hex colors."""
    return [to_hex(c) for c in cm.get_cmap(name, n)(range(n))]

blues_palette = get_palette('Blues', 9)      # 9 shades from light to dark
ylorrd_palette = get_palette('YlOrRd', 7)    # 7 shades from yellow to red
