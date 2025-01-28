import speech_recognition as sr
import pyttsx3
import re
import datetime
from dateutil import parser
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Authenticate Google Calendar API
def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json',
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

# Speak text function
def speak(text):
    print(f"Speaking: {text}") 
    engine.say(text)
    engine.runAndWait()

# Listen for voice input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio)
            print(f"You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            return None
        except sr.RequestError:
            speak("Network error. Please check your connection.")
            return None

# Adding appointment to Google Calendar
def add_appointment(service, date_time):
    date_time_with_tz = date_time + "+05:30"

    event = {
        'summary': 'Car Showroom Appointment',
        'start': {'dateTime': date_time_with_tz, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': (datetime.datetime.fromisoformat(date_time) + datetime.timedelta(hours=1)).isoformat() + "+05:30", 'timeZone': 'Asia/Kolkata'},
    }

    events_result = service.events().list(
        calendarId='primary',
        timeMin=date_time_with_tz,
        maxResults=1,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    existing_events = events_result.get('items', [])

    if existing_events:
        return "This time slot is already booked. Please choose another date and time."

    service.events().insert(calendarId='primary', body=event).execute()
    return f"Your appointment has been scheduled for {datetime.datetime.fromisoformat(date_time).strftime('%A, %d %B %Y at %I:%M %p')}."

# Get appointment details from the user
def get_appointment_details(service):
    speak("Then please say the date and time for your appointment, for example, '30th of January at 11 AM'.")
    query = listen()
    if query:
        try:
            date_time = parser.parse(query, fuzzy=True).isoformat()
            response = add_appointment(service, date_time)
            speak(response)
        except (ValueError, TypeError):
            speak("I couldn't understand the date and time format. Please try again.")
    else:
        speak("Please provide the date and time again.")

# Respond to user queries
def respond(query):
    car_models = ["Sedan", "SUV", "Hatchback", "Convertible", "Coupe"]

    if 'car' in query or 'model' in query:
        car_list = ", ".join(car_models)
        return f"We have the following car models available: {car_list}. Please choose one by saying the model name."
    elif any(model.lower() in query for model in car_models):
        return f"You've selected the {query.title()}. Would you like to know about the color options, features, price, availability, or schedule a test drive?"
    elif 'price' in query or 'cost' in query:
        return "Prices range from $20,000 to $50,000 depending on the model and features."
    elif 'feature' in query or 'specs' in query:
        return "Our cars come with features like touch-screen infotainment, leather seats, and backup cameras. Would you like to schedule a test drive?"
    elif 'color' in query:
        return "Available colors are red, blue, black, white, and silver. Do you have a preference?"
    elif 'availability' in query or 'stock' in query:
        return "We have a great selection of models in stock. Which one are you interested in?"
    elif 'test drive' in query or 'appointment' in query or 'book' in query:
        return "Would you like to schedule an appointment for a test drive"
    elif 'exit' in query or 'bye' in query:
        return "Goodbye! Thank you for visiting our showroom."
    else:
        return "Sorry, I didn't understand that. Could you please ask something else?"

# Main function
def main():
    speak("Hello! Welcome to Kapil's car showroom. How can I assist you today? The car models are Sedan, SUV, Hatchback, Convertible, Coupe")
    service = authenticate_google_calendar()
    while True:
        query = listen()
        if query:
            response = respond(query)
            speak(response)
            if 'appointment' in query or 'test drive' in query or 'book' in query:
                get_appointment_details(service)
            if 'exit' in query or 'bye' in query:
                break
        else:
            speak("Please repeat your query.")

if __name__ == "__main__":
    main()
