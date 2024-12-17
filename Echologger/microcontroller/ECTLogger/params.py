class params():
    
    # Deployment name, used for the log file and data file prefix
    deployment = 'G25'
    
    # Log file name
    log_file = '/'+deployment+'.log'
    
    # The file used to hold the counter
    ct_file = '/count.txt'
    
    # Ping configurations, see ECT D032 manual for details
    config = {'C1':{"IdTxLengthL":"1000",
                    "IdTxLengthH":"500",
                    "IdRangeL": "80000",
                    "IdRangeH": "80000",
                    "IdOutput": "100"},
              'C2':{"IdTxLengthL":"1000",
                    "IdTxLengthH":"500",
                    "IdRangeL": "80000",
                    "IdRangeH": "80000",
                    "IdOutput": "100"},
              'C3':{"IdTxLengthL":"1000",
                    "IdTxLengthH":"500",
                    "IdRangeL": "80000",
                    "IdRangeH": "80000",
                    "IdOutput": "100"}}
    
    # Number of pings for each ensemble
    numPings = {'C1':10,'C2':10,'C3':10}
    
    # Maximum time (s) allowed for each ensemble
    maxTime =  {'C1':40,'C2':40,'C3':40}
    
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