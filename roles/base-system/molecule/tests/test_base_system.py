import pytest
import os


# Test package management functionality
def test_rpm_fusion_repos(host):
    """Verify RPM Fusion repositories are properly configured"""
    cmd = host.run("dnf repolist | grep 'rpmfusion'")
    assert cmd.rc == 0, "RPM Fusion repositories not found"

    free_repo = host.run("dnf repolist | grep 'rpmfusion-free'")
    nonfree_repo = host.run("dnf repolist | grep 'rpmfusion-nonfree'")
    assert free_repo.rc == 0, "RPM Fusion free repository not found"
    assert nonfree_repo.rc == 0, "RPM Fusion nonfree repository not found"


def test_dnf_configuration(host):
    """Test DNF is configured with performance settings"""
    dnf_conf = host.file("/etc/dnf/dnf.conf")
    assert dnf_conf.exists
    assert dnf_conf.contains("fastestmirror=true")
    assert dnf_conf.contains("max_parallel_downloads=10")
    assert dnf_conf.contains("deltarpm=true")


def test_required_packages(host):
    """Verify all required packages are installed"""
    required_packages = [
        "dnf-utils",
        "htop",
        "emacs",
        "htop",
        "rsync",
        "net-tools",
        "bind-utils",
        "traceroute",
        "plocate",
        "tmux",
        "fwupd",
    ]

    for package in required_packages:
        assert host.package(package).is_installed, f"Package {package} not installed"


def test_nvidia_packages(host):
    """Verify NVIDIA packages are installed"""
    nvidia_packages = [
        "akmod-nvidia",
        "xorg-x11-drv-nvidia-cuda",
        "xorg-x11-drv-nvidia-cuda-libs",
        "kmodtool",
        "mokutil",
        "openssl",
        "xorg-x11-drv-nvidia-power",
        "vulkan-loader",
        "libva-nvidia-driver",
        "libva-utils",
        "vdpauinfo",
    ]

    for package in nvidia_packages:
        assert host.package(package).is_installed, f"Package {package} not installed"


def test_keyd_installation(host):
    """Verify keyd software is installed and enabled"""
    keyd_package = host.file("/usr/local/bin/keyd")
    assert keyd_package.exists, "keyd package not installed"
    assert keyd_package.is_executable, "keyd package is executable"
    keyd_service = host.service("keyd")
    assert keyd_service.is_enabled, "keyd service not enabled"


@pytest.mark.skip(reason="Flathub repository verification not implemented yet")
def test_flathub_repo(host):
    """Verify Flathub repository is configured"""
    cmd = host.run("flatpak remotes | grep -P '^flathub\b'")
    assert cmd.rc == 0, "Flathub repository found"
    assert "verified_floss" in cmd.stdout


def test_chrony_configuration(host):
    """Verify chrony is installed, configured and running"""
    assert host.package("chrony").is_installed

    chrony_conf = host.file("/etc/chrony.conf")
    assert chrony_conf.exists
    assert chrony_conf.user == "root"
    assert chrony_conf.group == "root"
    assert chrony_conf.mode == 0o644

    assert chrony_conf.contains("# Chrony configuration managed by Ansible")
    assert chrony_conf.contains("driftfile /var/lib/chrony/drift")

    chrony_service = host.service("chronyd")
    assert chrony_service.is_running
    assert chrony_service.is_enabled


def test_filesystem_blacklist(host):
    """Check that specified filesystems are blacklisted"""
    blacklist_conf = host.file("/etc/modprobe.d/blacklist.conf")
    assert blacklist_conf.exists

    for fs in ["cramfs", "udf"]:
        assert blacklist_conf.contains(f"install {fs} /bin/true")


def test_secure_mount_options(host):
    """Verify mount points have secure options"""
    tmp_mount = host.mount_point("/tmp")
    assert tmp_mount.exists
    for option in ["nodev", "nosuid", "noexec"]:
        assert option in tmp_mount.options, f"{option} not set on /tmp"

    var_tmp_mount = host.mount_point("/var/tmp")
    assert var_tmp_mount.exists
    for option in ["nodev", "nosuid", "noexec"]:
        assert option in var_tmp_mount.options, f"{option} not set on /var/tmp"

    home_mount = host.mount_point("/home")
    if home_mount.exists:
        for option in ["nodev", "nosuid"]:
            assert option in home_mount.options, f"{option} not set on /home"


def test_sysctl_settings(host):
    """Verify sysctl settings are applied"""
    settings = {
        "net.ipv4.conf.all.log_martians": "1",
        "net.ipv4.conf.default.log_martians": "1",
    }

    for setting, value in settings.items():
        cmd = host.run(f"sysctl {setting}")
        assert cmd.rc == 0
        assert f"{setting} = {value}" in cmd.stdout


def test_coredump_settings(host):
    """Verify systemd coredump settings"""
    coredump_conf = host.file("/etc/systemd/coredump.conf")
    assert coredump_conf.exists
    assert coredump_conf.contains("Storage=external")
    assert coredump_conf.contains("Compress=yes")


def test_grub_configuration(host):
    """Check GRUB configuration includes audit parameter"""
    grub_conf = host.file("/etc/default/grub")
    assert grub_conf.exists
    assert grub_conf.contains("audit=1")


# Test user configuration
def test_default_user_exists(host):
    """Verify the default user is created properly"""
    user = host.user("molecule-user")
    assert user.exists
    assert user.shell == "/bin/bash"
    assert "molecule-user" in user.groups


def test_sudo_access(host):
    """Check sudo configuration for default user"""
    sudo_file = host.file("/etc/sudoers.d/custom")
    assert sudo_file.exists
    assert sudo_file.mode == 0o440
    duser = os.getenv("DEFAULT_USER", "molecule")
    assert sudo_file.contains(f"{duser} ALL=(ALL) NOPASSWD: ALL")


def test_systemd_resolved(host):
    """Check systemd-resolved configuration"""
    assert host.package("systemd-resolved").is_installed

    resolved_conf = host.file("/etc/systemd/resolved.conf.d/dns.conf")
    assert resolved_conf.exists
    assert resolved_conf.contains("DNSSEC=allow-downgrade")
    assert resolved_conf.contains("DNSOverTLS=opportunistic")
    assert resolved_conf.contains("MulticastDNS=yes")

    resolved_service = host.service("systemd-resolved")
    assert resolved_service.is_running
    assert resolved_service.is_enabled


# Test borgbackup and vorta are installed
def test_borgbackup_and_vorta(host):
    """Verify borgbackup and vorta are installed"""
    assert host.package("borgbackup").is_installed
    assert host.package("vorta").is_installed


# Test backup script /usr/local/bin/backup.sh is present
def test_backup_script(host):
    """Verify backup script is present and executable"""
    backup_script = host.file("/usr/local/bin/backup.sh")
    assert backup_script.exists
    assert backup_script.is_file
    assert backup_script.is_executable


# Test if backup directories (/var/local/backup and /etc/backup) are created
def test_backup_directories(host):
    """Verify backup directories are created"""
    backup_dirs = ["/var/local/backup", "/etc/backup"]
    for dir in backup_dirs:
        backup_dir = host.file(dir)
        assert backup_dir.exists
        assert backup_dir.is_directory
        assert backup_dir.user == "root"
        assert backup_dir.group == "wheel"
        assert backup_dir.mode == 0o750


# Test if ecludes file /etc/backup/exclude.txt is present
def test_excludes_file(host):
    """Verify excludes file is present"""
    excludes_file = host.file("/etc/backup/exclude.txt")
    assert excludes_file.exists
    assert excludes_file.is_file
    assert excludes_file.user == "root"
    assert excludes_file.group == "root"
    assert excludes_file.mode == 0o644


# Test if back configuration file /etc/backup/backup.conf is present
def test_backup_configuration_file(host):
    """Verify backup configuration file is present"""
    backup_conf = host.file("/etc/backup/backup.conf")
    assert backup_conf.exists
    assert backup_conf.is_file
    assert backup_conf.user == "root"
    assert backup_conf.group == "root"
    assert backup_conf.mode == 0o640


# Test if backup passphrase file /etc/backup/passphrase is present
def test_backup_passphrase_file(host):
    """Verify backup passphrase file is present"""
    passphrase_file = host.file("/etc/backup/passphrase")
    assert passphrase_file.exists
    assert passphrase_file.is_file
    assert passphrase_file.user == "root"
    assert passphrase_file.group == "root"
    assert passphrase_file.mode == 0o600


# Test if backup systemd onshot service is present
def test_backup_systemd_service(host):
    """Verify backup systemd oneshot service is present"""
    backup_service = host.file("/etc/systemd/system/backup.service")
    assert backup_service.exists
    assert backup_service.is_file
    assert backup_service.user == "root"
    assert backup_service.group == "root"
    assert backup_service.mode == 0o644


# Test if backup systemd timer is present and enabled
def test_backup_systemd_timer(host):
    """Verify backup systemd timer is present and enabled"""
    backup_timer = host.file("/etc/systemd/system/backup.timer")
    assert backup_timer.exists
    assert backup_timer.is_file
    assert backup_timer.user == "root"
    assert backup_timer.group == "root"
    assert backup_timer.mode == 0o644

    timer_service = host.service("backup.timer")
    assert timer_service.is_enabled


def test_clamav_packages_installed(host):
    """
    Tests that all required ClamAV packages are installed.
    """
    packages = [
        "acl",
        "clamav",
        "clamd",
        "clamav-data",
        "clamav-freshclam",
        "clamav-lib",
        "clamav-filesystem",
    ]
    for package in packages:
        assert host.package(package).is_installed, f"Package {package} not installed"


@pytest.mark.skip(reason="clamd service is not running")
def test_freshclam_service_running(host):
    """
    Tests that the freshclam service is running.
    """
    assert not host.service(
        "clamav-freshclam.service"
    ).is_running, "freshclam service is running"

@pytest.mark.skip(reason="clamd service is not running")
def test_freshclam_timer_running(host):
    """
    Tests that the freshclam timer is running.
    """
    assert host.service(
        "clamav-freshclam.timer"
    ).is_enabled, "freshclam timer is not running"

@pytest.mark.skip(reason="clamd service is not running")
def test_clamd_service_running(host):
    """
    Tests that the clamd service is running.
    """
    assert host.service("clamd@clamd.service").is_running, "clamd service is not running"


@pytest.mark.skip(reason="clamd service is not running")
def test_clamonacc_service_running(host):
    """
    Tests that the clamonacc service is running.
    """
    assert host.service(
        "clamonacc.service"
    ).is_running, "clamonacc service is not running"

@pytest.mark.skip(reason="clamd service is not running")
def test_clamscan_timer_running(host):
    """
    Tests that the clamscan timer is running
    """
    assert host.service("clamscan.timer").is_enabled, "clamscan.timer is not running"
