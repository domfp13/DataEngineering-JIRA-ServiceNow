# -*- coding: utf-8 -*-
# Luis Enrique Fuentes Plata
# Daniel Steinemann
# Angel Angel

from typing import Optional
import pandas as pd

# Abstract class
class Abstract:
  def values(self)->dict:
    return self.__dict__

# Users
class User(Abstract):
  def __init__(self, **kwards):
    self.active = kwards.get('active')
    self.email = kwards.get('email')
    self.employee_number = kwards.get('employee_number')
    self.first_name = kwards.get('first_name')
    self.last_name = kwards.get('last_name')
    self.u_visible_sys_id = kwards.get('u_visible_sys_id')

class Users:
  def __init__(self, session_handler):
    self.__url = 'https://iaas.service-now.com/sys_user_list.do?sysparm_query=u_visible_sys_id%3D'
    self.__session_handler = session_handler
    self.ids = set()
      
  def addUsers(self)->None:
    """Uses the ids variable to create a REST API request to ServiceNow and get information about 
    Users with Task/Incidents. This method creates the df (Pandas DataFrame)

    Returns:
        None
    """
    # if self.ids is 
    if len(self.ids) != 0:
      #creating List that will hold the dictionaries
      final_list = []

      # Transforming set to list
      lst = list(self.ids)
      # Creating a generator so the data gets process by chucks of users
      def chunks(lst:list, n:int):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

      # Uses the chuncks inner function in chuncks of 10 different users
      for chuck in chunks(lst, 10):
        concatenatedString = ""
        for assigned_to in chuck:
          concatenatedString = "{x}{y}^ORu_visible_sys_id%3D".format(x = concatenatedString, y = assigned_to)
      
        for x in self.__session_handler.instance.get('{url}{ids}{json}'.format(url=self.__url, ids=concatenatedString[:len(concatenatedString)-22], json='&JSON')).json()['records']:
          final_list.append(User(**x).values())
      
      self.df = pd.DataFrame(final_list)
    else:
      # if there are no self.ids then return an empty Dataframe
      self.df = pd.DataFrame([{}], columns= ['active', 'email', 'employee_number', 'first_name', 'last_name','u_visible_sys_id'])
      self.df.fillna("", inplace=True)

# Tasks
class Task(Abstract):

  # Class variables
  registry = {1: 'New',
              2: 'Active',
              3: 'Work Started',
              4: 'Awaiting Customer Info',
              6: 'Closed',
              9: 'In Progress'}

  def __init__(self, **kwards):
    self.number = kwards.get('number')
    self.assigned_to = kwards.get('assigned_to')
    self.description = kwards.get('description')
    self.sys_updated_by = kwards.get('sys_updated_by')
    self.sys_updated_on = kwards.get('sys_updated_on')
    self.priority = kwards.get('priority')
    self.opened_at = kwards.get('opened_at')
    self.short_description = kwards.get('short_description')
    self.sys_created_by = kwards.get('sys_created_by')
    self.opened_by = kwards.get('opened_by')
    self.state = kwards.get('state')
    self.state_description = self.task_state_desc()
    self.u_resolution_code = None
    
  def task_state_desc(self)->str:
    """This method is used to parse and return data using the class variable "registry"

    Returns:
        str
    """
    return Task.registry[int(self.state)]

class Tasks:
  def __init__(self, session_handler, group_id:str):
    self.__url = "https://iaas.service-now.com/sc_task_list.do?sysparm_query=assignment_group%3D{group_id}%5Esys_updated_on%3E%3Djavascript:gs.beginningOfYesterday()"
    self.__session_handler = session_handler
    self.group_id = group_id
    self.df = pd.DataFrame(self.__addTasks())

  def __addTasks(self)->list:
    """REST API request to ServiceNow, it uses the group_id as part of the URL, this method return a list
    of dictionaries parsed already with the Task class

    Returns:
        list: list of dictionries
    """
    return [Task(**x).values() for x in self.__session_handler.instance.get(self.__url.format(group_id=self.group_id) + '&JSON').json()['records']]

  def getAssignedTo(self, users:Users)->None:
    """This method uses an object of Users and it uses its dataframe to get the 'assigned_to' to add them 
    to the Users.ids (Set).

    Args:
        users (Users): Instance of Users class
    """
    try:
      lst = self.df['assigned_to'].to_list()
      
      while "" in lst:
        # Removes empty assigned_to users 
        lst.remove("")
      
      if len(lst)>0:
        users.ids.update(lst)
    except:
      pass

# Incidents
class Incident(Abstract):

  # Class variable
  registry = {1: "New",
              2: "Active",
              3: "Awaiting Problem",
              4: "Awaiting User Info",
              5: "Awaiting Evidence",
              6: "Resolved",
              7: "Closed",
              8: "Work Started",
              9: "Awaiting Change",
              10: "Awaiting Vendor"}

  def __init__(self, **kwards):
    self.number = kwards.get('number')
    self.assigned_to = kwards.get('assigned_to')
    self.description = kwards.get('description')
    self.sys_updated_by = kwards.get('sys_updated_by')
    self.sys_updated_on = kwards.get('sys_updated_on')
    self.priority = kwards.get('priority')
    self.opened_at = kwards.get('opened_at')
    self.short_description = kwards.get('short_description')
    self.sys_created_by = kwards.get('sys_created_by')
    self.opened_by = kwards.get('opened_by')
    self.state = kwards.get('incident_state')
    self.state_description = self.inicident_state_desc()
    self.u_resolution_code = kwards.get('u_resolution_code')

  def inicident_state_desc(self)->str:
    """This method is used to parse and return data using the class variable "registry"

    Returns:
        str
    """
    return Incident.registry[int(self.state)]
    
class Incidents:
  def __init__(self, session_handler, group_id:str):
    self.__url = "https://iaas.service-now.com/incident_list.do?sysparm_query=assignment_group%3D{group_id}%5Esys_updated_on%3E%3Djavascript:gs.beginningOfYesterday()"
    self.__session_handler = session_handler
    self.group_id = group_id
    self.df = pd.DataFrame(self.__addIncidents())

  def __addIncidents(self):
    """REST API request to ServiceNow, it uses the group_id as part of the URL, this method return a list
    of dictionaries parsed already with the Incidents class

    Returns:
        list: list of dictionries
    """
    return [Incident(**x).values() for x in self.__session_handler.instance.get(self.__url.format(group_id=self.group_id) + '&JSON').json()['records']]

  def getAssignedTo(self, users:Users)->None:
    """This method uses an object of Users and it uses its dataframe to get the 'assigned_to' to add them 
    to the Users.ids (Set).

    Args:
      users (Users): Instance of Users class
    
    Returns:
      None
    """
    try:
      lst = self.df['assigned_to'].to_list()

      while "" in lst:
        # Removes empty assigned_to users 
        lst.remove("")

      if len(lst)>0:
        users.ids.update(lst)
    except:
      pass