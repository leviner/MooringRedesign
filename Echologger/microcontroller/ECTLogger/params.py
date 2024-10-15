class params():
    # Deployment name, used for the log file and data file prefix
    deployment = 'GOA2025'
    # Log file name, if not using SD card modify here
    log_file = '/sd/'+deployment+'.log'
    # Ping configurations, see ECT D032 manual for details
    config = {'C1':{"IdTxLengthL":"1000",
                    "IdTxLengthH":"500",
                    "IdRangeL": "100000",
                    "IdRangeH": "100000",
                    "IdOutput": "100"},
              'C2':{"IdTxLengthL":"1000",
                    "IdTxLengthH":"500",
                    "IdRangeL": "50000",
                    "IdRangeH": "50000",
                    "IdOutput": "100"}}
    # Number of pings for each ensemble
    numPings = {'C1':10,'C2':10}
    # Maximum time (s) allowed for each ensemble
    maxTime =  {'C1':25,'C2':25}
    # Start time of the mission
    start_time = (2024,10,01,00,00,00,00,-1,-1)
    # End time of the mission
    end_time = (2024,10,30,00,00,00,00,-1,-1)
    # If not 1 or 60, is the time relative to the last wakeup
    wakeup_interval = 5 # Alarm interval in minutes
    # Minimum voltage for use in the 
    minimum_voltage = 10.5