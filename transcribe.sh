#!/bin/bash

for file in *.mp3; do
    # Replace spaces with underscores
    NEW_NAME=$(echo $file | tr ' ' '_')
    BASE_NAME=${NEW_NAME%.mp3}
    echo $BASE_NAME
    
    mv "$file" $NEW_NAME;
    echo "Renamed file to $NEW_NAME"

    # Convert to mono-channel flac
    FLAC_NAME="$BASE_NAME.flac"
    ffmpeg -i $NEW_NAME -ac 1 -ab 44k $FLAC_NAME
    sleep 60
    echo "Converted $NEW_NAME to flac"

    # Upload to google cloud and set to public
    gsutil cp $FLAC_NAME gs://pod_transcriber
    gsutil acl ch -u AllUsers:R gs://pod_transcriber/$FLAC_NAME
    echo "Uploaded $FLAC_NAME to gcloud"

    # Output into txt file
    python3 transcribe_async.py gs://pod_transcriber/$FLAC_NAME > "$BASE_NAME transcript".txt
    sleep 120
	
done
