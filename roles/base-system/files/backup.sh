#!/bin/bash
# backup.sh - Automated Borg backup script

# Exit on error
set -e

# Load configuration
CONFIG_FILE="/etc/backup/backup.conf"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file $CONFIG_FILE not found"
    exit 1
fi

source "$CONFIG_FILE"

# Set variables if not defined in config
FQDN=$(hostname -f)
BORG_REPO="${BORG_REPO_PREFIX}/${FQDN}"
ARCHIVE_NAME="backup-$(date +%Y-%m-%dT%H:%M:%S)"

# Load passphrase
if [ -f "$BORG_PASSPHRASE_FILE" ]; then
    export BORG_PASSPHRASE=$(cat "$BORG_PASSPHRASE_FILE")
else
    echo "Error: Passphrase file not found"
    exit 1
fi

echo "=== Backup started at $(date) ==="

# Initialize repository if it doesn't exist
if [ ! -d "$BORG_REPO" ]; then
    echo "Initializing Borg repository..."
    /usr/bin/borg init --encryption=repokey "$BORG_REPO"
fi

# Create backup archive
echo "Creating backup archive..."
/usr/bin/borg create \
    $BORG_CREATE_OPTS \
    $BORG_REPO::$ARCHIVE_NAME \
    $BACKUP_PATHS

# Prune old backups
echo "Pruning old backups..."
/usr/bin/borg prune \
    $BORG_PRUNE_OPTS \
    $BORG_REPO

echo "=== Backup completed at $(date) ==="

# Clear the passphrase from environment
unset BORG_PASSPHRASE

# Return explicit success
exit 0
