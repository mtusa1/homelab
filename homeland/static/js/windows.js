const {
    setText,
    applyStatus,
} = window.Homeland;

const {
    renderStorageGrid,
    progressMetric,
} = window.HomelandComponents;

const page = document.getElementById("windows-device-page");

const deviceId = page.dataset.deviceId;

const statusDot = document.getElementById("device-status-dot");

async function loadDevice() {

    try {

        const response = await fetch(
            `/api/device/windows/${deviceId}`,
            {
                cache: "no-store"
            }
        );

        if (!response.ok)
            throw new Error(response.status);

        const data = await response.json();

        applyStatus(statusDot, data.status);

        setText("device-status-text", data.status);

        setText("summary-cpu", data.cpu.display);
        setText("summary-memory", data.memory.display);
        setText("summary-uptime", data.uptime.display);

        setText(
            "summary-disk-count",
            `${data.drives.length} drives`
        );

        progressMetric(
            "cpu-display",
            "CPU Usage",
            data.cpu.display,
            data.cpu.percent
        );

        progressMetric(
            "memory-display",
            "Memory Usage",
            data.memory.display,
            data.memory.percent
        );

        setText("uptime-display", data.uptime.display);

        renderStorageGrid(
            "drive-grid",
            data.drives
        );

        setText(
            "last-updated",
            new Date().toLocaleTimeString()
        );

    }
    catch(err){

        console.error(err);

        applyStatus(statusDot, "Offline");

        setText("device-status-text","Offline");
        setText("last-updated","Update Failed");
    }

}

loadDevice();

setInterval(loadDevice,30000);
