let winnerModalInstance = null;

document.addEventListener("DOMContentLoaded", function() {
    // 2. CREATE ONCE: Initialize it when the page loads
    const modalElement = document.getElementById('winnerModal');
    if (modalElement) {
        winnerModalInstance = new bootstrap.Modal(modalElement, {
            backdrop: true, // Allow clicking outside to close
            keyboard: true  // Allow ESC key to close
        });
    }
});

function getSurprise() {
    const urlParams = new URLSearchParams(window.location.search);
    const currentPath = window.location.pathname;
    
    if (currentPath.includes('/shops/')) {
        const area = currentPath.split('/')[2];
        if (area) urlParams.append('area', area);
    }

    fetch(`/api/random/?${urlParams.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            document.getElementById('winnerName').innerText = data.name;
            document.getElementById('winnerDetails').innerText = 
                `${data.cuisine ? data.cuisine : 'Food'} • ${data.area.replace('_', ' ').toUpperCase()}`;

            const mapDiv = document.getElementById('winnerMap');
            if (data.latitude && data.longitude) {
                mapDiv.innerHTML = `
                    <a href="https://www.google.com/maps?q=${data.latitude},${data.longitude}" target="_blank" class="btn btn-outline-primary me-2">📍 Google Maps</a>
                    <a href="https://waze.com/ul?ll=${data.latitude},${data.longitude}&navigate=yes" target="_blank" class="btn btn-info text-white">🚗 Waze</a>
                `;
            } else {
                mapDiv.innerHTML = `<button class="btn btn-secondary" disabled>No Map Available</button>`;
            }

            // 3. REUSE: Just show the existing instance!
            if (winnerModalInstance) {
                winnerModalInstance.show();
            }
        });
}