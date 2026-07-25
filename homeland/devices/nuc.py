from __future__ import annotations

from devices.linux import LinuxFilesystem, get_linux_data


NUC_FILESYSTEMS = (
    LinuxFilesystem(
        name="Ubuntu Root",
        mountpoint="/",
    ),
    LinuxFilesystem(
        name="Media",
        mountpoint="/media/tusa/Media",
    ),
    LinuxFilesystem(
        name="Storage",
        mountpoint="/media/tusa/Storage",
    ),
    LinuxFilesystem(
        name="Data",
        mountpoint="/media/tusa/Data",
    ),
)


def get_nuc_data() -> dict:
    """
    Compatibility wrapper for existing NUC routes and overview code.

    New Linux hosts should call devices.linux.get_linux_data directly.
    """
    return get_linux_data(
        job="nuc",
        filesystems=NUC_FILESYSTEMS,
        container_job="docker",
    )
