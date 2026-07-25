const refreshIntervalMs = 30000;

const {
    setText,
    applyStatus,
    setProgressBar,
} = window.Homeland;

async function refreshLinuxDevice() {
    try {
        const config = window.HomelandLinuxDevice || {};

        if (!config.apiUrl) {
            throw new Error(
                "Linux device API URL is missing."
            );
        }

        const response = await fetch(config.apiUrl, {
            headers: {
                "Accept": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(
                `${response.status} ${response.statusText}`
            );
        }

        const data = await response.json();
        const summary = data.summary || {};
        const cpu = data.cpu || {};
        const memory = data.memory || {};
        const storage = data.storage || {};
        const docker = data.docker || {};

        setText("device-status-text", summary.status);
        applyStatus(
            document.getElementById("device-status-dot"),
            summary.status
        );

        setText("summary-cpu", summary.cpu);
        setText("summary-memory", summary.memory);
        setText("summary-containers", summary.containers);
        setText("summary-uptime", summary.uptime);

        setText("cpu-percent", cpu.display);
        setText(
            "memory-percent",
            memory.used_percent != null
                ? `${memory.used_percent}%`
                : "Unknown"
        );
        setText("memory-display", memory.display);
        setText("uptime-display", data.uptime);

        setText("load-1m", cpu.load_1m);
        setText("load-5m", cpu.load_5m);
        setText("load-15m", cpu.load_15m);

        setText(
            "memory-bar-label",
            memory.used_percent != null
                ? `${memory.used_percent}%`
                : "Unknown"
        );

        setProgressBar(
            "memory-bar",
            memory.used_percent
        );

        renderFilesystems(storage.filesystems || []);

        setText(
            "docker-containers",
            docker.containers_detected != null
                ? docker.containers_detected
                : "Unknown"
        );

        setText(
            "last-updated",
            new Date().toLocaleTimeString()
        );
    } catch (error) {
        console.error("Unable to load Linux device data:", error);

        setText("device-status-text", "Offline");

        applyStatus(
            document.getElementById("device-status-dot"),
            "Offline"
        );
    }
}

function storageStatus(percent) {
    if (!Number.isFinite(percent)) {
        return {
            label: "Unknown",
            className: "warning",
        };
    }

    if (percent >= 90) {
        return {
            label: "Critical",
            className: "offline",
        };
    }

    if (percent >= 80) {
        return {
            label: "Warning",
            className: "warning",
        };
    }

    return {
        label: "Healthy",
        className: "healthy",
    };
}

function createFilesystemCard(filesystem) {
    const card = document.createElement("article");
    card.className = "filesystem-card";

    const percent = Number(filesystem.used_percent);
    const status = storageStatus(percent);

    const percentText = Number.isFinite(percent)
        ? `${percent}%`
        : "Unknown";

    card.innerHTML = `
        <div class="filesystem-card-header">
            <div>
                <h3>${filesystem.name || "Filesystem"}</h3>
                <div class="filesystem-mountpoint">
                    ${filesystem.mountpoint || "Unknown"}
                </div>
            </div>

            <div class="filesystem-percent">
                ${percentText}
            </div>
        </div>

        <div class="progress-track">
            <div
                class="progress-bar"
                style="width: ${
                    Number.isFinite(percent)
                        ? Math.max(0, Math.min(100, percent))
                        : 0
                }%"
            ></div>
        </div>

        <div class="filesystem-values">
            <div>
                <span>Used</span>
                <strong>${filesystem.used || "Unknown"}</strong>
            </div>

            <div>
                <span>Available</span>
                <strong>${filesystem.available || "Unknown"}</strong>
            </div>

            <div>
                <span>Total</span>
                <strong>${filesystem.total || "Unknown"}</strong>
            </div>
        </div>

        <div style="margin-top: 14px;">
            <span class="status-pill ${status.className}">
                ${status.label}
            </span>
        </div>
    `;

    return card;
}

function renderFilesystems(filesystems) {
    const grid = document.getElementById("filesystem-grid");
    const summary = document.getElementById("storage-summary");

    if (!grid || !summary) {
        return;
    }

    grid.innerHTML = "";

    if (!Array.isArray(filesystems) || filesystems.length === 0) {
        grid.innerHTML = `
            <p class="loading-message">
                No filesystem metrics were found.
            </p>
        `;

        summary.textContent = "Unknown";
        applyStatus(summary, "Unknown");
        return;
    }

    let worstPercent = null;

    for (const filesystem of filesystems) {
        grid.appendChild(createFilesystemCard(filesystem));

        const percent = Number(filesystem.used_percent);

        if (
            Number.isFinite(percent) &&
            (worstPercent === null || percent > worstPercent)
        ) {
            worstPercent = percent;
        }
    }

    const overallStatus = storageStatus(worstPercent);

    summary.textContent = overallStatus.label;
    summary.className = `status-pill ${overallStatus.className}`;
}	

refreshLinuxDevice();
setInterval(refreshLinuxDevice, refreshIntervalMs);
