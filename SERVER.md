# Homeland Server

## Host Information

Hostname: nuc-ubuntu
Role: Primary Homelab Server
OS: Ubuntu 24.04 LTS
Timezone: America/New_York

---

## Hardware

Platform: Intel NUC
Primary Purpose:
- Docker Host
- Media Server
- Photo Backup
- Comic/Book Library
- Remote Access
- Development Services

---

## Storage

### Mounted Drives

/media/tusa/Data
Purpose:
- Docker persistent data
- Photos
- Comics
- ROMs
- Downloads

/media/tusa/Media
Purpose:
- Books
- Movies
- Television
- Cartoons
- Games
- Audio Books

/media/tusa/Storage
Purpose:
- General storage
- Future backups
- Archive

---

## Networking

Remote Access:
- Tailscale

File Sharing:
- Samba

Docker Installed:
Yes

Git Installed:
Yes

SSH Enabled:
Yes

---

## Migration Plan

Current Server:
Intel NUC

Future Primary:
Dell OptiPlex 5050 Micro

Migration Strategy:
- Build OptiPlex first
- Copy Docker persistent data
- Verify services
- Cut over once validated
- Repurpose NUC as backup/test server

---

## Recovery Notes

System recovered from an interrupted Ubuntu release upgrade.

Major repairs completed:
- Repaired Python installation
- Restored apt package manager
- Completed Ubuntu upgrade
- Repaired GNOME desktop
- Normalized storage mounts
- Restored Docker services

Current Status:
Stable
