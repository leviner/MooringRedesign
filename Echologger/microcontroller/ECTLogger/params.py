class params():
    
    # Deployment name, used for the log file and data file prefix
    deployment = 'GOA25'
    
    # Log file name
    log_file = '/'+deployment+'.log'
    
    # The file used to hold the counter
    ct_file = '/count.txt'
    
    # Ping configurations, see ECT D032 manual for details
    config = {'C1':{"IdTxLengthL": "500",
                  "IdTxLengthH": "500",
                  "IdRangeL": "80000",
                  "IdRangeH": "80000",
                  "IdOutput": "100",
                  "IdSamplFreq": "12500",
                  "IdInterval": "1",
                  "IdSound": "1466",
                  "IdTVGMode": "3",
                  "IdTVGSprdL": "0",
                  "IdTVGSprdH": "0",
                  "IdTVGAbsL": "0.0",
                  "IdTVGAbsH": "0.0",
                  "IdGainL": "15",
                  "IdGainH": "20",
                  "IdAttnL": "0",
                  "IdAttnH": "0"},
            'C2':{"IdTxLengthL": "500",
                  "IdTxLengthH": "500",
                  "IdRangeL": "80000",
                  "IdRangeH": "80000",
                  "IdOutput": "100",
                  "IdSamplFreq": "12500",
                  "IdInterval": "1",
                  "IdSound": "1466",
                  "IdTVGMode": "3",
                  "IdTVGSprdL": "0",
                  "IdTVGSprdH": "0",
                  "IdTVGAbsL": "0.0",
                  "IdTVGAbsH": "0.0",
                  "IdGainL": "37.5",
                  "IdGainH": "40",
                  "IdAttnL": "0",
                  "IdAttnH": "0"},
            'C3':{"IdTxLengthL": "500",
                  "IdTxLengthH": "500",
                  "IdRangeL": "80000",
                  "IdRangeH": "80000",
                  "IdOutput": "100",
                  "IdSamplFreq": "12500",
                  "IdInterval": "1",
                  "IdSound": "1466",
                  "IdTVGMode": "3",
                  "IdTVGSprdL": "0",
                  "IdTVGSprdH": "0",
                  "IdTVGAbsL": "0.0",
                  "IdTVGAbsH": "0.0",
                  "IdGainL": "60",
                  "IdGainH": "60",
                  "IdAttnL": "0",
                  "IdAttnH": "0"}}
    
    # Number of pings for each ensemble
    numPings = {'C1':60,'C2':60,'C3':60}
    
    # Maximum time (s) allowed for each ensemble
    maxTime =  {'C1':60,'C2':60,'C3':60}
    
    # Relative to the hour (00:00), i.e., '5' means wakeup at
    # 00:05, 00:10, 00:15..., '120' means wakeup at 00:00, 02:00, 04:00...
    wakeup_interval = 30 # Alarm interval in minutes
    
    # Minimum voltage for use in the 
    minimum_voltage = 10.25
    
    # Maximum attempts to connect to ECT before aborting wakeup
    max_connect_attempts = 5
    
    # Time period for reduced ping test wakeup in days
    test_wakeup_days = 1
    
    # Time period for LED indicators in days
    LED_wakeup_days = 7
    
    # CURRENTLY UNUSED PARAMETERS
    # Start time of the mission
    start_time = (2024,10,01,00,00,00,00,-1,-1)
    # End time of the mission
    end_time = (2025,10,30,00,00,00,00,-1,-1)