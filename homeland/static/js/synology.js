const refreshIntervalMs = 30000;

const {
    setText,
    applyStatus,
    setProgressBar,
} = window.Homeland;

function createDriveCard(drive) {
    const card = document.createElement("article");
    card.className = "drive-card";

    const statusClass =
        drive.health === "Healthy" ? "healthy" : "warning";

    card.innerHTML = `
        <div class="drive-card-header">
            <h3>${drive.name}</h3>
            <span class="status-pill ${statusClass}">
                ${drive.health}
            </span>
        </div>

        <div class="drive-temperature">
            ${drive.temperature}
        </div>

        <div class="drive-model">
            ${drive.model}
        </div>

        <div class="drive-stats">
            <div class="drive-stat">
                <span>Type</span>
                <strong>${drive.type}</strong>
            </div>

            <div class="drive-stat">
                <span>Bad sectors</span>
                <strong>${drive.bad_sectors}</strong>
            </div>

            <div class="drive-stat">
                <span>Retries</span>
                <strong>${drive.retries}</strong>
            </div>

            <div class="drive-stat">
                <span>Identify failures</span>
                <strong>${drive.identify_failures}</strong>
            </div>
        </div>
    `;

    return card;
}

async function refreshSynology() {
    try {
        const response = await fetch("/api/device/synology");

        if (!response.ok) {
            throw new Error(
                `${response.status} ${response.statusText}`
            );
        }

        const data = await response.json();
        const summary = data.summary || {};
        const storage = data.storage || {};
        const disks = data.disks || [];

        const statusText = document.getElementById(
            "device-status-text"
        );
        const statusDot = document.getElementById(
            "device-status-dot"
        );
        const storageHealth = document.getElementById(
            "storage-health"
        );

        setText("device-status-text", summary.status);
        applyStatus(statusDot, summary.status);

        setText("summary-storage", summary.storage);
        setText("summary-temperature", summary.temperature);
        setText(
            "summary-disk-temperature",
            summary.disk_temperature
        );
        setText("summary-uptime", summary.uptime);

        setText(
            "storage-percent",
            storage.used_percent != null
                ? `${storage.used_percent}%`
                : "Unknown"
        );
        setText("storage-total", storage.total);
        setText("storage-used", storage.used);
        setText("storage-free", storage.free);
        setText(
            "storage-hot-spares",
            storage.hot_spares ?? "Unknown"
        );

        storageHealth.textContent = storage.status;
        applyStatus(storageHealth, storage.status);

        const storageBar = document.getElementById("storage-bar");

        if (storageBar && storage.used_percent != null) {
            storageBar.style.width = `${storage.used_percent}%`;
        }

        setText("drive-count", `${disks.length} drives`);

        const driveGrid = document.getElementById("drive-grid");
        driveGrid.innerHTML = "";

        for (const drive of disks) {
            driveGrid.appendChild(createDriveCard(drive));
        }

        setText(
            "last-updated",
            new Date().toLocaleTimeString()
        );
    } catch (error) {
        console.error("Unable to load Synology data:", error);

        setText("device-status-text", "Offline");

        applyStatus(
            document.getElementById("device-status-dot"),
            "Offline"
        );
    }
}

refreshSynology();
setInterval(refreshSynology, refreshIntervalMs);
