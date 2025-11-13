# AIManager: Basit ticaret botları ve dinamik NPC hareketleri
class TradeBot:
    def __init__(self, name, location):
        self.name = name
        self.location = location
    def analyze_market(self, price, volume):
        # Basit karar mantığı
        if price < 100 and volume > 10:
            return 'Al'
        elif price > 200:
            return 'Sat'
        return 'Bekle'

def create_npcs(locations):
    return [TradeBot(f'NPC_{i+1}', loc) for i, loc in enumerate(locations)]
