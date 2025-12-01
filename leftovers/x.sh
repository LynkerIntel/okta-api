#! /bin/sh
export DATA="{
    \"key_id\": \"${KEY_ID}\",
    \"key_secret\": \"${KEY_SECRET}\"
  }"
echo ---
echo $DATA
echo ---

OUTPUT=$(curl  --location "https://${OKTA_ORG}.pam.okta.com/v1/teams/${OKTA_TEAM}/service_token" \
  --header 'Content-Type: application/json' \
  --header 'Accept: application/json' \
  --data "$DATA")
echo $OUTPUT
export BEARER_TOKEN=$(echo $OUTPUT | jq -r '.bearer_token')

echo ---
curl -i -X POST   "https://${OKTA_ORG}.pam.okta.com/v1/teams/${OKTA_TEAM}/projects/${OKTA_TARGET_PROJECT}/server_enrollment_tokens" \
   -H 'Content-Type: application/json' -H "Authorization: Bearer ${BEARER_TOKEN}"   -d "{ \"description\": \"test\"  }"
