#!/bin/bash

# Clean images files out of the BMU temp directory.

if [[ -z $CS_TEMP_MMIN ]]; then
	CS_TEMP_MMIN=2880 # Minimum minutes since last modification required for a file to be deleted
        # 2880 mins = 48 hours
fi

TEMP_DIR=/tmp/image_upload_cache_$1

if [[ ! -d $TEMP_DIR ]]; then
        echo "could not find $TEMP_DIR"
        exit 1
fi

COUNT=0

cd "$TEMP_DIR"

echo "`date`: Cleaning `pwd`"

while read f
do
	echo "Removing $f"

	/bin/rm -rf "$f"

	if [[ -e $f ]]; then
		echo "ERROR: Failed to remove $f"
	else
		COUNT=$((COUNT+1))
	fi
done < <(find . -type f ! -name "*.csv" -a ! -name "*.log" -mmin +${CS_TEMP_MMIN})

echo "Removed $COUNT files from `pwd`"
