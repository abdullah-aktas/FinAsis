# WorldGenerator: Prosedürel dünya üretimi
class WorldGenerator:
    def __init__(self, name, seed=0):
        self.name = name
        self.seed = seed
        self.map = self.generate_map()

    def generate_map(self):
        # Basit grid tabanlı harita
        size = 10 + (self.seed % 10)
        tiles = []
        for x in range(size):
            for y in range(size):
                tile_type = "market" if (x + y) % 5 == 0 else "house"
                tiles.append({"x": x, "y": y, "type": tile_type})
        return tiles


def generate_worlds(names):
    return [WorldGenerator(name, i * 42) for i, name in enumerate(names)]
