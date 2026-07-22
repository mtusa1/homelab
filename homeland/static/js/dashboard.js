const refreshIntervalMs = 30000;

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value ?? "Unknown";
    }
}

function setStatus(elementId, status) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    const normalized = String(status || "Unknown").toLowerCase();

    element.className = "status-pill";

    if (normalized === "online" || normalized === "healthy") {
        element.classList.add("healthy");
    } else if (normalized === "offline") {
        element.classList.add("offline");
    } else {
        element.classList.add("warning");
    }

    element.textContent = status || "Unknown";
}

async function fetchJson(url) {
    const response = await fetch(url, {
        headers: {
            "Accept": "application/json",
        },
    });

    if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
    }

    return response.json();
}

async function loadSynology() {
    try {
        const data = await fetchJson("/api/device/synology");
        const summary = data.summary || {};
        const storage = data.storage || {};
        const disks = data.disks || [];

        setStatus("synology-status", summary.status);
        setText(
            "synology-storage-percent",
            storage.used_percent != null
                ? `${storage.used_percent}%`
                : "Unknown"
        );
        setText("synology-storage-used", `${storage.used} used`);
        setText("synology-storage-free", `${storage.free} free`);
        setText("synology-temperature", summary.temperature);
        setText(
            "synology-disk-temperature",
            summary.disk_temperature
        );
        setText("synology-raid", summary.raid);
        setText("synology-uptime", summary.uptime);
        setText(
            "synology-drive-count",
            `${disks.length} drives detected`
        );

        const bar = document.getElementById("synology-storage-bar");

        if (bar && storage.used_percent != null) {
            bar.style.width = `${storage.used_percent}%`;
        }
    } catch (error) {
        console.error("Unable to load Synology data:", error);
        setStatus("synology-status", "Offline");
    }
}

async function loadNuc() {
    try {
        const data = await fetchJson("/nuc");

        setStatus("nuc-status", data.status);
        setText("nuc-cpu", data.cpu);
        setText("nuc-memory", data.memory);
        setText("nuc-containers", data.containers);
        setText("nuc-uptime", data.uptime);
    } catch (error) {
        console.error("Unable to load NUC data:", error);
        setStatus("nuc-status", "Offline");
    }
}

async function refreshDashboard() {
    await Promise.allSettled([
        loadSynology(),
        loadNuc(),
    ]);

    setText(
        "last-updated",
        new Date().toLocaleTimeString()
    );
}

refreshDashboard();
setInterval(refreshDashboard, refreshIntervalMs);

async function loadWindowsCard(device,prefix){

    try{

        const response=await fetch(
            `/api/device/windows/${device}`,
            {cache:"no-store"}
        );

        if(!response.ok)
            throw new Error(response.status);

        const data=await response.json();

        setStatus(
            `${prefix}-status`,
            data.status
        );

        setText(
            `${prefix}-cpu`,
            data.cpu.display
        );

        setText(
            `${prefix}-memory`,
            data.memory.display
        );

        setText(
            `${prefix}-storage`,
            data.drives.length + " drives"
        );

        setText(
            `${prefix}-uptime`,
            data.uptime.display
        );

        setText(
            `${prefix}-drivecount`,
            data.drives
                .map(d=>d.letter)
                .join(", ")
        );

    }
    catch(err){

        console.error(err);

        setStatus(
            `${prefix}-status`,
            "Offline"
        );

    }

}

loadWindowsCard(
    "main-desktop",
    "windows-main"
);

loadWindowsCard(
    "windows-workstation",
    "windows-workstation"
);


/* HOMELAND WINDOWS DASHBOARD CARDS */

async function loadWindowsDashboardCard(deviceId, prefix) {
    try {
        const response = await fetch(
            `/api/device/windows/${deviceId}`,
            { cache: "no-store" }
        );

        if (!response.ok) {
            throw new Error(
                `Windows API returned HTTP ${response.status}`
            );
        }

        const data = await response.json();

        setStatus(`${prefix}-status`, data.status);
        setText(`${prefix}-cpu`, data.cpu.display);
        setText(`${prefix}-memory`, data.memory.display);
        setText(`${prefix}-uptime`, data.uptime.display);

        const drives = Array.isArray(data.drives)
            ? data.drives
            : [];

        setText(
            `${prefix}-storage`,
            `${drives.length} ${drives.length === 1 ? "drive" : "drives"}`
        );

        const driveSummary = drives.length
            ? drives.map((drive) => drive.letter).join(", ")
            : "No drives reported";

        setText(`${prefix}-drivecount`, driveSummary);

        if (
            window.HomelandComponents &&
            window.HomelandComponents.progressMetric
        ) {
            window.HomelandComponents.progressMetric(
                `${prefix}-cpu-metric`,
                "CPU usage",
                data.cpu.display,
                data.cpu.percent
            );

            window.HomelandComponents.progressMetric(
                `${prefix}-memory-metric`,
                "Memory",
                data.memory.display,
                data.memory.percent
            );
        }
    } catch (error) {
        console.error(
            `Unable to load Windows dashboard card ${deviceId}:`,
            error
        );

        setStatus(`${prefix}-status`, "Offline");
        setText(`${prefix}-cpu`, "Unavailable");
        setText(`${prefix}-memory`, "Unavailable");
        setText(`${prefix}-storage`, "Unavailable");
        setText(`${prefix}-uptime`, "Unavailable");
        setText(`${prefix}-drivecount`, "Exporter unavailable");
    }
}

async function loadWindowsDashboardCards() {
    await Promise.allSettled([
        loadWindowsDashboardCard(
            "main-desktop",
            "windows-main"
        ),
        loadWindowsDashboardCard(
            "windows-workstation",
            "windows-workstation"
        ),
    ]);
}

loadWindowsDashboardCards();

async function loadDockerHomepageCard() {
    const runningElement =
        document.getElementById("home-docker-running");
    const servicesElement =
        document.getElementById("home-docker-services");
    const attentionElement =
        document.getElementById("home-docker-attention");
    const statusElement =
        document.getElementById("home-docker-status");

    if (
        !runningElement ||
        !servicesElement ||
        !attentionElement ||
        !statusElement
    ) {
        return;
    }

    try {
        const response = await fetch("/api/docker");

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const services = await response.json();

        const running = services.filter(
            service => service.status === "running"
        ).length;

        const registered = services.filter(
            service => service.registered
        ).length;

        const unregistered = services.filter(
            service => !service.registered
        ).length;

        const stopped = services.length - running;
        const attention = stopped + unregistered;

        runningElement.textContent = running;
        servicesElement.textContent = registered;
        attentionElement.textContent = attention;

        if (stopped === 0) {
            statusElement.textContent = "Healthy";
            statusElement.classList.add("is-online");
        } else {
            statusElement.textContent = "Attention";
            statusElement.classList.add("is-warning");
        }
    } catch (error) {
        statusElement.textContent = "Unavailable";
        statusElement.classList.add("is-warning");
    }
}

async function loadOverview() {
    try {
        const data = await fetchJson("/api/overview");

        const devices = data.devices || {};
        const docker = data.docker || {};
        const storage = data.storage || {};
        const cpu = data.cpu || {};
        const alerts = data.alerts || [];

        setText(
            "overview-devices",
            `${devices.online ?? 0} / ${devices.total ?? 0} online`
        );

        setText(
            "overview-devices-caption",
            devices.total === 1
                ? "Ubuntu NUC monitored"
                : `${devices.total ?? 0} monitored systems`
        );

        setText(
            "overview-docker",
            `${docker.running ?? 0} / ${docker.total ?? 0} running`
        );

        setText(
            "overview-docker-caption",
            `${docker.registered ?? 0} registered services`
        );

        setText(
            "overview-storage",
            storage.used_percent != null
                ? `${storage.used_percent}% used`
                : "Unknown"
        );

        setText(
            "overview-storage-caption",
            "Across monitored NUC filesystems"
        );

        setText(
            "overview-cpu",
            cpu.average_percent != null
                ? `${cpu.average_percent}%`
                : "Unknown"
        );

        setText(
            "overview-cpu-caption",
            "Current Ubuntu NUC CPU usage"
        );

        const cpuBar =
            document.getElementById("overview-cpu-bar");

        if (cpuBar && cpu.average_percent != null) {
            cpuBar.style.width =
                `${Math.min(cpu.average_percent, 100)}%`;
        }

        const healthElement =
            document.getElementById("overview-health");

        const healthTextElement =
            document.getElementById("overview-health-text");

        const health = String(
            data.health || "unknown"
        ).toLowerCase();

        if (healthElement) {
            healthElement.className =
                `overview-health ${health}`;
        }

        if (healthTextElement) {
            if (health === "healthy") {
                healthTextElement.textContent =
                    "All systems operational";
            } else if (health === "warning") {
                healthTextElement.textContent =
                    "Attention recommended";
            } else if (health === "critical") {
                healthTextElement.textContent =
                    "Immediate attention required";
            } else {
                healthTextElement.textContent =
                    "Status unknown";
            }
        }

        setText(
            "overview-alert-count",
            alerts.length === 1
                ? "1 active alert"
                : `${alerts.length} active alerts`
        );

        setText(
            "overview-refresh-status",
            "Live metrics updated"
        );

        const alertList =
            document.getElementById("overview-alert-list");

        if (alertList) {
            alertList.innerHTML = "";

            if (alerts.length === 0) {
                const alert = document.createElement("div");
                alert.className =
                    "overview-alert healthy";
                alert.textContent =
                    "No active alerts";
                alertList.appendChild(alert);
            } else {
                alerts.forEach((item) => {
                    const alert =
                        document.createElement("div");

                    alert.className =
                        `overview-alert ${item.level || "neutral"}`;

                    alert.textContent =
                        item.message || "Unknown alert";

                    alertList.appendChild(alert);
                });
            }
        }

        setText(
            "last-updated",
            new Date().toLocaleTimeString([], {
                hour: "numeric",
                minute: "2-digit",
                second: "2-digit",
            })
        );
    } catch (error) {
        console.error(
            "Failed to load overview:",
            error
        );

        setText(
            "overview-health-text",
            "Overview unavailable"
        );

        setText(
            "overview-refresh-status",
            "Unable to load live metrics"
        );
    }
}

loadOverview()
loadDockerHomepageCard();

setInterval(
    () => {
        loadOverview();
        loadSynology();
        loadNuc();
        loadWindowsDashboardCards();
        loadDockerHomepageCard();
    },
    refreshIntervalMs
);
