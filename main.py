# -*- coding: utf-8 -*-
# Luis Enrique Fuentes Plata
# Daniel Steinemann
# Angel Angel
# export GOOGLE_APPLICATION_CREDENTIALS=/Users/domfp13/CloudKeys/luis-defaul-microstrategyit.json

# External Modules
from typing import Optional
from json import dumps
import logging
import pandas as pd

# Local Modules
from etl.GeneralFunctions import getGroupIds, convertToCSV, send_to_bucket
from etl.ServiceNow import SessionHandler
from etl.EtlServiceNowClasses import Users, Tasks, Incidents

def JiraServiceNow(request):
    """Responds to any HTTP request
    Args:
        request: HTTP request object
    Returns:
        The response text or any set of values that can be turned into a
        Response object. 
    """
    try:
        logging.info("Start")

        # This object its being used across different classes
        logging.info("1.- Creating session_handler")
        session_handler = SessionHandler()

        # Getting the JIRA reference object (API call to Google sheets)
        logging.info("2.- Getting REST API respons from Google Sheets")
        for element in getGroupIds().items():
            
            logging.info("3.- Creating Users")
            users = Users(session_handler)

            logging.info("4.- Creating Tasks and adding to Users")
            tasks = Tasks(session_handler, element[1])
            tasks.getAssignedTo(users)

            logging.info("5.- Creating Incidents and adding to Users")
            incidents = Incidents(session_handler, element[1])
            incidents.getAssignedTo(users)

            logging.info("6.- users instance creating df")
            users.addUsers()
            
            # Prevents error by verifying dfs exists
            if ~incidents.df.empty or ~tasks.df.empty:
                data_concat = pd.concat([incidents.df, tasks.df], ignore_index=True, sort=False)

                logging.info("7.- Joining concatenated df with users df")
                join_data = pd.merge(data_concat, users.df, how='left', left_on='assigned_to', right_on='u_visible_sys_id')

                logging.info("8.- Converting DataFrame to csv file")
                file_full_path = convertToCSV(join_data, element[0].replace(" ", ""))
                
                logging.info("8.- Uploading Data to bucket")
                send_to_bucket(file_full_path)

        # Finishing process by sending success response    
        return dumps({'success': True}), 200, {'ContentType': 'application/json'}

    except Exception as e:
        logging.exception(element[0].replace(" ", ""), ' ', e)
        return dumps({'success': False}), 400, {'ContentType': 'application/json'}    