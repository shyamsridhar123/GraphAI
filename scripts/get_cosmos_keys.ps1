#!/usr/bin/env pwsh
# Script to get Cosmos DB keys using Azure CLI

param (
    [Parameter(Mandatory=$true)]
    [string]$AccountName,
    
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroup
)

Write-Host "Retrieving keys for Cosmos DB account: $AccountName"

# List keys
$keys = az cosmosdb keys list `
    --name $AccountName `
    --resource-group $ResourceGroup `
    --query "{primaryMasterKey: primaryMasterKey, primaryReadonlyMasterKey: primaryReadonlyMasterKey}" `
    --output json | ConvertFrom-Json

Write-Host "`nPrimary Key (for writing):"
Write-Host $keys.primaryMasterKey
Write-Host "`nRead-only Key (for reading):"
Write-Host $keys.primaryReadonlyMasterKey

# Save to file
$keys | ConvertTo-Json | Out-File -FilePath "cosmos-keys.json" -Encoding utf8

Write-Host "`nKeys have been saved to cosmos-keys.json"
Write-Host "Use the primary key for uploading products"
