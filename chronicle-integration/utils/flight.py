def get_flight(chronicle_app_data_entset, chronicle_devices_entset, chronicle_participants_entset, subject_id, device_id, chronicle_recorded_by_entset):
    flight = '''entityDefinitions:
    activitydata:
      entitySetName: {chronicle_app_data_entset}
      fqn: ol.applicationdata
      name: activitydata
      propertyDefinitions:
        general.fullname:
          column: "70d2ff1c-2450-4a47-a954-a7641b7399ae"
          type: general.fullname
        ol.recordtype:
          type: ol.recordtype
          column: "285e6bfc-2a73-49ae-8cb2-b112244ed85d"
        general.stringid:
          type: general.stringid
          column: "ee3a7573-aa70-4afb-814d-3fad27cda988"
        ol.altitude:
          type: ol.altitude
          column: "1624fc2d-d221-48d2-a7b4-ee94f80a515b"
        location.latitude:
          type: location.latitude
          column: "06083695-aebe-4a56-9b98-da6013e93a5e"
        location.longitude:
          type: location.longitude
          column: "e8f9026a-2494-4749-84bb-1499cb7f215c"
        ol.datelogged:
          type: ol.datelogged
          column: "e90a306c-ee37-4cd1-8a0e-71ad5a180340"
        general.Duration:
          type: general.Duration
          column: "c106ee75-f18e-48ed-bc85-b75702bfe802"
        ol.datetimestart:
          type: ol.datetimestart
          column: "92a6a5c5-b4f1-40ce-ace9-be232acdce2a"
        general.EndTime:
          type: general.EndTime
          column: "00e5c55f-f1ef-4538-8d48-c08d5bcfe4c7"
        ol.timezone:
          type: ol.timezone
          column: "071ba832-035f-4b04-99e4-d11dc4fbe0e8"
    people:
      entitySetName: {chronicle_participants_entset}
      name: people
      fqn: general.person
      propertyDefinitions:
        nc.SubjectIdentification:
          type: nc.SubjectIdentification
          transforms:
          - !<transforms.ValueTransform>
            value: {subject_id}        
    devices:
      entitySetName: {chronicle_devices_entset}
      name: devices
      fqn: ol.device
      propertyDefinitions:
        general.stringid:
          type: general.stringid
          transforms:
          - !<transforms.ValueTransform>
            value: {device_id}        
associationDefinitions:
    recordedbyperson:
      entitySetName: {chronicle_recorded_by_entset}
      fqn: ol.recordedby
      name: recordedbyperson
      src: activitydata
      dst: people
      propertyDefinitions:
        general.stringid:
          type: general.stringid
          transforms:
          - !<transforms.ConcatCombineTransform>
            transforms:
            - !<transforms.ColumnTransform>
              column: "ee3a7573-aa70-4afb-814d-3fad27cda988"          
            - !<transforms.ValueTransform>
              value: "data"
    recordedbydevice:
      entitySetName: {chronicle_recorded_by_entset}
      fqn: ol.recordedby
      name: recordedbydevice
      src: activitydata
      dst: devices
      propertyDefinitions:
        general.stringid:
          type: general.stringid
          transforms:
          - !<transforms.ConcatCombineTransform>
            transforms:
            - !<transforms.ColumnTransform>
              column: "ee3a7573-aa70-4afb-814d-3fad27cda988"          
            - !<transforms.ValueTransform>
              value: "device"
    '''.format(
        chronicle_app_data_entset = chronicle_app_data_entset, 
        chronicle_devices_entset = chronicle_devices_entset,
        chronicle_participants_entset = chronicle_participants_entset,
        subject_id = subject_id,
        device_id = device_id,
        chronicle_recorded_by_entset = chronicle_recorded_by_entset
        )
    
    return flight
