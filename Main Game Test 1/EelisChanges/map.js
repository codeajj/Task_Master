document.addEventListener("DOMContentLoaded", function () {
    // Initialize map
    const map = L.map('map').setView([20, 0], 2);  // Center the map on the world view

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    }).addTo(map);



    let geojsonLayer;

    // List of countries to highlight initially
    const countriesToHighlight = ['Argentina'];  // Example country list

    // Fetch and load the GeoJSON data for all countries
    fetch('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json')
        .then(response => response.json())
        .then(data => {
            geojsonLayer = L.geoJson(data, {
                onEachFeature: (feature, layer) => {
                    layer.bindPopup(feature.properties.name);  // Use 'name' property for country names

                    // Initially highlight countries in the 'countriesToHighlight' list
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

    // Function to highlight a country
    function highlightCountry(layer, feature) {
        layer.setStyle({
            color: '#ffd52c',        // Outline color
            weight: 3,               // Outline thickness
            fillColor: '#191919',    // Fill color
            fillOpacity: 0.7        // Transparency
        });

        // Get the bounds of the highlighted country
        const bounds = layer.getBounds();

        // Smoothly pan and zoom to the country
        map.flyToBounds(bounds, {
            duration: 2,  // Duration of the animation (in seconds)
            maxZoom: 5    // Optional: specify a max zoom level
        });
    }

    // Function to reset the highlight style for countries
    function resetCountryStyle(layer) {
        layer.setStyle({
            color: '#000000',
            weight: 1,
            fillColor: '#191919',
            fillOpacity: 0.3
        });
    }

    // Highlights the selected coutnry
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
