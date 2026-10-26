targetScope = 'subscription'

param resourceGroupName string
param location string

@allowed([
  'dev'
  'prod'
])
param environment string

resource resourceGroup 'Microsoft.Resources/resourceGroups@2025-04-01' = {
  name: resourceGroupName
  location: location
  tags: {
    project: 'HealthNet'
    environment: environment
  }
}

output rgId string = resourceGroup.id
output rgName string = resourceGroup.name
output rgLocation string = resourceGroup.location
