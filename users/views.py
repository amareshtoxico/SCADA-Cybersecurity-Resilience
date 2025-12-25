# Create your views here.
import pandas as pd
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserRegistrationModel, TokenCountModel
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from datetime import datetime, timedelta
from jose import JWTError, jwt
import numpy as np
import os
import matplotlib.pyplot as plt
import json
import random

SECRET_KEY = "ce9941882f6e044f9809bcee90a2992b4d9d9c21235ab7c537ad56517050f26b"
ALGORITHM = "HS256"


def create_access_token(data: dict):
    to_encode = data.copy()
    # expire time of the token
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # return the generated token
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HttpResponse(
            status_code=HttpResponse(status=204),
            detail="Could not validate credentials",
        )



def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            user = form.save()  # Save the user instance
            TokenCountModel.objects.create(loginid=user.loginid, count=0)

            messages.success(request, f'You have been successfully registered. Your key is: {user.key}')

            form = UserRegistrationForm()  # Reset the form after successful submission
            return render(request, 'UserRegistrations.html', {'form': form, 'key': user.key})

        else:
            messages.error(request, 'Email or Mobile Already Exists')
            print("Invalid form")
    
    else:
        form = UserRegistrationForm()
    
    return render(request, 'UserRegistrations.html', {'form': form})




def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                data = {'loginid': loginid}
                token_jwt = create_access_token(data)
                request.session['token'] = token_jwt
                print("User id At", check.id, status)
                # return render(request, 'users/UserHomePage.html', {})
                return redirect('user_key')
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})

def key_login(request):
    if request.method == 'POST':
        g_key = request.POST.get('key')

        try:
            check = UserRegistrationModel.objects.get(key=g_key)
            messages.success(request, f"Login successful for {check.loginid}")
            # return redirect('UserLoginCheck')  
            return render(request, 'users/UserHomePage.html', {})
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, "Invalid Key! Please try again.")
    
    return render(request, 'key_login.html')

def UserHome(request):
    return render(request, 'users/UserHomePage.html', {})


def sendScadaMessage(request):
    if request.method == "POST":
        hostName = request.POST.get('hostName')
        ip = request.POST.get('ip')
        pressureValue = request.POST.get('pressureValue')
        temperature = request.POST.get('temperature')
        flowRate = request.POST.get('flowRate')
        switchRate = request.POST.get('switchRate')
        valveStatus = request.POST.get('valveStatus')
        pumpStatus = request.POST.get('pumpStatus')
        flowIndicator = request.POST.get('flowIndicateor')
        msg = {"HostName": hostName,
               "IP": ip,
               "PressureValue": pressureValue,
               "Temperature": temperature,
               "FlowRate": flowRate,
               "SwitchRate": switchRate,
               "ValveStatus": valveStatus,
               "PumpStatus": pumpStatus,
               "FlowIndicator": flowIndicator,
               "status": random.choice(['Normal', "Idle"])
               }
        machineOperator = json.dumps(msg)
        import socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 54321))  # Connect to the attacker instead of server
        client_socket.sendall(machineOperator.encode())

        return render(request, 'users/ScadaRes.html', {"data": msg})
    else:
        import socket
        hostname = socket.gethostname()
        # IPAddr = socket.gethostbyname(hostname)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IPAddr = s.getsockname()[0]
        s.close()

        print("Your Computer Name is:" + hostname)
        print("Your Computer IP Address is:" + IPAddr)
        return render(request, "users/sendScadaForm.html", {'hostName': hostname, 'ip': IPAddr})


# Function to convert cursor to a list of dictionaries
def cursor_to_dict(cursor):
    # Get the column names from the cursor
    columns = [description[0] for description in cursor.description]

    # Fetch all rows and convert each row to a dictionary
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def MachinesLogs(request):
    import sqlite3
    conn = sqlite3.connect('attacker.db')
    cursor = conn.cursor()
    data = cursor.execute('''SELECT * FROM ScadaNetwork''')
    result = cursor_to_dict(cursor)
    print(result, type(result))
    df = pd.DataFrame(result)
    return render(request, "users/scadalogs.html", {'data': df.to_html(index=False)})


def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        
        try:
            user = UserRegistrationModel.objects.get(loginid=username)
            return redirect('reset_password', username=username)  # Redirect to password reset page
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'User does not exist.')
    
    return render(request, 'Forgot_password.html')  # Render forgot password page

def reset_password(request, username):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            try:
                user = UserRegistrationModel.objects.get(loginid=username)
                user.password = new_password  # Update the password
                user.save()
                messages.success(request, 'Password updated successfully! Please login.')
                return redirect('UserLogin')  # Redirect back to login page
            except UserRegistrationModel.DoesNotExist:
                messages.error(request, 'User does not exist.')
        else:
            messages.error(request, 'Passwords do not match.')
    
    return render(request, 'reset_password.html', {'username': username})