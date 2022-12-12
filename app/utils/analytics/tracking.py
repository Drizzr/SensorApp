from app import db
from app.models import DayAnalytics, Device, DeviceDayCalls, UserDayCalls
from flask import request, abort, _request_ctx_stack, current_app
from flask_login import current_user
from datetime import datetime
import requests
import json
from app.task import launch_task


def tracking(view=True):        

    time = datetime.utcnow().isoformat()
    date = time[:10]
    client_ip = request.environ['REMOTE_ADDR']
    ctx = _request_ctx_stack.top
    query = DayAnalytics.query.filter_by(date=date).first()#

    ip_query = Device.query.filter_by(ip=client_ip).first()

    if not ip_query:
        ip_query = Device(
                            ip = client_ip, 
                            calls_all_time = 1, 
                            last_call = time,
                            flagged = False,
                            )
        db.session.add(ip_query)

    else:
        ip_query.last_call = time
        ip_query.calls_all_time += 1

        if  ip_query.flagged:
            abort(403)
    
    if current_user.is_authenticated:
            ip_query.users.append(current_user)
    
    if query:
        if view:
            query.view_calls += 1
        else:
            query.api_calls += 1
        
        device_day_calls = DeviceDayCalls.query.filter_by(date=query.date, device_ip=ip_query.id).first()
        if not device_day_calls:
            device_day_calls = DeviceDayCalls(date=query.date, device_ip=ip_query.id, view_calls = 0, api_calls= 0)
            db.session.add(device_day_calls)
        if view:
            device_day_calls.view_calls += 1
        else:
            device_day_calls.api_calls += 1


        if current_user.is_authenticated:
            query.authorized_view_calls += 1
            user_day_calls = UserDayCalls.query.filter_by(date=query.date, user_id=current_user.id).first()
            if not user_day_calls:
                query.unique_users += 1
                user_day_calls = UserDayCalls(date = query.date, user_id = current_user.id, view_calls = 0, api_calls= 0)
                db.session.add(user_day_calls)
            if view:
                user_day_calls.view_calls += 1
            else:
                user_day_calls.api_calls += 1
    else:
        query = DayAnalytics(
                                date=date,
                                authorized_view_calls=1 if current_user.is_authenticated and view else 0,
                                view_calls=1 if view else 0,
                                new_access_token=0,
                                new_refresh_token=0,
                                unique_users=1,
                                new_registered_users=0,
                                authorized_api_calls=0,
                                api_calls=1 if not view else 0
                                )

        new_device_day_calls = DeviceDayCalls(
                            date=query.date,
                            device_ip=ip_query.id,
                            view_calls=1 if view else 0,
                            api_calls=1 if not view else 0,
                            )
        
        db.session.add(query)
        db.session.add(new_device_day_calls)
        
    
        if current_user.is_authenticated:
            user_day_calls = UserDayCalls(
                            date=query.date,
                            user_id=current_user.id,
                            view_calls=1 if view else 0,
                            api_calls=1 if not view else 0,
                            )
            db.session.add(user_day_calls)

    db.session.commit()
    
    launch_task(current_app, "get_ip_geo_loc", "geo locate client", client_ip)
    # add api geo loc here


def trackUserApiCalls(current_user, new_access_token=False, new_refresh_token=False):
    # for api analytics, tracks new tokens that have been created
    # tracks users daily api calls

    today = datetime.utcnow().isoformat()[:10]

    query = DayAnalytics.query.filter_by(date=today).first()
    query.authorized_api_calls += 1

    if new_refresh_token:
        query.new_refresh_token += 1
    if new_access_token:
        query.new_access_token += 1

    user_day_calls = UserDayCalls.query.filter_by(date=query.date, user_id=current_user.id).first()

    if not user_day_calls:
        user_day_calls = UserDayCalls(date=query.date, user_id=current_user.id, view_calls=0, api_calls=0)
        db.session.add(user_day_calls)

    user_day_calls.api_calls += 1