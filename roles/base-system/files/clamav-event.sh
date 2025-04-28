#!/bin/bash
# clamav-event.sh - Notify graphical users when ClamAV detects a virus/malware

sanitize() {
    # Remove shell metacharacters and limit length
    echo "$1" | tr -d ';$`|&<>"{}()[]!?' | tr -d "'" | cut -c1-200
}

if [ $# -lt 2 ]; then
    logger -p emerg -t clamav-event "Error: Insufficient arguments provided to clamav-event.sh"
    exit 1
fi

VIRUS_NAME=$(sanitize "$1")
FILE_NAME=$(sanitize "$2")
MESSAGE="SECURITY ALERT: Malware detected!\nVirus: ${VIRUS_NAME}\nFile: ${FILE_NAME}"

logger -p emerg -t clamav-event "$MESSAGE"

# Find users with active graphical sessions and notify them
who | grep -v '(:0)' | awk '{print $1}' | sort -u | while read -r USER; do
    USER_ID=$(id -u "$USER")
    if [ -n "$USER_ID" ]; then
        # Get DBUS address for this user
        DBUS_ADDRESS=$(DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$USER_ID/bus)

        # Send notification to the user
        sudo -u "$USER" DBUS_SESSION_BUS_ADDRESS="$DBUS_ADDRESS" \
            notify-send -u critical -i dialog-warning "ClamAV Security Alert" "$MESSAGE"
    fi
done

exit 0
