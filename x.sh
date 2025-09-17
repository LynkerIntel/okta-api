#! /bin/sh
export DATA="{
    \"key_id\": \"${KEY_ID}\",
    \"key_secret\": \"${KEY_SECRET}\"
  }"
echo ---
echo $DATA
echo ---

OUTPUT=$(curl  --location "https://noaa.pam.okta.com/v1/teams/nos-coastal-modeling-cloud-sandbox/service_token" \
  --header 'Content-Type: application/json' \
  --header 'Accept: application/json' \
  --data "$DATA")
echo $OUTPUT
export BEARER_TOKEN=$(echo $OUTPUT | jq -r '.bearer_token')

echo ---
curl -i -X POST   "https://noaa.pam.okta.com/v1/teams/nos-coastal-modeling-cloud-sandbox/projects/${OKTA_TARGET_PROJECT}/server_enrollment_tokens" \
   -H 'Content-Type: application/json' -H "Authorization: Bearer ${BEARER_TOKEN}"   -d "{ \"description\": \"test\"  }"
