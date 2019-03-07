def get_flight(entitysetname):
    flight = '''entityDefinitions:
    activitydata:
      entitySetName: chronicle_preprocessed_app_data
      fqn: ol.applicationdata
      name: activitydata
      propertyDefinitions:
        general.EndTime:
          type: general.EndTime
          transforms:
          - !<transforms.ConcatTransform>
            columns:
            - date
            - endtime
            separator: " "
          - !<transforms.SplitTransform>
            index: 0
            separator: "\\\."
          - !<transforms.DateTimeTransform>
            pattern: ['yyyy-MM-dd HH:mm:ss']
        general.fullname:
          column: app_fullname
          type: general.fullname
        general.stringid:
          type: general.stringid
          transforms:
          - !<transforms.HashTransform>
            columns: [participant_id, date, starttime, app_fullname]
            hashFunction: "sha256"
        general.Duration:
          type: general.Duration
          column: duration_seconds
        ol.datetimestart:
          type: ol.datetimestart
          transforms:
          - !<transforms.ConcatTransform>
            columns:
            - date
            - starttime
            separator:  " "
          - !<transforms.SplitTransform>
            index: 0
            separator: "\\\."
          - !<transforms.DateTimeTransform>
            pattern: ['yyyy-MM-dd HH:mm:ss']
    people:
      entitySetName: chronicle_participants_{entitysetname}
      fqn: general.person
      name: people
      propertyDefinitions:
        nc.SubjectIdentification:
          type: nc.SubjectIdentification
          column: participant_id
associationDefinitions:
    recordedby:
      entitySetName: chronicle_recorded_by
      fqn: ol.recordedby
      name: recordedby
      src: activitydata
      dst: people
      propertyDefinitions:
        general.stringid:
          type: general.stringid
          transforms:
          - !<transforms.HashTransform>
            columns: [participant_id, date, starttime, app_fullname]
            hashFunction: "sha256"            
    '''.format(entitysetname = entitysetname)
    return flight
