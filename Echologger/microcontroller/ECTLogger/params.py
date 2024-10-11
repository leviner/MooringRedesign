class params():
    # 
    deployment = 'GOA2025'
    log_file = '/sd/'+deployment+'.log'
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
    numPings = {'C1':10,'C2':10}
    maxTime =  {'C1':25,'C2':25}
    start_time = (2024,10,01,00,00,00,00,-1,-1)
    end_time = (2024,10,20,00,00,00,00,-1,-1)
    minimum_voltage = 10.5
              
                    