"use strict";

const dockerState = {
    services: [],
    query: "",
};

const dockerElements = {
    applications: document.getElementById("docker-applications"),
    total: document.getElementById("docker-total"),
    running: document.getElementById("docker-running"),
    attention: document.getElementById("docker-attention"),

    engineStatus: document.getElementById("docker-engine-status"),
    refreshButton: document.getElementById("docker-refresh"),
    searchInput: document.getElementById("docker-search"),

    message: document.getElementById("docker-message"),
    serviceSections: document.getElementById("docker-service-sections"),

    technicalToggle: document.getElementById("docker-technical-toggle"),
    technicalPanel: document.getElementById("docker-technical-panel"),
    technicalGrid: document.getElementById("docker-technical-grid"),
    technicalCount: document.getElementById("docker-technical-count"),
};


function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function normalizedStatus(service) {
    return String(service.status || "unknown").toLowerCase();
}


function isRunning(service) {
    return normalizedStatus(service) === "running";
}


function statusText(service) {
    const status = normalizedStatus(service);

    if (status === "running") {
        return "Online";
    }

    if (status === "exited") {
        return "Stopped";
    }

    return status.charAt(0).toUpperCase() + status.slice(1);
}


function matchesSearch(service) {
    if (!dockerState.query) {
        return true;
    }

    const searchable = [
        service.title,
        service.description,
        service.category,
        service.container,
        service.image,
    ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

    return searchable.includes(dockerState.query);
}


function createServiceCard(service) {
    const externalUrl =
        service.url && !String(service.url).startsWith("/");

    const openButton = service.url
        ? `
            <a
                class="docker-card-button docker-card-button-primary"
                href="${escapeHtml(service.url)}"
                ${externalUrl ? 'target="_blank" rel="noopener noreferrer"' : ""}
            >
                Open
            </a>
        `
        : "";

    return `
        <article class="docker-service-card">
            <div class="docker-service-card-top">
                <div class="docker-service-icon">
                    ${escapeHtml(service.icon || "📦")}
                </div>

                <span class="docker-status-pill ${
                    isRunning(service) ? "is-online" : "is-offline"
                }">
                    <span class="docker-status-dot"></span>
                    ${escapeHtml(statusText(service))}
                </span>
            </div>

            <div class="docker-service-card-copy">
                <p class="docker-service-category">
                    ${escapeHtml(service.category || "Other")}
                </p>

                <h3>${escapeHtml(service.title || service.container)}</h3>

                <p>
                    ${escapeHtml(
                        service.description || "Docker application"
                    )}
                </p>
            </div>

            <div class="docker-service-meta">
                <span title="${escapeHtml(service.container)}">
                    ${escapeHtml(service.container)}
                </span>

                <span title="${escapeHtml(service.image)}">
                    ${escapeHtml(service.image)}
                </span>
            </div>

            <div class="docker-service-actions">
                ${openButton}

                <button
                    class="docker-card-button"
                    type="button"
                    disabled
                    title="Container controls are coming next"
                >
                    Manage
                </button>
            </div>
        </article>
    `;
}


function createTechnicalCard(service) {
    return `
        <article class="docker-technical-card">
            <div>
                <strong>${escapeHtml(service.container)}</strong>
                <span title="${escapeHtml(service.image)}">
                    ${escapeHtml(service.image)}
                </span>
            </div>

            <span class="docker-status-pill ${
                isRunning(service) ? "is-online" : "is-offline"
            }">
                <span class="docker-status-dot"></span>
                ${escapeHtml(statusText(service))}
            </span>
        </article>
    `;
}


function renderSummary() {
    const registered = dockerState.services.filter(
        service => service.registered
    );

    const running = dockerState.services.filter(isRunning);

    const stopped = dockerState.services.filter(
        service => !isRunning(service)
    );

    const unregistered = dockerState.services.filter(
        service => !service.registered
    );

    dockerElements.applications.textContent = registered.length;
    dockerElements.total.textContent = dockerState.services.length;
    dockerElements.running.textContent = running.length;

    /*
     * Attention includes stopped containers and services that have not yet
     * been entered in Homeland's registry.
     */
    dockerElements.attention.textContent =
        stopped.length + unregistered.length;

    if (stopped.length === 0) {
        dockerElements.engineStatus.textContent = "Engine healthy";
        dockerElements.engineStatus.classList.add("is-healthy");
        dockerElements.engineStatus.classList.remove("is-warning");
    } else {
        dockerElements.engineStatus.textContent =
            `${stopped.length} container${stopped.length === 1 ? "" : "s"} offline`;

        dockerElements.engineStatus.classList.remove("is-healthy");
        dockerElements.engineStatus.classList.add("is-warning");
    }
}


function renderRegisteredServices() {
    const registered = dockerState.services
        .filter(service => service.registered)
        .filter(matchesSearch);

    if (!registered.length) {
        dockerElements.serviceSections.innerHTML = `
            <div class="docker-empty-state">
                No registered services match your search.
            </div>
        `;
        return;
    }

    const groups = new Map();

    for (const service of registered) {
        const category = service.category || "Other";

        if (!groups.has(category)) {
            groups.set(category, []);
        }

        groups.get(category).push(service);
    }

    dockerElements.serviceSections.innerHTML = Array.from(groups.entries())
        .map(([category, services]) => {
            const sortedServices = [...services].sort((a, b) =>
                String(a.title).localeCompare(String(b.title))
            );

            return `
                <section class="docker-category-section">
                    <div class="docker-category-heading">
                        <h2>${escapeHtml(category)}</h2>
                        <span>${sortedServices.length}</span>
                    </div>

                    <div class="docker-service-grid">
                        ${sortedServices.map(createServiceCard).join("")}
                    </div>
                </section>
            `;
        })
        .join("");
}


function renderTechnicalContainers() {
    const technical = dockerState.services
        .filter(service => !service.registered)
        .filter(matchesSearch)
        .sort((a, b) =>
            String(a.container).localeCompare(String(b.container))
        );

    dockerElements.technicalCount.textContent = technical.length;

    dockerElements.technicalGrid.innerHTML = technical.length
        ? technical.map(createTechnicalCard).join("")
        : `
            <div class="docker-empty-state">
                No technical containers match your search.
            </div>
        `;
}


function renderDockerPage() {
    renderSummary();
    renderRegisteredServices();
    renderTechnicalContainers();
}


function showError(message) {
    dockerElements.message.textContent = message;
    dockerElements.message.hidden = false;

    dockerElements.serviceSections.innerHTML = `
        <div class="docker-empty-state">
            Docker service data could not be loaded.
        </div>
    `;

    dockerElements.engineStatus.textContent = "Engine unavailable";
    dockerElements.engineStatus.classList.remove("is-healthy");
    dockerElements.engineStatus.classList.add("is-warning");
}


async function loadDockerServices() {
    dockerElements.refreshButton.disabled = true;
    dockerElements.refreshButton.textContent = "Refreshing…";
    dockerElements.message.hidden = true;

    try {
        const response = await fetch("/api/docker", {
            method: "GET",
            headers: {
                Accept: "application/json",
            },
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (!Array.isArray(data)) {
            throw new Error("Unexpected API response");
        }

        dockerState.services = data;
        renderDockerPage();
    } catch (error) {
        console.error("Docker page error:", error);

        showError(
            `Unable to load Docker services: ${error.message}`
        );
    } finally {
        dockerElements.refreshButton.disabled = false;
        dockerElements.refreshButton.textContent = "Refresh";
    }
}


dockerElements.refreshButton?.addEventListener(
    "click",
    loadDockerServices
);


dockerElements.searchInput?.addEventListener("input", event => {
    dockerState.query = event.target.value.trim().toLowerCase();

    renderRegisteredServices();
    renderTechnicalContainers();
});


dockerElements.technicalToggle?.addEventListener("click", () => {
    const isExpanded =
        dockerElements.technicalToggle.getAttribute("aria-expanded") ===
        "true";

    dockerElements.technicalToggle.setAttribute(
        "aria-expanded",
        String(!isExpanded)
    );

    dockerElements.technicalPanel.hidden = isExpanded;
});


loadDockerServices();
