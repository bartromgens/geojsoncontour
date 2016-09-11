from geojson import MultiPolygon


class MP(object):
    """Class for easy MultiPolygon generation.

    Just a helper class for easy identification of
    similar matplotlib.collections.
    """

    def __init__(self, title, color):
        """Destinction based on title and color."""
        self.title = title
        self.color = color
        self.coords = []

    def add_coords(self, coords):
        """Add new coordinate set for MultiPolygon."""
        self.coords.append(coords)

    def __eq__(self, other):
        """Comparison of two MP instances."""
        return (self.title == getattr(other, 'title', False) and
                self.color == getattr(other, 'color', False))

    def mpoly(self):
        """Output of GeoJSON MultiPolygon object."""
        return MultiPolygon(coordinates=[self.coords])
