# Homelab

A personal self-hosted infrastructure platform for media, development, automation, backups, and experimentation.

---

# Goals

This homelab is designed around a few core principles:

* Own my data.
* Minimize dependence on cloud services.
* Make every service reproducible.
* Keep configuration under version control.
* Be able to rebuild the server from scratch in a few hours.
* Learn Linux, Docker, networking, and self-hosting through practical projects.

---

# Hardware

## Server

* Intel NUC running Ubuntu
* Docker
* Portainer
* Tailscale
* Samba

## Storage

### `/media/tusa/Data`

Application data.

Contains:

* Docker
* Photos
* Downloads
* ROMs
* Backups
* Application configuration

### `/media/tusa/Media`

Media library.

Contains:

* Movies
* TV
* Music
* Comics
* Books
* Audiobooks
* Cartoons
* Games

### `/media/tusa/Storage`

Long-term storage.

Contains:

* Projects
* Archives
* 3D assets
* Long-term backups
* OneDrive sync
* Large datasets

---

# Current Services

| Service   | Purpose                     | Status    |
| --------- | --------------------------- | --------- |
| Portainer | Docker management           | ✅ Running |
| Immich    | Photo backup and management | ✅ Running |
| Kavita    | Comics and book library     | ✅ Running |
| Samba     | File sharing                | ✅ Running |
| Tailscale | Secure remote access        | ✅ Running |

---

# Planned Services

## Media

* Jellyfin
* Sonarr
* Radarr
* Prowlarr
* Transmission integration

## Productivity

* Vaultwarden
* Homepage Dashboard
* Karakeep

## Future

* Reverse Proxy
* HTTPS
* Monitoring
* Automated backups
* AI services
* Paperless-ngx (document management)
* Additional automation tools

---

# Development Environment

This homelab also serves as the central development environment for personal projects.

Current development includes:

* Arena Aeternum
* Python utilities
* Comic downloader automation
* Docker infrastructure
* AI experimentation
* Linux scripting

All infrastructure configuration, helper scripts, and documentation are maintained in this repository whenever practical.

---

# Repository Structure

```
Homelab/
├── README.md
├── SERVER.md
├── STORAGE.md
├── SERVICES.md
├── PORTS.md
├── RECOVERY.md
├── TODO.md
├── configs/
├── docker/
└── scripts/
```

---

# Disaster Recovery Philosophy

The server should be replaceable.

If the NUC fails, recovery should be:

1. Install Ubuntu.
2. Clone this repository.
3. Mount the storage drives.
4. Restore secrets and environment files.
5. Start Docker containers.
6. Resume normal operation.

Application data lives on the storage drives. Infrastructure knowledge lives in this repository.

---

# Guiding Principles

* Keep services containerized whenever possible.
* Avoid manual configuration drift.
* Document significant changes.
* Commit infrastructure changes to Git.
* Use stable mount points.
* Prefer automation over repetitive manual work.
* Build for long-term maintainability rather than short-term convenience.

---

# Roadmap

Current priorities:

* Complete Homepage dashboard
* Deploy Jellyfin
* Deploy the Arr stack
* Deploy Vaultwarden
* Improve Kavita metadata
* Import Karakeep bookmarks
* Automate backups
* Continue documenting the homelab

This repository is intended to become the single source of truth for the entire homelab infrastructure.
