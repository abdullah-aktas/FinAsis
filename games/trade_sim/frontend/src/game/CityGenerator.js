// CityGenerator: Prosedürel şehir üretimi
export function generateCity(name, seed = 0) {
  // Basit algoritma: grid tabanlı bina ve yol yerleşimi
  const buildings = [];
  const roads = [];
  const size = 10 + (seed % 10);
  for (let x = 0; x < size; x++) {
    for (let y = 0; y < size; y++) {
      if ((x + y) % 5 === 0) {
        roads.push({ x, y });
      } else {
        buildings.push({ x, y, type: (x % 3 === 0 ? 'market' : 'house') });
      }
    }
  }
  return { name, buildings, roads };
}

export function generateCities(cityNames) {
  return cityNames.map((name, i) => generateCity(name, i * 42));
}
// CityGenerator ile şehirlerin algoritmik olarak oluşturulması ve haritada gösterimi
