#!/bin/bash

# Define destination
DEST="$(pwd)/opencode_config"
mkdir -p "$DEST"

# 1. Handle auth.json
SOURCE_AUTH="$HOME/.local/share/opencode/auth.json"
if [ -f "$SOURCE_AUTH" ]; then
    echo "Copying auth.json to $DEST..."
    cp "$SOURCE_AUTH" "$DEST/"
else
    echo "Notice: $SOURCE_AUTH not found, skipping."
fi

# 2. Handle antigravity-accounts.json
SOURCE_AG="$HOME/.config/opencode/antigravity-accounts.json"
if [ -f "$SOURCE_AG" ]; then
    echo "Copying antigravity-accounts.json to $DEST..."
    cp "$SOURCE_AG" "$DEST/"
else
    echo "Notice: $SOURCE_AG not found, skipping."
fi

# 3. Handle oh-my-opencode.json
SOURCE_OMO="$HOME/.config/opencode/oh-my-opencode.json"
if [ -f "$SOURCE_OMO" ]; then
    echo "Copying oh-my-opencode.json to $DEST..."
    cp "$SOURCE_OMO" "$DEST/"
else
    echo "Notice: $SOURCE_OMO not found, skipping."
fi

# 4. Handle opencode.json from example dir
SOURCE_EX="opencode_config_example/opencode.json"
if [ -f "$SOURCE_EX" ]; then
    echo "Copying opencode.json from $SOURCE_EX to $DEST..."
    cp "$SOURCE_EX" "$DEST/"
else
    echo "Notice: $SOURCE_EX not found, skipping."
fi

echo "Configuration copy process completed."