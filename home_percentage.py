from datetime import date
from schema import Schema
from schema import Regex
import matplotlib.pyplot as plt

DATE_SCHEMA = Schema(Regex(r"^\d{1,}-([0]\d{1}|[1][0,1,2])-([0,1,2]\d{1}|[3][0,1])$"))
DATE_DELIMITER = '-'
PRESENT_SCHEMA = "present"
NO_LABELS = 6
START_TIME_INDEX = 4
END_TIME_INDEX = 5


class HomeDate:
    def calc_time_diff(self):
        self.time_delta = self.end_time - self.start_time

#Creates an object of Class HomeDate and sets the attributes according to the first row (labels) in the data file
def create_data(attributes, data):
    hd = HomeDate()
    for i in range(len(attributes)):
        if i == START_TIME_INDEX:
            s_time_list = data[i].split(DATE_DELIMITER)
            setattr(hd, attributes[i], date(int(s_time_list[0]), int(s_time_list[1]), int(s_time_list[2])))
        elif i == END_TIME_INDEX:
            if data[i] == PRESENT_SCHEMA:
                setattr(hd, attributes[i], date.today())
            else:
                e_time_list = data[5].split(DATE_DELIMITER)
                setattr(hd, attributes[i], date(int(e_time_list[0]), int(e_time_list[1]), int(e_time_list[2])))
        else:
            setattr(hd, attributes[i], data[i])
    hd.calc_time_diff()

    return hd

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
            data_list.append(DataClass(labels, line_data))

    return labels, data_list

def plot_date(data_list, loc_attr, time_attr, y_axis='percentage', sort=True):
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

    #Converts list to percentage
    if y_axis == 'percentage':
        for key in locations:
            locations[key] = locations[key]/total_days*100
    elif y_axis == 'days':
        pass
    else:
        print(f"Invalid y_axis: {y_axis}")
        return None

    if sort:
        locations = {key: value for key, value in sorted(locations.items(), key=lambda item: item[1], reverse=True)}

    print(locations)
    plt.bar(range(len(locations)), list(locations.values()), align='center')
    plt.xticks(range(len(locations)), list(locations.keys()))
    plt.show()

    

labels, data_list = parse_data('data.csv', create_data)
if labels == None and data_list == None:
    print("Exited with errors")
    exit(0)

plot_date(data_list, 'region', 'time_delta', y_axis='percentage')
