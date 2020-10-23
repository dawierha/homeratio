'''
These variables in combination with the specified data file is everything 
that needs to be modified in order to read a file with different format.
Only constraint is that they need to have one field for the start time 
and one for the end time.'''

DATE_REGEX = r"^\d{1,}-([0]\d{1}|[1][0,1,2])-([0,1,2]\d{1}|[3][0,1])$" #Format YYYY-MM-DD
DATE_DELIMITER = '-'
PRESENT_SCHEMA = "present"
START_TIME_INDEX = 0
END_TIME_INDEX = 1