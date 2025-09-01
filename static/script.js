document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("restaurantSearch");
    const restaurantCards = document.querySelectorAll(".restaurant-card");

    searchInput.addEventListener("input", () => {
        const query = searchInput.value.toLowerCase().trim();
        const queryWords = query.split(/\s+/); // boşluklara göre kelimelere ayır

        restaurantCards.forEach(card => {
            const name = card.querySelector(".restaurant-name").textContent.toLowerCase();
            const locationText = card.querySelector("p i.bi-geo-alt").parentElement.textContent.toLowerCase();
            const [city, state] = locationText.split(',').map(s => s.trim());

            // Tüm kelimelerden herhangi biri eşleşirse göster
            const match = queryWords.some(word => 
                name.includes(word) || city.includes(word) || state.includes(word)
            );

            card.style.display = match ? "block" : "none";
        });
    });
});
