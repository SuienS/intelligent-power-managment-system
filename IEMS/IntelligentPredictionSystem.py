from firebase import firebase
import datetime

"""
===================================================================
      Intelligent Statistics and Predictions Generating System
      By Rammuni Ravidu Suien Silva
      IIT No - 2016134
      UoW No - 16267097
===================================================================

"""

"""
--------------------------------------------------------------------------
    This program will identify the patterns of the user's current
    usage data. With the identified pattern this will divide the
    daily goal of the user accordingly to 4-hour sets of a day.
    The users pattern will be adapted daily according the usage
    of the user. Also the prediction of the month-end usage will 
    also adapted daily.
    
    Even for the each device this program identifies the usage 
    pattern and amount of all the devices and divides the daily
    usage goal for each device, which will ultimatly help the user
    to find where and which sepcific device he has failed to achieve his
    goal.
---------------------------------------------------------------------------

"""
# Firebase linking
firebase = firebase.FirebaseApplication('https://swatt-d1414.firebaseio.com', None)

day = 0  # denotes the spent time period of the day
# home data storing variables
curGoal = 50  # current goal for the home per day
# predictions and statistics calculations will happen aiming 6 4-hour sets in the day
# six 4-hour sets for a day (4-hourSet * 6 = 24Hours)
dayUsageSet = [0, 0, 0, 0, 0, 0]  # last day's usages
usageSet = [10, 10, 10, 10, 10, 10]  # total 4-hour set based usages from the installation of the system

# goals will be divided into the 4-hours sets in the day
# It will be divided according to the dynamically updating usage patterns of the user
# This program identifies the users electricity usage patterns and divides user's day-goal accordingly to 4-hours sets
usagePatternSet = [0, 0, 0, 0, 0, 0]  # usage pattern for the sets
goalSet = [0, 0, 0, 0, 0, 0]  # allocated goals for each set
devices = []  # device list


# This function(method) will help to divide the user's day goal into 4-hour sets the day
# Calculate usage pattern percentages
def calc_pattern_prcntge(pattern_set, usage_set):
    total = sum(usage_set)
    for i in range(6):
        pattern_set[i] = (usage_set[i] / total) * 100


# Calculating setting up goals for the 6 sets according to the user's usage pattern
def goals_set(goal, goal_set, pattern_set):
    for i in range(6):
        goal_set[i] = (goal * pattern_set[i]) / 100


# This function(method) checks and find the deviation of the real values with the goal allocated
def check_usage_goal_stat(set_index, goal_set, day_usage_set):
    deviation = goal_set[set_index] - day_usage_set[set_index]
    return deviation


# This function(method) finds usage patterns of the device
def device_u_pattern(device):
    calc_pattern_prcntge(device.usage_device_pattern_set, device.usage_device_set)


# This function(method) calculates and sets up the goal for each device's each set
def device_goals(device):
    goals_set(device.goal_device, device.goal_device_set, device.usage_device_pattern_set)


# This function(method) checks and find the deviation of the real values with the goal allocated for a device
def check_dev_use(set_index, device):
    return check_usage_goal_stat(set_index, device.goal_device_set, device.day_device_usage_set)


# This function(method) calculates and sets up the goal for each device
def cal_device_goal(goal, device, sum_usage):
    device.goal_device = sum(device.usage_device_set) / sum_usage * goal


# This function calculate deviations for all the 4-hours sets in a day by using above methods
def goal_set_stat_desc():
    set_stat = []
    for i in range(6):
        dev = check_usage_goal_stat(i, goalSet, dayUsageSet)
        set_stat.append(dev)
    return set_stat


# This function calculate deviations for "each device" for all the 4-hours sets in a day by using above methods
def device_goal_stat():
    device_goal_stat_desc = {}
    for d in devices:
        device_goal_set_stat = []
        for i in range(6):
            dev = check_dev_use(i, d)
            device_goal_set_stat.append(dev)
        print(d.id,'stat',device_goal_set_stat)
        device_goal_stat_desc[d.id] = device_goal_set_stat
    return device_goal_stat_desc


# Calculates and stores the amount of the usage consumes by a device from the total usage in each 4-hour set of a day
# This will help to find the pattern of the devices' usages
def device_set_usages():
    for d in devices:
        d.device_set_usage = [(d.usage_device_set[0] / usageSet[0]), (d.usage_device_set[1] / usageSet[1]),
                              (d.usage_device_set[2] / usageSet[2]),
                              (d.usage_device_set[3] / usageSet[3]), (d.usage_device_set[4] / usageSet[4]),
                              (d.usage_device_set[5] / usageSet[5])]


# This function updates device usage data to the firebase
def update_dev_data(d, offset):
    path_d = str('usage/') + str(d.id) + str('/hours/')
    indx = 0
    # saving them in 4-hour set based usages
    for i in range(3):
        result = 0
        for y in range(4):
            dta = firebase.get(path_d + str(indx), None)
            result += float(dta)
            indx += 1
        d.day_device_usage_set[i + offset] = float(result)
        d.usage_device_set[i + offset] += d.day_device_usage_set[i + offset]
    print(d.id,"usage",d.usage_device_set)
    print(d.id,"usageDay",d.day_device_usage_set)


# This finds new devices added and add them to the Intelligent Prediction System
# If the device is already added one this updates its new data to this system
def add_devices(offset):
    path = str('users/1C3rQ2P3mgQzfC06Bqd2JRKaBOK2/device')
    dta = firebase.get(path, None)
    dId = dta
    for dev_id in dId:
        found = False
        for d in devices:
            if d.id == dev_id:
                found = True
                update_dev_data(d, offset)
                break
        if not found:
            dev = Device(dev_id)
            devices.append(dev)
            update_dev_data(devices[len(devices) - 1], offset)
    device_set_usages()


# This function executes statistic generating functions
def stat_cal():
    calc_pattern_prcntge(usagePatternSet, usageSet)
    goals_set(curGoal, goalSet, usagePatternSet)
    sum_usage = sum(usageSet)
    for d in devices:
        cal_device_goal(curGoal, d, sum_usage)
        device_u_pattern(d)
        device_goals(d)


# updating calculated statistics by the functions mentioned above to the firebase
def add_firebase_set_stat():
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    set_stat = goal_set_stat_desc()
    #print(set_stat)
    pathFB = str('prediction/dayStats/') + str(date)
    for i in range(6):
        result = firebase.patch(pathFB, {i: set_stat[i]})


# updating calculated device statistics by the functions mentioned above to the firebase
def add_firebase_device_stat():
    date = datetime.datetime.today().strftime('%Y-%m-%d')  # getting the current date
    devices_stats = device_goal_stat()
    for d in devices:
        device_stat = devices_stats[d.id]
        for i in range(6):
            path = str('prediction/') + str(d.id) + str('/') + str(date)
            result = firebase.patch(path, {i: device_stat[i]})


# Calculation of the prediciton of the monthly usage
def cal_prediction():
    pathFB = str('prediction/dayStats')
    result = firebase.get(pathFB, None)
    offsetUse = 0
    days = 0
    for r in result:
        days += 1
        for i in range(6):
            offsetUse += result.get(r)[i]
    prediction = ((curGoal * days) + offsetUse) + (30 - days) * curGoal  # Equation for the prediction
    firebase.put('prediction/', 'monthlyPrediction', prediction)  # Updating it to the firebase


# Execution statistics generating and prediction calculating functions
def run_processes():
    global dayUsageSet
    global usageSet
    global curGoal
    index = 0
    offset = 0
    global day
    if day == 0.5:
        offset = 3

    path = str('users/1C3rQ2P3mgQzfC06Bqd2JRKaBOK2/home/goalDay')
    goal = firebase.get(path, None)
    curGoal = float(goal)
    print("Retrieving new data from firebase ...")
    for i in range(3):
        result = 0
        for y in range(4):
            path = str('users/1C3rQ2P3mgQzfC06Bqd2JRKaBOK2/home/allDeviceUsage/') + str(index)
            d = firebase.get(path, None)
            result += float(d)
            index += 1
        dayUsageSet[i + offset] = result
        usageSet[i + offset] += dayUsageSet[i + offset]
    print("Retrieving new data from firebase for Devices...")
    add_devices(offset)

    if day == 0.5:
        stat_cal()
        print("Saving new data to firebase ...")
        add_firebase_set_stat()
        add_firebase_device_stat()
        cal_prediction()
        day = 0
    else:
        day = 0.5


# Class for the device object creation
class Device:

    def __init__(self, id):
        self.id = id
        # Variables needed fo the device
        self.goal_device = 0
        self.devices = [0, 0, 0, 0, 0, 0]
        self.day_device_usage_set = [0, 0, 0, 0, 0, 0]
        self.usage_device_set = [0, 0, 0, 0, 0, 0]
        self.goal_device_set = [0, 0, 0, 0, 0, 0]
        self.usage_device_pattern_set = [0, 0, 0, 0, 0, 0]
        self.device_set_usage = [0, 0, 0, 0, 0, 0]


######## Main Program #########

# run_processes() function will only run for once in 12-hour period
# every 24-hour period this system will predict and calculate stats
run_processes()
run_processes()
