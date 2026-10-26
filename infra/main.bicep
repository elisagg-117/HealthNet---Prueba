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