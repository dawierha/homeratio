from datetime import date
from schema import Schema
from schema import Regex
import matplotlib.pyplot as plt

DATE_SCHEMA = Schema(Regex(r"^\d{1,}-([0]\d{1}|[1][0,1,2])-([0,1,2]\d{1}|[3][0,1])$"))
PRESENT_SCHEMA = "present"
NO_LABELS = 6
START_TIME_INDEX = 4
END_TIME_INDEX = 5


class HomeDate:
    def __init__(self, data):
        self.country = data[0] 
        self.region = data[1]
        self.city = data[2]
        self.address = data[3]
        s_time_list = data[4].split('-')
        self.start_time = date(int(s_time_list[0]), int(s_time_list[1]), int(s_time_list[2]))
        
        if data[5] == PRESENT_SCHEMA:
            self.end_time = date.today()
        else:
            e_time_list = data[5].split('-')
            self.end_time = date(int(e_time_list[0]), int(e_time_list[1]), int(e_time_list[2])) 

        self.time_delta = self.end_time - self.start_time


def validate_date(date):
    if DATE_SCHEMA.is_valid(date) or date == PRESENT_SCHEMA:
        return True
    else:
        print(f"ERROR, Invalid date format '{date}'")
        return False

def parse_data(file_name, DataClass):
    data_list = []
    with open(file_name, 'r') as file:
        line = file.readline()
        labels = line.split(',')
        labels = [h.strip().strip('\n') for h in labels]

        print(labels)
        if (len(labels) != NO_LABELS):
            print(f"ERROR, number of labels: {len(labels)}. Should be {NO_LABELS}")
            return None, None

        line_no = 1     
        while line:
            line_no += 1
            line = file.readline()

            # There is often newline characther at the end of the line
            if line == '' or line == '\n':
                break

            line_data = line.split(',')
            line_data = [ld.strip().strip('\n') for ld in line_data] #Cleaning up input data
            print(line_data)
            if (len(line_data) != NO_LABELS):
                print(f"ERROR on line {line_no} in {file_name}, number of fields: {len(line_data)}. Should be {NO_LABELS}")
                return None, None
            
            if not validate_date(line_data[START_TIME_INDEX]) or not validate_date(line_data[END_TIME_INDEX]): return None
            data_list.append(DataClass(line_data))

    return labels, data_list

def plot_date(data_list, loc_attr, time_attr):
    locations = {}
    total_days = 0
    for data in data_list:
        location = str(getattr(data, loc_attr))
        days = getattr(data, time_attr).days
        if location not in locations:
            locations[location] = days
        else:
            locations[location] += days
        total_days += days
    
    print(f"total days: {total_days}")
    print(locations)

    #Converts list to percentage
    for key in locations:
        locations[key] = locations[key]/total_days*100

    plt.bar(range(len(locations)), list(locations.values()), align='center')
    plt.xticks(range(len(locations)), list(locations.keys()))
    plt.show()

    

labels, data_list = parse_data('data.csv', HomeDate)
if labels == None and data_list == None:
    print("Exited with errors")
    exit(0)

plot_date(data_list, 'region', 'time_delta')
