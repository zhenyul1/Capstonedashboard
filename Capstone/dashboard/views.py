from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta
import requests
import ast
from collections import defaultdict, namedtuple, OrderedDict


def home(request):
    context = {}
    # get machine list and parse the input to dics
    response = requests.get("http://18.188.124.37/getMachines/")
    str = response.content.decode('utf-8')
    newStr = str.replace("}", "}!").replace("u'", "'").replace("L,", ",").replace("L}", "}")[:-1]
    machineArray = newStr.split("!")
    machineStruct = namedtuple('machineStruct', 'last_service id name type_id')
    machineObjects = []
    for machine in machineArray:
        machineDic = ast.literal_eval(machine)

        tmp = machineStruct(last_service=machineDic['last_service'], id=int(machineDic['id']), name=machineDic['name'],
                            type_id=int(machineDic['type_id']))
        machineObjects.append(tmp)

    context['machines'] = machineObjects
    return render(request, 'table.html', context)


def charts(request, machine_id):
    if request.method == 'GET':
        context = {}
        context['machine_id'] = machine_id
        # we don't use the time for presente
        endTime = datetime.now() - timedelta(days=0)
        startTime = endTime - timedelta(days=14)
        sentEndTime = endTime.strftime("%m-%d-%Y %H:%M:%S").replace(" ", "%20")
        sentStartTime = startTime.strftime("%m-%d-%Y %H:%M:%S").replace(" ", "%20")
        # fix the time due to limit data
        context['startTime'] = datetime.strptime("05-06-2018 00:00:01", "%m-%d-%Y %H:%M:%S")  # startTime
        context['endTime'] = datetime.strptime("05-06-2018 23:59:59", "%m-%d-%Y %H:%M:%S")
        context['startTimeStamp'] = "05-06-2018 00:00:01"  # sentStartTime
        context['endTimeStamp'] = "05-06-2018 23:59:59"
        return render(request, 'dashboard.html', context)

    # deal with the datetime picker time range
    if request.method == 'POST':
        context = {}
        context['machine_id'] = machine_id
        startTime = request.POST.get('startTime')
        endTime = request.POST.get('endTime')
        # handle wrong input graceful
        if endTime == None:
            endTime = datetime.now()
        if startTime == None or endTime < startTime:
            startTime = datetime.now() - timedelta(days=7)
            endTime = datetime.now()
        sentEndTime = datetime.strftime(datetime.strptime(endTime, "%Y-%m-%d %H:%M"), "%m-%d-%Y %H:%M:%S").replace(" ",
                                                                                                                   "%20")
        sentStartTime = datetime.strftime(datetime.strptime(startTime, "%Y-%m-%d %H:%M"), "%m-%d-%Y %H:%M:%S").replace(
            " ", "%20")
        context['startTime'] = startTime
        context['endTime'] = endTime
        context['startTimeStamp'] = sentStartTime
        context['endTimeStamp'] = sentEndTime
        return render(request, 'dashboard.html', context)


# respond json file
def get_data(request, strstartTime, strendTime, machineId):
    context = {}
    sentStartTime = strstartTime.replace(" ", "%20")
    sentEndTime = strendTime.replace(" ", "%20")
    url = "http://18.188.124.37/getInfoTime/?machineid=" + machineId + "&start=" + sentStartTime + "&end=" + sentEndTime
    print(url)
    response = requests.get(url)
    str = response.content.decode('utf-8')
    newStr = str.replace("u'", "'").replace("Decimal(", "").replace(")", "")
    machineDic = ast.literal_eval(newStr)
    # gauge charts
    context['staticsN'] = [['Label', 'Value'], ['Minimum', float(machineDic['noise_attr']['min'])],
                           ['Maximum', float(machineDic['noise_attr']['max'])],
                           ['Average', float(machineDic['noise_attr']['avg'])]]
    context['staticsT'] = [['Label', 'Value'], ['Minimum', float(machineDic['temp_attr']['min'])],
                           ['Maximum', float(machineDic['temp_attr']['max'])],
                           ['Average', float(machineDic['temp_attr']['avg'])]]
    # what's the configuration ???
    context['dangerN'] = float(machineDic['Ideal_noise']) * 1.15
    context['dangerT'] = float(machineDic['Ideal_temp']) * 1.15
    context['warningN'] = float(machineDic['Ideal_noise']) * 0.85
    context['warningT'] = float(machineDic['Ideal_temp']) * 0.85
    warningT = context['warningT']
    warningN = context['warningN']
    dangerT = context['dangerT']
    dangerN = context['dangerN']
    # time series
    context['timeT'] = [[e1, float(e2), dangerT, warningT] for e1, e2 in
                        zip(machineDic['temp_data']['Date'], machineDic['temp_data']['Temp'])]
    context['timeN'] = [[e1, float(e2), dangerN, warningN] for e1, e2 in
                        zip(machineDic['noise_data']['Date'], machineDic['noise_data']['Noise'])]
    # comparison
    # x.split(" ")[0] for date
    # here we use the miniute as unit, cut the last three chars
    dictAvgT = defaultdict(list)
    for key, value in zip(list(map(lambda x: x[:-3], machineDic['temp_data']['Date'])),
                          machineDic['temp_data']['Temp']):
        dictAvgT[key].append(float(value))
    dictDisT = dictAvgT.copy()
    for key in dictAvgT.keys():
        dictAvgT[key] = sum(dictAvgT[key]) / len(dictAvgT[key])
    dictAvgN = defaultdict(list)
    # x.split(" ")[0] for date
    # here we use the miniute as unit , cut the last three chars
    for key, value in zip(list(map(lambda x: x[:-3], machineDic['noise_data']['Date'])),
                          machineDic['noise_data']['Noise']):
        dictAvgN[key].append(float(value))
    dictDisN = dictAvgN.copy()
    for key in dictAvgN.keys():
        dictAvgN[key] = sum(dictAvgN[key]) / len(dictAvgN[key])
    dictAvgT = OrderedDict(sorted(dictAvgT.items()))
    dictAvgN = OrderedDict(sorted(dictAvgN.items()))
    context['comparison'] = [[k1, dictAvgT[k1], dictAvgN[k2]] for k1, k2 in zip(dictAvgT.keys(), dictAvgN.keys())]
    context['comparison'].insert(0, ['Dates', 'Avg temperature', 'Avg vibration'])
    # stacked column
    # normal, danger, warning
    for key in dictDisT.keys():
        dictDisT[key] = [count_range_in_list(dictDisT[key], -100, warningT),
                         count_range_in_list(dictDisT[key], warningT, dangerT),
                         count_range_in_list(dictDisT[key], dangerT, 1000)]
    for key in dictDisN.keys():
        dictDisN[key] = [count_range_in_list(dictDisN[key], -100, warningN),
                         count_range_in_list(dictDisN[key], warningN, dangerN),
                         count_range_in_list(dictDisN[key], dangerN, 1000)]
    dictDisT = OrderedDict(sorted(dictDisT.items()))
    dictDisN = OrderedDict(sorted(dictDisN.items()))
    context['stackedColT'] = [[k1, dictDisT[k1][1], dictDisT[k1][0] + dictDisT[k1][2], ''] for k1 in dictDisT.keys()]
    context['stackedColN'] = [[k1, dictDisN[k1][1], dictDisN[k1][0] + dictDisN[k1][2], ''] for k1 in dictDisN.keys()]

    return JsonResponse(context)


def count_range_in_list(li, min, max):
    ctr = 0
    for x in li:
        if min < x <= max:
            ctr += 1
    return ctr
