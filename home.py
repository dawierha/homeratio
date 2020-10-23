from datetime import date
from schema import Schema
from schema import Regex
import matplotlib.pyplot as plt
import sys
import argparse

'''
These variables in combination with the specified data file is everything 
that needs to be modified in order to read a file with different format.
Only constraint is that they need to have one field for the start time 
and one for the end tim.'''
DATE_SCHEMA = Schema(Regex(r"^\d{1,}-([0]\d{1}|[1][0,1,2])-([0,1,2]\d{1}|[3][0,1])$")) #Format YYYY-MM-DD
DATE_DELIMITER = '-'
PRESENT_SCHEMA = "present"
NO_LABELS = 6
START_TIME_INDEX = 0
END_TIME_INDEX = 1


class HomeDate:
    
    #Creates an object of Class HomeDate and sets the attributes according to the first row (labels) in the data file
    def __init__(self, attributes, data):
        for i in range(len(attributes)):
            if i == START_TIME_INDEX:
                s_time_list = data[i].split(DATE_DELIMITER)
                setattr(self, attributes[i], date(int(s_time_list[0]), int(s_time_list[1]), int(s_time_list[2])))
            elif i == END_TIME_INDEX:
                if data[i] == PRESENT_SCHEMA:
                    setattr(self, attributes[i], date.today())
                else:
                    e_time_list = data[i].split(DATE_DELIMITER)
                    setattr(self, attributes[i], date(int(e_time_list[0]), int(e_time_list[1]), int(e_time_list[2])))
            else:
                setattr(self, attributes[i], data[i])
        
        self.time_delta = getattr(self, attributes[END_TIME_INDEX]) - getattr(self, attributes[START_TIME_INDEX])
        

def validate_date(date):
    if DATE_SCHEMA.is_valid(date) or date == PRESENT_SCHEMA:
        return True
    else:
        print(f"ERROR, Invalid date format '{date}'")
        return False


def parse_data(file_name, DataClass, debug=False):
    data_list = []
    with open(file_name, 'r') as file:
        line = file.readline()
        labels = line.split(',')
        labels = [h.strip().strip('\n') for h in labels]

        if debug: print(f"Labels: {labels}")
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
            if debug: print(f"Line {line_no}, data: {line_data}")
            if (len(line_data) != NO_LABELS):
                print(f"ERROR on line {line_no} in {file_name}, number of fields: {len(line_data)}. Should be {NO_LABELS}")
                return None, None
            
            if not validate_date(line_data[START_TIME_INDEX]) or not validate_date(line_data[END_TIME_INDEX]): return None
            data_list.append(DataClass(labels, line_data))

    return labels, data_list

#Aggregates the total number of days with the given loc_attr
def aggregate_data(data_list, loc_attr,debug=False):
    locations = {}
    total_days = 0
    for data in data_list:
        location = str(getattr(data, loc_attr))
        days = data.time_delta.days
        if location not in locations:
            locations[location] = days
        else:
            locations[location] += days
        total_days += days
    
    if debug: print(f"total days: {total_days}")

    return locations, total_days


def plot_dates(data_list, loc_attr, y_axis='percentage', pie_plot=False, nosort=False, reverse=False, debug=False):
    
    locations, total_days = aggregate_data(data_list, loc_attr, debug=debug)

    #Converts list to percentage
    if y_axis == 'percentage':
        for key in locations:
            locations[key] = locations[key]/total_days*100
        title_label = f"Percentage of days lived in each {loc_attr}"
    elif y_axis == 'days':
        title_label = f"Number of days lived in each {loc_attr}"
    else:
        print(f"ERROR, Invalid y_axis: {y_axis}")
        return None

    if not nosort:
        locations = {key: value for key, value in sorted(locations.items(), key=lambda item: item[1], reverse=not reverse)}
    if debug: print(locations)

    fig = plt.subplots(figsize =(12, 9))
    plt.title(title_label)
    
    if pie_plot:
        plt.pie(locations.values(), labels=locations.keys(), autopct='%1.1f%%', pctdistance=0.85, radius=1.2) 
    else:
        plt.bar(range(len(locations)), list(locations.values()), align='center')
        plt.xticks(range(len(locations)), list(locations.keys()))
        plt.xlabel(f"{loc_attr}")
        plt.ylabel(f"{y_axis}") 
       
    plt.show()
    

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate the number of days you have spent in different households')
    parser.add_argument("file", help="specifies the data file to read from")
    parser.add_argument("location", help="specifies the location resolution to sort on. I.e city or region, etc")
    parser.add_argument("-p", "--pie", help="plot as a pie chart instead", action="store_true", default=False)
    parser.add_argument("-a", "--axis",  help="unit to display the y-axis in. Either 'days' or 'percentage'. Default is 'percentage'",
                               default='percentage')
    parser.add_argument("-s", "--nosort", help="do not sort the x-axle", action="store_true", default=False)
    parser.add_argument("-r", "--reverse", help="reverse the x-axle. Must not be used with '--nosort'", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", default=False)
    args = parser.parse_args()
    
    if args.reverse and args.nosort:
        print(f"ERROR, argument '-r' must not be used with '-s'")
        sys.exit(-1)

    if args.pie and args.axis=='days':
        print(f"ERROR, argument '-p' must not be used with '-a days'")
        sys.exit(-1)

    labels, data_list = parse_data(args.file, HomeDate, debug=bool(args.verbose))
    if labels == None and data_list == None:
        print("Exited with errors")
        sys.exit(-1)

    plot_dates(data_list, args.location, y_axis=args.axis, 
                pie_plot=bool(args.pie), nosort=bool(args.nosort), 
                reverse=bool(args.reverse), debug=bool(args.verbose))