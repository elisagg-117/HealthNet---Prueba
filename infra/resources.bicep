targetScope = 'resourceGroup'

param location string
param environment string
param storageAccountName string
param storageSku string
param containerNames array
param dataFactoryName string
param selfHostedIrName string
param keyVaultName string
param keyVaultSku string
param logAnalyticsName string
param logRetentionDays int
param factoryDiagnosticsName string

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: storageSku
  }
  tags: {
    project: 'HealthNet'
    environment: environment
  }
  properties: {
    isHnsEnabled: true
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    publicNetworkAccess: 'Enabled'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' existing = {
  parent: storage
  name: 'default'
}

resource containers 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = [for containerName in containerNames: {
  parent: blobService
  name: containerName
  properties: {
    publicAccess: 'None'
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
  }
}]

output storageId string = storage.id
output storageName string = storage.name
output storageEndpoints object = storage.properties.primaryEndpoints
output containerDetails array = [for (containerName, index) in containerNames: {
  name: containerName
  id: containers[index].id
}]

resource factory 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: dataFactoryName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  tags: {
    project: 'HealthNet'
    environment: environment
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

resource localRuntime 'Microsoft.DataFactory/factories/integrationRuntimes@2018-06-01' = {
  parent: factory
  name: selfHostedIrName
  properties: {
    type: 'SelfHosted'
  }
}

var blobContributorRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
)

resource factoryStorageRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, factory.id, blobContributorRoleId)
  scope: storage
  properties: {
    roleDefinitionId: blobContributorRoleId
    principalId: factory.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

output factoryId string = factory.id
output factoryName string = factory.name
output factoryPrincipalId string = factory.identity.principalId
output runtimeId string = localRuntime.id
output runtimeName string = localRuntime.name
output storageRoleAssignmentId string = factoryStorageRole.id


resource vault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: {
    project: 'HealthNet'
    environment: environment
  }
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: keyVaultSku
    }
    enableRbacAuthorization: true
    accessPolicies: []
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    publicNetworkAccess: 'Enabled'
  }
}

var vaultSecretsUserRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '4633458b-17de-408a-b874-0445c86b69e6'
)

resource factoryVaultRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(vault.id, factory.id, vaultSecretsUserRoleId)
  scope: vault
  properties: {
    roleDefinitionId: vaultSecretsUserRoleId
    principalId: factory.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

output vaultId string = vault.id
output vaultName string = vault.name
output vaultUri string = vault.properties.vaultUri
output vaultRoleAssignmentId string = factoryVaultRole.id

resource logWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: {
    project: 'HealthNet'
    environment: environment
  }
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: logRetentionDays
    features: {
      disableLocalAuth: true
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

resource factoryDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: factoryDiagnosticsName
  scope: factory
  properties: {
    workspaceId: logWorkspace.id
    logAnalyticsDestinationType: 'Dedicated'
    logs: [
      {
        category: 'PipelineRuns'
        enabled: true
      }
      {
        category: 'ActivityRuns'
        enabled: true
      }
      {
        category: 'TriggerRuns'
        enabled: true
      }
    ]
  }
}

output logWorkspaceId string = logWorkspace.id
output logWorkspaceName string = logWorkspace.name
output logWorkspaceCustomerId string = logWorkspace.properties.customerId
output factoryDiagnosticsId string = factoryDiagnostics.id