document.addEventListener("DOMContentLoaded", function (evt) {
    evt.preventDefault()
    const map = L.map('map').setView([20, 0], 2);  // keskittää kartan keskelle

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    }).addTo(map);



    let geojsonLayer;

    // ensimmäinen maa joka ääriviivat hohtaa
    const countriesToHighlight = ['Argentina'];
    weatherUpdate(-34.603722, -58.381592)
    // Fetchaa ja lataa GeoJSON datan kaikille maille että saadaan ääriviivat tehtyä
    fetch('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json')
        .then(response => response.json())
        .then(data => {
            geojsonLayer = L.geoJson(data, {
                onEachFeature: (feature, layer) => {
                    layer.bindPopup(feature.properties.name);

                    // ääriviivoittaa salitun maan
                    if (countriesToHighlight.includes(feature.properties.name)) {
                        highlightCountry(layer, feature);
                    } else {
                        resetCountryStyle(layer);
                    }
                }
            }).addTo(map);
        })
        .catch(error => {
            console.error("Error loading GeoJSON data:", error);
        });

    // Funktio ääriviivoittaa maat ja säätää värit
    function highlightCountry(layer) {
        layer.setStyle({
            color: '#ffd52c',        // reunus
            weight: 3,               // reunus paksuus
            fillColor: '#191919',    // täyte väri
            fillOpacity: 0.7        // läpinäkyvyys
        });

        // saa highlithed countryn reunat
        const bounds = layer.getBounds();

        // smootti fransformaatio
        map.flyToBounds(bounds, {
            duration: 0,  // aika lentää seuraavaan paikkaan
            maxZoom: 5    // kuinka korkealla käy
        });
    }

    // fukntio resettaa highlight countriesin
    function resetCountryStyle(layer) {
        layer.setStyle({
            color: '#000000',
            weight: 1,
            fillColor: '#191919',
            fillOpacity: 0.3
        });
    }

    // Highlittaa valitun maan
    window.highlightCountryByName = function(countryName) {
        geojsonLayer.eachLayer(function (layer) {
            if (layer.feature.properties.name === countryName) {
                highlightCountry(layer, layer.feature);
            } else {
                resetCountryStyle(layer);
            }
        });
    };
});

// päivittää säätilan latitudin ja longtitudin perusteella
function weatherUpdate(latitude,longitude) {
    api="524990caf48ba5a43ea93849d5964612"
    let info = "https://api.openweathermap.org/data/2.5/weather?lat="+latitude+"&lon="+longitude+"&appid="+api+"&units=metric"
    console.log(info)
    fetch(info)
        .then(r => r.json())
        .then(data => {
            console.log(data);
            showWeather(data)
            showWeatherImage(data)
        })
// näyttää nykyisen paikan säätilan
function showWeather(data) {
    const description = data.weather[0].description;
    const temperature = data.main.temp;
    const heading = document.getElementById("weather-text");

    heading.innerHTML = `${description} ${temperature}°C`;
}

// näyttää openweather apista löytyvän sää kuvan kyseiseen paikkaan
function showWeatherImage(data) {
    const imageUrl = "https://openweathermap.org/img/wn/" + data.weather[0].icon + "@2x.png";
    const imageElement = document.getElementById("weather-image");
    imageElement.src = imageUrl;
    imageElement.alt = data.weather[0].description;
}}
// päivittää levelin aina uudeksi kun endistytään
function updateLevel(data){
    const level = data
    const heading = document.getElementById("current-level")
    heading.innerHTML = `Level: ${level+1}`
}
// kello joka laskee ylöspäin
function updateClock() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const seconds = String(now.getSeconds()).padStart(2, "0");

    const timeString = `${hours}:${minutes}:${seconds}`;
    const timeElement = document.getElementById("current-time");

    if (timeElement) {
        timeElement.textContent = timeString;
    }
}

// kello päivittyy joka sekunti
setInterval(updateClock, 1000);
updateClock(); // alkukäynnistys
