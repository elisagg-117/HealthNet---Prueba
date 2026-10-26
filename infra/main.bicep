targetScope = 'subscription'

param resourceGroupName string
param location string

@allowed([
  'dev'
  'prod'
])
param environment string

@minLength(3)
@maxLength(24)
param storageAccountName string

@allowed([
  'Standard_LRS'
  'Standard_ZRS'
])
param storageSku string

param containerNames array
param dataFactoryName string
param selfHostedIrName string

param keyVaultName string
@allowed([
  'standard'
  'premium'
])
param keyVaultSku string

param logAnalyticsName string
param logRetentionDays int
param factoryDiagnosticsName string

param actionGroupName string
param actionGroupLocation string
param alertEmail string


resource resourceGroup 'Microsoft.Resources/resourceGroups@2025-04-01' = {
  name: resourceGroupName
  location: location
  tags: {
    project: 'HealthNet'
    environment: environment
  }
}

module resources './resources.bicep' = {
  name: 'healthnet-${environment}-resources'
  scope: resourceGroup
  params: {
    location: location
    environment: environment
    storageAccountName: storageAccountName
    storageSku: storageSku
    containerNames: containerNames
    dataFactoryName: dataFactoryName
    selfHostedIrName: selfHostedIrName
    keyVaultName: keyVaultName
    keyVaultSku: keyVaultSku
    logAnalyticsName: logAnalyticsName
    logRetentionDays: logRetentionDays
    factoryDiagnosticsName: factoryDiagnosticsName
    actionGroupName: actionGroupName
    actionGroupLocation: actionGroupLocation
    alertEmail: alertEmail
  }
}

output rgId string = resourceGroup.id
output rgName string = resourceGroup.name
output rgLocation string = resourceGroup.location
output storageId string = resources.outputs.storageId
output storageName string = resources.outputs.storageName
output storageEndpoints object = resources.outputs.storageEndpoints
output containerDetails array = resources.outputs.containerDetails

output factoryId string = resources.outputs.factoryId
output factoryName string = resources.outputs.factoryName
output factoryPrincipalId string = resources.outputs.factoryPrincipalId
output runtimeId string = resources.outputs.runtimeId
output runtimeName string = resources.outputs.runtimeName
output storageRoleAssignmentId string = resources.outputs.storageRoleAssignmentId

output vaultId string = resources.outputs.vaultId
output vaultName string = resources.outputs.vaultName
output vaultUri string = resources.outputs.vaultUri
output vaultRoleAssignmentId string = resources.outputs.vaultRoleAssignmentId

output logWorkspaceId string = resources.outputs.logWorkspaceId
output logWorkspaceName string = resources.outputs.logWorkspaceName
output logWorkspaceCustomerId string = resources.outputs.logWorkspaceCustomerId
output factoryDiagnosticsId string = resources.outputs.factoryDiagnosticsId

output actionGroupId string = resources.outputs.actionGroupId
output actionGroupName string = resources.outputs.actionGroupResourceName