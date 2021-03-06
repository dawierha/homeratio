from datetime import date
from schema import Schema
from schema import Regex
import matplotlib.pyplot as plt
import sys
import argparse
import traceback
from config import *

DATE_SCHEMA = Schema(Regex(DATE_REGEX)) #Format YYYY-MM-DD


class HomeDate:
    """Class for storing time data for a location
    """
    def __init__(self, attributes, data):
        """
        Creates an object and sets the attributes according to the first row (labels) in the data file

        Args:
            attributes (list of str: These will form the class attributes
            data (list of int and str): Data for the attributes
        """
        self.loc_list = [] # list with all the available locations
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
                self.loc_list.append(attributes[i])
        
        self.time_delta = getattr(self, attributes[END_TIME_INDEX]) - getattr(self, attributes[START_TIME_INDEX])

def validate_date(date, line_no):
    if DATE_SCHEMA.is_valid(date) or date == PRESENT_SCHEMA:
        return True
    else:
        print(f"ERROR, Invalid date format '{date}' on line {line_no}")
        return False


def parse_data(file_name, DataClass, debug=False):
    data_list = []
    with open(file_name, 'r') as file:
        line = file.readline()
        labels = line.split(',')
        labels = [h.strip().strip('\n') for h in labels]
        no_labels = len(labels)
        if debug: print(f"Labels: {labels}")

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
            if (len(line_data) != no_labels):
                print(f"ERROR on line {line_no} in {file_name}, number of fields: {len(line_data)}. Should be {no_labels}")
                return None, None
            
            if not validate_date(line_data[START_TIME_INDEX], line_no) or not validate_date(line_data[END_TIME_INDEX], line_no): return None, None
            data_list.append(DataClass(labels, line_data))

    return labels, data_list

#Aggregates the total number of days with the given loc_attr
def aggregate_data(data_list, loc_attr,debug=False):
    locations = {}
    total_days = 0
    for data in data_list:
        try:
            location = str(getattr(data, loc_attr))
        except AttributeError:
            if debug: traceback.print_exc() 
            print(f"ERROR, location '{loc_attr}' is not specified as a label.")
            print(f"Available location labels: {data.loc_list}")
            sys.exit(-1)

        days = data.time_delta.days
        if location not in locations:
            locations[location] = days
        else:
            locations[location] += days
        total_days += days
    
    if debug: print(f"total days: {total_days}")

    return locations, total_days


def plot_dates(data_list, loc_attr, y_axis='percentage', pie_plot=False, nosort=False, reverse=False, debug=False):
    """Plot the number of days as a bar or a pie chart at the given location

    Args:
        data_list (list of HomeData): List with the number of days spent in one location
        loc_attr (str): Specifies which location to sort on
        y_axis (str, optional): Y-axis unit, can be either 'percentage' or 'days'. Defaults to 'percentage'.
        pie_plot (bool, optional): Flag for creating a pie chart instead of a bar plot. Defaults to False.
        nosort (bool, optional): Flag for not sorting the bar graph's columns. Defaults to False.
        reverse (bool, optional): Flag for reversing the sort of the bar graph's columns. Defaults to False.
        debug (bool, optional): Flag for printing debugging statements. Defaults to False.

    Returns:
        Does not return anything
    """

    locations, total_days = aggregate_data(data_list, loc_attr, debug=debug)

    #Converts list to percentage
    if y_axis == 'percentage':
        for key in locations:
            locations[key] = locations[key]/total_days*100
        title_label = f"Percentage of days lived in each {loc_attr}"
        y_axis = "%"
    elif y_axis == 'days':
        title_label = f"Number of days lived in each {loc_attr}"
    else:
        print(f"ERROR, Invalid y_axis: {y_axis}")
        return None

    if not nosort:
        locations = {key: value for key, value in sorted(locations.items(), key=lambda item: item[1], reverse=not reverse)}
    if debug: print(locations)

    fig, ax = plt.subplots(figsize =(12, 9))
    plt.title(title_label)

    if pie_plot:
        plt.pie(locations.values(), labels=locations.keys(), autopct='%1.1f%%', pctdistance=0.85, radius=1.2) 
    else:
        plt.bar(range(len(locations)), list(locations.values()), align='center')
        plt.xticks(range(len(locations)), list(locations.keys()))
        plt.xlabel(f"{loc_attr}")
        plt.ylabel(f"{y_axis}") 
        
        #Prints the number of days/percentage on top of the bar
        x=0
        for y in locations.values():
            plt.text(x-0.1,y+(0.01*ax.get_ylim()[1]), f"{y:.4g} {y_axis}") 
            x+=1

    

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate the number of days you have spent in different households')
    parser.add_argument("file", help="specifies the data file to read from")
    parser.add_argument("location", nargs='+', help="specifies the location resolution to sort on. I.e city or region, etc")
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
    for location in args.location:
        plot_dates(data_list, location, y_axis=args.axis, 
                    pie_plot=bool(args.pie), nosort=bool(args.nosort), 
                    reverse=bool(args.reverse), debug=bool(args.verbose))
    plt.show()
    
