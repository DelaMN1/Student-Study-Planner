from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from datetime import timedelta
from icalendar import Calendar, Event
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from flask import session as flask_session
import os
from models import db, User, Task
from utils import login_required
from config import Config

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar')
@login_required
def calendar():
    user = db.session.get(User, session['user_id'])
    return render_template('calendar.html', user=user)

@calendar_bp.route('/calendar/events')
@login_required
def calendar_events():
    user = db.session.get(User, session['user_id'])
    tasks = Task.query.filter_by(user_id=user.id).all()
    events = []
    for task in tasks:
        if task.due_date:
            events.append({
                'id': task.id,
                'title': task.title,
                'start': task.due_date.strftime('%Y-%m-%d'),
                'url': url_for('main.view_task', task_id=task.id),
                'color': '#dc3545' if task.priority == 'High' else '#ffc107' if task.priority == 'Medium' else '#28a745',
            })
    return jsonify(events)

@calendar_bp.route('/calendar/export')
@login_required
def calendar_export():
    user = db.session.get(User, session['user_id'])
    tasks = Task.query.filter_by(user_id=user.id).all()
    cal = Calendar()
    cal.add('prodid', '-//Student Study Planner//')
    cal.add('version', '2.0')
    for task in tasks:
        if task.due_date:
            event = Event()
            event.add('summary', task.title)
            event.add('dtstart', task.due_date.date())
            event.add('dtend', task.due_date.date())
            event.add('description', task.description or '')
            event.add('priority', {'High': 1, 'Medium': 5, 'Low': 9}.get(task.priority, 5))
            cal.add_component(event)
    ics_bytes = cal.to_ical()
    response = make_response(ics_bytes)
    response.headers['Content-Disposition'] = 'attachment; filename=tasks.ics'
    response.headers['Content-Type'] = 'text/calendar'
    return response

@calendar_bp.route('/google/auth')
@login_required
def google_auth():
    # Allow OAuth2 to work with HTTP for local development
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    # Check if credentials file exists
    if not os.path.exists(Config.GOOGLE_CLIENT_SECRETS_FILE):
        flash('Google OAuth credentials file not found. Please add credentials.json to the project root.', 'error')
        return redirect(url_for('calendar.calendar'))
    
    try:
        flow = Flow.from_client_secrets_file(
            Config.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=Config.GOOGLE_SCOPES,
            redirect_uri=url_for('calendar.google_callback', _external=True)
        )
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        flask_session['google_oauth_state'] = state
        return redirect(auth_url)
    except Exception as e:
        flash(f'Error setting up Google OAuth: {str(e)}', 'error')
        return redirect(url_for('calendar.calendar'))

@calendar_bp.route('/google/callback')
@login_required
def google_callback():
    # Allow OAuth2 to work with HTTP for local development
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    # Check for OAuth errors
    error = request.args.get('error')
    if error:
        if error == 'access_denied':
            flash('Google OAuth access was denied. Please try again and make sure to grant calendar permissions.', 'error')
        else:
            flash(f'Google OAuth error: {error}', 'error')
        return redirect(url_for('calendar.calendar'))
    
    # Check for authorization code
    code = request.args.get('code')
    if not code:
        flash('No authorization code received from Google.', 'error')
        return redirect(url_for('calendar.calendar'))
    
    try:
        state = flask_session.get('google_oauth_state')
        flow = Flow.from_client_secrets_file(
            Config.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=Config.GOOGLE_SCOPES,
            state=state,
            redirect_uri=url_for('calendar.google_callback', _external=True)
        )
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        flask_session['google_credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        flash('Google OAuth successful!', 'success')
        return redirect(url_for('calendar.google_sync'))
    except Exception as e:
        flash(f'Error during Google OAuth callback: {str(e)}', 'error')
        return redirect(url_for('calendar.calendar'))

@calendar_bp.route('/google/sync')
@login_required
def google_sync():
    creds_data = flask_session.get('google_credentials')
    if not creds_data:
        flash('Google authentication required. Please authenticate first.', 'error')
        return redirect(url_for('calendar.calendar'))
    
    try:
        creds = Credentials(
            creds_data['token'],
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data['scopes']
        )
        service = build('calendar', 'v3', credentials=creds)
        user = db.session.get(User, session['user_id'])
        tasks = Task.query.filter_by(user_id=user.id).all()
        
        synced_count = 0
        for task in tasks:
            if task.due_date:
                event = {
                    'summary': task.title,
                    'description': task.description or '',
                    'start': {'date': task.due_date.strftime('%Y-%m-%d')},
                    'end': {'date': task.due_date.strftime('%Y-%m-%d')},
                }
                service.events().insert(calendarId='primary', body=event).execute()
                synced_count += 1
        
        flash(f'Successfully synced {synced_count} tasks to your Google Calendar!', 'success')
    except Exception as e:
        flash(f'Error syncing with Google Calendar: {str(e)}', 'error')
    
    return redirect(url_for('calendar.calendar')) 