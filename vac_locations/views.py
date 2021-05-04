from django.shortcuts import render
import requests
import datetime
import json
from django.core.mail import send_mail
from django.conf import settings

COWIN_BASE_URL = "https://cdn-api.co-vin.in/api"

# Create your views here.
def searchByDistrict(request):
    response = requests.get(COWIN_BASE_URL+"/v2/admin/location/states")
    if response.status_code == 200:
        data = response.json()
        # print(data)
        today=datetime.date.today()
        data['today'] = today.strftime("%Y-%m-%d")
        return render(request, "vac_locations_searchByDistrict.html", data)
    else:
        # TODO: error handling
        return error()

def search(request):
    return render(request,"vac_locations_search.html")

def results():
    #get data from API
    return render(request,"results.html",data)

def searchByDistrictResults(request):
    if "district_id" in request.GET and "date" in request.GET: 
        district_id  = request.GET['district_id']
        yyyy,mm,dd=request.GET['date'].split('-')
        params = {'district_id': district_id, 'date': '-'.join([dd,mm,yyyy])}
        dataFilter=dict()
        if "Above18Only" in request.GET:
            dataFilter['Above18Only']= request.GET['Above18Only']
        if "getFor7Days" in request.GET and request.GET['getFor7Days']=="yes":
            inp_date = datetime.datetime(int(yyyy), int(mm), int(dd))
            datesofNext7days = [(inp_date + datetime.timedelta(days=count)).strftime("%d-%m-%Y") for count in range(0,7)]
            response = requests.get(COWIN_BASE_URL+"/v2/appointment/sessions/public/calendarByDistrict",params)
            data=response.json()
            data['datesofNext7days']=datesofNext7days
            for key, value in dataFilter.items():
                data[key] = value
            print(data)
            return render(request,"vac_locations_searchResultsFor7days.html",data)
        else:
            response = requests.get(COWIN_BASE_URL+"/v2/appointment/sessions/public/findByDistrict",params)
            data=response.json()
            for key, value in dataFilter.items():
                data[key] = value
            print(data)
            return render(request,"vac_locations_searchResults.html",data)
    else:
        # TODO: error handling
        return render(request,"vac_locations_searchResults.html")

def searchByPinCodeResults(request):
    if "pincode" in request.GET and "date" in request.GET:
        pincode = request.GET['pincode']
        yyyy,mm,dd=request.GET['date'].split('-')
        dataFilter=dict()
        params = {'pincode': pincode, 'date': '-'.join([dd,mm,yyyy])}
        if "Above18Only" in request.GET:
            dataFilter['Above18Only']= request.GET['Above18Only']
        if "getFor7Days" in request.GET and request.GET['getFor7Days']=="yes":
            inp_date = datetime.datetime(int(yyyy), int(mm), int(dd))
            datesofNext7days = [(inp_date + datetime.timedelta(days=count)).strftime("%d-%m-%Y") for count in range(0,7)]
            response = requests.get(COWIN_BASE_URL+"/v2/appointment/sessions/public/calendarByPin",params)
            data=response.json()
            data['datesofNext7days']=datesofNext7days
            for key, value in dataFilter.items():
                data[key] = value
            print(data)
            process_data(data,data["Above18Only"]=="yes")
            return render(request,"vac_locations_searchResultsFor7days.html",data)
        else:
            response = requests.get(COWIN_BASE_URL+"/v2/appointment/sessions/public/findByPin",params=params)
            data=response.json()
            for key, value in dataFilter.items():
                data[key] = value
            print(data)
            return render(request,"vac_locations_searchResults.html",data)
    else:
        # TODO error hanlding
        return render(request,"vac_locations_searchResults.html")
 
# def notify():
#     # send email if found

# def book_appointment():
#     # get required details like date, loc
#     # call cowin API

def error():
    data = {'error_msg': "Having issues connecting to API"}
    return render(request,"error.html",data)

def load_districts(request):
    data=dict()
    if "state_id" in request.GET:
        state_id = request.GET['state_id']
        response = requests.get(COWIN_BASE_URL+"/v2/admin/location/districts/"+state_id)
        if response.status_code == 200:
            data = response.json()
        else:
            # TODO: error handling
            return render(request,"error.html")
    return render(request, "vac_locations_districts.html", context=data)

def notifyByPin(request):
    return render(request, "vac_locations_notifyByPin.html")

def notifyByDistrict(request):
    response = requests.get(COWIN_BASE_URL+"/v2/admin/location/states")
    data=response.json()
    return render(request, "vac_locations_notifyByDistrict.html",data)

def notifyByPinResults(request):
    inp_date = datetime.date.today()
    pincode = request.GET['pincode']
    params = {'pincode': pincode, 'date': inp_date.strftime("%d-%m-%Y")}
    response = requests.get(COWIN_BASE_URL+"/v2/appointment/sessions/public/calendarByPin",params)
    data=response.json()
    count = process_data(data,request.GET["Above18Only"]=="yes")
    print(count)
    context={'count': count}
    if count>0:
        send_mail(
        'Subject here',
        'Here is the message.',
        settings.EMAIL_HOST_USER,
        ['bommvams72@gmail.com'],
        fail_silently=False,
        )
    return render(request, "vac_locations_notifyResponse.html",context)

def notifyByDistrictResults(request):
    inp_date = datetime.date.today()
    district_id = request.GET['district_id']
    params = {'district_id': district_id, 'date': inp_date.strftime("%d-%m-%Y")}
    response = requests.get(COWIN_BASE_URL+"/v2/appointment/sessions/public/calendarByDistrict",params)
    data=response.json()
    count = process_data(data,request.GET["Above18Only"]=="yes")
    print(count)
    context={'count': count}
    if count>0:
        send_mail(
        'Subject here',
        'Here is the message.',
        settings.EMAIL_HOST_USER,
        ['bommvams72@gmail.com'],
        fail_silently=False,
        )
    return render(request, "vac_locations_notifyResponse.html",context)

def process_data(data,above18Only=False):
    # data=json.loads(response)
    count=0
    for center in data['centers']:
        for session in center['sessions']:
            # print(session['min_age_limit'])
            if(above18Only and session['min_age_limit']<=18):
                count+=session['available_capacity']
            elif not above18Only:
                count+=session['available_capacity']
    return count

def searchByPinCode(request):
    today=datetime.date.today()
    data={'today': today.strftime("%Y-%m-%d")}
    return render(request, "vac_locations_searchByPinCode.html", data)
