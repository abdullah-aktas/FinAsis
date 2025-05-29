// TradeSim - Modern Finansal Simülasyon Oyunu
// Bu dosya, Ticaretin İzinde ve TradeSim oyunlarının birleşik JS mantığını içerir.
// Temel özellikler: şehirler arası ticaret, görevler, envanter, alış-satış, seviye, deneyim, kaynak yönetimi.

const gameState = {
    gold: 10000,
    goods: [],
    reputation: 0,
    level: 1,
    experience: 0,
    inventory: { capacity: 10, items: [] },
    cities: [
        { name: 'İstanbul', goods: ['Telefon', 'Laptop', 'Ekmek'] },
        { name: 'Ankara', goods: ['Peynir', 'Süt', 'Tablet'] },
        { name: 'İzmir', goods: ['Tişört', 'Pantolon', 'Ayakkabı'] }
    ],
    currentCity: null,
    quests: [],
    weather: 'sunny',
    time: 0
};

// Şehirleri arayüze ekle
function renderCities() {
    const cityList = document.getElementById('city-list');
    cityList.innerHTML = '';
    gameState.cities.forEach(city => {
        const btn = document.createElement('button');
        btn.className = 'list-group-item list-group-item-action';
        btn.textContent = city.name;
        btn.onclick = () => selectCity(city.name);
        cityList.appendChild(btn);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    renderCities();
    updateUI();
});

function selectCity(cityName) {
    gameState.currentCity = cityName;
    showCityMenu(cityName);
}

function showCityMenu(cityName) {
    const city = gameState.cities.find(c => c.name === cityName);
    if (!city) return;
    const menu = document.getElementById('city-menu');
    menu.classList.remove('d-none');
    const goodsList = city.goods.map(good => {
        const price = Math.floor(100 + Math.random() * 200);
        return `<button class="list-group-item list-group-item-action" onclick="buyGood('${good}', '${cityName}', ${price})">${good} - ${price} Altın</button>`;
    }).join('');
    menu.querySelector('.card-body .list-group').innerHTML = goodsList + `<button class='btn btn-secondary mt-3' onclick='closeCityMenu()'>Kapat</button>`;
}

function closeCityMenu() {
    document.getElementById('city-menu').classList.add('d-none');
}

function buyGood(good, cityName, price) {
    if (gameState.inventory.items.length >= gameState.inventory.capacity) {
        alert('Envanteriniz dolu!');
        return;
    }
    if (gameState.gold >= price) {
        gameState.gold -= price;
        gameState.inventory.items.push({ name: good, city: cityName, price: price });
        updateUI();
        addExperience(5);
        alert(`${good} satın alındı! ${price} altın harcandı.`);
    } else {
        alert('Yeterli altınınız yok!');
    }
}

function sellGoods() {
    if (gameState.inventory.items.length === 0) {
        alert('Satacak malınız yok!');
        return;
    }
    let totalEarnings = 0;
    gameState.inventory.items.forEach(item => {
        const price = Math.floor(item.price * (1 + Math.random() * 0.3));
        totalEarnings += price;
    });
    gameState.gold += totalEarnings;
    gameState.reputation += gameState.inventory.items.length;
    addExperience(gameState.inventory.items.length * 2);
    gameState.inventory.items = [];
    updateUI();
    alert(`Tüm mallarınızı sattınız! ${totalEarnings} altın kazandınız.`);
}

function addExperience(amount) {
    gameState.experience += amount;
    if (gameState.experience >= 100) {
        gameState.level++;
        gameState.experience -= 100;
        gameState.inventory.capacity += 2;
        alert(`Tebrikler! Seviye ${gameState.level}'e yükseldiniz!`);
    }
    updateUI();
}

function updateUI() {
    document.getElementById('gold').textContent = gameState.gold;
    document.getElementById('goods').textContent = gameState.inventory.items.map(item => item.name).join(', ') || '-';
    document.getElementById('reputation').textContent = gameState.reputation;
    document.getElementById('level').textContent = gameState.level;
    document.getElementById('experience').textContent = gameState.experience;
} 