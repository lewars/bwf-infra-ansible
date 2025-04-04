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
        "dnf-utils", "htop", "unzip", "zip", "rsync",
        "net-tools", "bind-utils", "traceroute", "plocate", "tmux"
    ]

    for package in required_packages:
        assert host.package(package).is_installed, f"Package {package} not installed"

def test_keyd_installation(host):
    """Verify keyd package is installed if enabled"""
    keyd_package = host.package("keyd")
    if keyd_package.is_installed:
        keyd_service = host.service("keyd")
        assert keyd_service.is_enabled, "keyd service not enabled"

def test_hostname_configuration(host):
    """Test hostname is set correctly"""
    hostname = host.check_output("hostname")
    assert "molecule-test.local" in hostname

    hosts_file = host.file("/etc/hosts")
    assert hosts_file.contains("127.0.1.1\\s+molecule-test.local\\s+molecule-test")

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
        "net.ipv4.conf.default.log_martians": "1"
    }

    for setting, value in settings.items():
        cmd = host.run(f"sysctl {setting}")
        assert cmd.rc == 0
        assert f"{setting} = {value}" in cmd.stdout

def test_system_limits(host):
    """Check system limits configuration"""
    limits_conf = host.file("/etc/security/limits.conf")
    assert limits_conf.exists
    assert limits_conf.contains("# Managed by Ansible")

    assert limits_conf.contains("* soft core 0")
    assert limits_conf.contains("* soft nofile 65535")

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
    user = host.user("molecule")
    assert user.exists
    assert user.shell == "/bin/bash"
    assert "wheel" in user.groups

def test_sudo_access(host):
    """Check sudo configuration for default user"""
    sudo_file = host.file("/etc/sudoers.d/custom")
    assert sudo_file.exists
    assert sudo_file.mode == 0o440
    assert sudo_file.contains("molecule ALL=(ALL) NOPASSWD: ALL")

def test_systemd_resolved(host):
    """Check systemd-resolved configuration"""
    assert host.package("systemd-resolved").is_installed

    resolved_conf = host.file("/etc/systemd/resolved.conf.d/custom.conf")
    assert resolved_conf.exists
    assert resolved_conf.contains("DNSSEC=allow-downgrade")
    assert resolved_conf.contains("DNSOverTLS=opportunistic")

    resolved_service = host.service("systemd-resolved")
    assert resolved_service.is_running
    assert resolved_service.is_enabled
