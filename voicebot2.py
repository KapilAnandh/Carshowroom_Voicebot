import speech_recognition as sr
import pyttsx3
import re

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to speak text while displaying it
def speak(text):
    print(f"Assistant: {text}")  # Display the text in the console
    engine.say(text)
    engine.runAndWait()

# Function to recognize voice input
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
            return query
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Could not request results; check your network connection.")
            speak("Could not request results; please check your network connection.")
            return None

# Function to show suggestions and respond based on showroom queries
def respond(query):
    query = query.lower()

    # List of available car models
    car_models = ["Sedan", "SUV", "Hatchback", "Convertible", "Coupe"]

    # When the user asks about models, provide a list of car models
    if 'car' in query or 'model' in query:
        car_list = ", ".join(car_models)
        return f"We have the following car models available: {car_list}. Please choose one by saying the model name."

    elif any(model.lower() in query for model in car_models):
        # Follow-up question after the user selects a model
        return f"You've selected the {query.title()}. Would you like to know about the color options, features, price, availability, or schedule a test drive?"

    elif 'price' in query or 'cost' in query:
        return "The price depends on the model and features you choose. Prices range from $20,000 to $50,000. Which model would you like to inquire about?"

    elif 'feature' in query or 'specs' in query:
        return "Our cars come with modern features like touch-screen infotainment, leather seats, backup cameras, and more. Book an appointment for test drive?"

    elif 'color' in query:
        return "Our cars come in a variety of colors such as red, blue, black, white, and silver. Do you have a preferred color?"

    elif 'availability' in query or 'stock' in query:
        return "We have a great selection of models in stock. Please tell me the model you are interested in, and I'll check availability for you."

    elif 'test drive' in query:
        return "We offer test drives for all our cars. Would you like to schedule a test drive for a specific model?"

    elif 'appointment' in query or 'book' in query:
        return "Would you like to book an appointment for a test drive or a showroom visit? Please say 'yes' to proceed."

    elif 'yes' in query:
        return "Great! Please tell me the date and time for your appointment."

    elif 'no' in query:
        return "Okay! Let me know if you need anything else."

    elif 'exit' in query or 'bye' in query:
        return "Goodbye! Thank you for visiting our showroom. Have a great day!"

    else:
        return "Sorry, I didn't understand that. Could you please ask about something else?"

# Function to get the date and time from the user
def get_appointment_details():
    speak("Please say the date and time for your appointment. For example, you can say 'January 25th at 10 AM'.")
    
    query = listen()
    
    if query:
        # A simple regex to capture dates and times (can be enhanced further for more complex patterns)
        date_time_pattern = r"(\w+\s\d{1,2}[a-z]{0,2}\s(?:at\s)?(?:\d{1,2}\s?[APap][Mm]))"
        match = re.search(date_time_pattern, query)
        
        if match:
            appointment_details = match.group(0)
            speak(f"Your appointment is scheduled for {appointment_details}.")
            return f"Appointment scheduled for {appointment_details}."
        else:
            speak("Sorry, I couldn't understand the date and time. Please try again.")
            return None
    else:
        speak("Please provide the date and time again.")
        return None

# Main loop to keep the conversation going
def main():
    speak("Hello! Welcome to our car showroom. How can I assist you today? We have Sedan, SUV, Hatchback, Convertible, and Coupe models.")
    
    while True:
        query = listen()
        if query:
            response = respond(query)
            speak(response)
            
            # If the user selects a car model, ask follow-up questions
            if any(model.lower() in query for model in ["sedan", "suv", "hatchback", "convertible", "coupe"]):
                speak("Would you like to know about the color options, features, price, availability, or schedule a test drive?")
            
            # If the user says goodbye
            if 'exit' in query.lower() or 'bye' in query.lower():
                break
        else:
            speak("Please say something again.")

if __name__ == "__main__":
    main()
