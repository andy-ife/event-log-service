# Event-Log-Service

Run this SQL in openmrs DB to update the sync strategy before running this app:

`update global_property set property_value='org.bahmni.module.bahmniOfflineSync.strategy.LocationBasedSyncStrategy' where property='bahmniOfflineSync.strategy';`
