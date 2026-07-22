window.Homeland = window.Homeland || {};

window.Homeland.setText = function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value ?? "Unknown";
    }
};

window.Homeland.applyStatus = function applyStatus(
    element,
    status
) {
    if (!element) {
        return;
    }

    const normalized = String(
        status || "Unknown"
    ).toLowerCase();

    element.classList.remove(
        "loading",
        "healthy",
        "warning",
        "offline"
    );

    if (
        normalized === "online" ||
        normalized === "healthy"
    ) {
        element.classList.add("healthy");
    } else if (
        normalized === "offline" ||
        normalized === "critical"
    ) {
        element.classList.add("offline");
    } else {
        element.classList.add("warning");
    }
};

window.Homeland.setProgressBar = function setProgressBar(
    id,
    percent
) {
    const bar = document.getElementById(id);

    if (!bar) {
        return;
    }

    const numericPercent = Number(percent);

    const safePercent = Number.isFinite(numericPercent)
        ? Math.max(0, Math.min(100, numericPercent))
        : 0;

    bar.style.width = `${safePercent}%`;
};

window.Homeland.formatPercent = function formatPercent(
    value,
    decimals = 1
) {
    const numericValue = Number(value);

    if (!Number.isFinite(numericValue)) {
        return "Unknown";
    }

    return `${numericValue.toFixed(decimals)}%`;
};

window.Homeland.escapeHtml = function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = String(value ?? "");
    return element.innerHTML;
};
