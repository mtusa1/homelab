# Homelab Services

## Homepage

Purpose:
Homelab dashboard

Port:
3000

Compose:
~/docker/homepage

Status:
Running

---

## Portainer

Purpose:
Docker Management

Port:
9443

Compose:
~/docker/portainer

Status:
Running

---

## Immich

Purpose:
Photo Backup

Port:
2283

Compose:
~/docker/immich

Persistent Data:
/media/tusa/Data/Photos

Database:
/media/tusa/Data/Docker

Status:
Running

---

## Kavita

Purpose:
Books and Comics

Port:
5000

Compose:
~/docker/kavita

Configuration:
/media/tusa/Data/Docker/Kavita/config

Books:
/media/tusa/Media/The Trove

Comics:
/media/tusa/Media/Comics

Status:
Running

Notes:
Configuration must always mount:

/media/tusa/Data/Docker/Kavita/config

Do NOT use:

~/docker/kavita/config

or a new empty database will be created.

---

## Jellyfin

Purpose:
Media Server

Port:
8096

Compose:
~/docker/jellyfin

Libraries:

Movies:
/media/tusa/Media/Movies

Television:
/media/tusa/Data/Video/Television

Status:
Running

---

## Samba

Purpose:
File Sharing

Shares:

Data
/media/tusa/Data

Media
/media/tusa/Media

Storage
/media/tusa/Storage

Status:
Running

---

## Tailscale

Purpose:
Remote VPN

Status:
Running

Used For:
- SSH
- SMB
- Remote Docker Management
- Tablet Access
- Laptop Access

---

## Git

Repository:

https://github.com/mtusa1/homelab

Purpose:
Infrastructure documentation
Compose files
Scripts
Configuration backup

Status:
Configured
