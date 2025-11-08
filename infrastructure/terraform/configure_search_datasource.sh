#!/bin/bash

SEARCH_SERVICE_NAME="maya-dev-search"
RESOURCE_GROUP="maya-dev-rg"
COSMOS_ACCOUNT="maya-dev-cosmos-db"

# Get Search Service admin key
SEARCH_KEY=$(az search admin-key show \
  --resource-group $RESOURCE_GROUP \
  --service-name $SEARCH_SERVICE_NAME \
  --query primaryKey -o tsv)

# Get Cosmos DB connection string
COSMOS_CONN=$(az cosmosdb keys list \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" -o tsv)

SEARCH_ENDPOINT="https://${SEARCH_SERVICE_NAME}.search.windows.net"

# Create Data Source
curl -X PUT "${SEARCH_ENDPOINT}/datasources/maya-dev-ds?api-version=2023-11-01" \
  -H "Content-Type: application/json" \
  -H "api-key: ${SEARCH_KEY}" \
  -d '{
    "name": "maya-dev-ds",
    "type": "cosmosdb",
    "credentials": {
      "connectionString": "'"${COSMOS_CONN}"'"
    },
    "container": {
      "name": "embeddings",
      "query": "SELECT * FROM c WHERE (c.doc_type = '\''PDF'\'') AND c._ts > @HighWaterMark ORDER BY c._ts"
    },
    "dataChangeDetectionPolicy": {
      "@odata.type": "#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy",
      "highWaterMarkColumnName": "_ts"
    }
  }'

echo "Data source created successfully"