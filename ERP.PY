
import os
import json
import webbrowser
import yfinance as yf
import sympy as sp
from datetime import datetime
import logging
import pyjokes
import nltk
from nltk.tokenize import sent_tokenize
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import pyttsx3
import speech_recognition as sr
from deep_translator import GoogleTranslator
import wikipediaapi

# Initialize logging
logging.basicConfig(filename='marcus.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

# File to log spoken responses and user inputs
log_file = "spoken_responses.txt"

# Load pre-trained model and tokenizer for text classification
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')

# Initialize speech recognition and synthesis
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Initialize the translator
translator = GoogleTranslator(source='auto', target='en')

# Initialize Wikipedia API with a custom user agent
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='MarkusAI/1.0  (https://skyaidevelopment01.wixsite.com/skyai-1); dipawasthi123@gmail.com)'
)

# File for storing business details in ERP
business_details_file = "business_details.json"
erp_system_used = False

def log_user_input(input_text):
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(f"User: {input_text}\n")

def speak(text):
    prefixed_text = f"Marcus AI says: {text}"
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(prefixed_text + "\n")
    tts_engine.say(prefixed_text)
    tts_engine.runAndWait()

def greet_user():
    hour = datetime.now().hour
    greetings = {
        range(0, 12): "Good morning!",
        range(12, 18): "Good afternoon!",
        range(18, 21): "Good evening!",
        range(21, 24): "Good night!"
    }
    greeting = next(g for h, g in greetings.items() if hour in h)
    speak(greeting)

def get_time_info(info_type):
    now = datetime.now()
    info_map = {
        'time': now.strftime("%H:%M:%S"),
        'day': now.strftime("%A"),
        'date': now.strftime("%d %B %Y"),
        'year': now.strftime("%Y")
    }
    return info_map.get(info_type, "Please try again.")

def translate_text(text, dest_language):
    try:
        return GoogleTranslator(source='auto', target=dest_language).translate(text)
    except Exception as e:
        return f"Error: {str(e)}"

def recognize_user_speech():
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError:
            print("Could not request results; check your network connection")
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
        return None

def handle_translation(command):
    if 'translate' in command:
        parts = command.split('into')
        if len(parts) == 2:
            text = parts[0].replace("translate", "").strip()
            dest_language = parts[1].strip().lower()
            return f"The translation is: {translate_text(text, dest_language)}"
        return "Please specify the text and target language."
    return "No translation command found."

def handle_command(command):
    commands = {
        'open youtube': lambda: webbrowser.open("https://www.youtube.com"),
        'open chrome': lambda: os.system("start chrome"),
        'exit': lambda: (speak("Exiting..."), True),
        'open site': lambda: speak(open_site()),
        'stock market update': lambda: speak(handle_stock_market_update()),
        'translate': lambda: speak(handle_translation(command)),
        'tell me a joke': lambda: speak(handle_joke()),
        'solve': lambda: speak(handle_math(command)),
        'summarize': lambda: speak(handle_summarization(command)),
        'analyze my dream': lambda: speak(handle_dream_analysis(command)),
        'search wikipedia for': lambda: speak(handle_wikipedia_query(command)),
        'start erp': lambda: start_erp_system(),
        'start fintech': lambda: start_fintech_system(),
        'start personal ai': lambda: start_personal_ai(),
        'start healthcare robot': lambda: start_healthcare_robot()
    }

    for keyword, handler in commands.items():
        if keyword in command:
            return handler()
    
    # Default action for general queries
    response = handle_general_query(command)
    speak(response)
    return False

def open_site():
    url = "https://skyaidevelopment01.wixsite.com/skyai-1"
    webbrowser.open(url)
    return f"Opening the site: {url}"

# ERP Functions
def save_business_details(details):
    with open(business_details_file, "w") as file:
        json.dump(details, file)

def load_business_details():
    if os.path.exists(business_details_file):
        with open(business_details_file, "r") as file:
            return json.load(file)
    return None

def get_business_details():
    details = load_business_details()
    if details:
        return details
    
    details = {}
    speak("Starting ERP system. This is your first time using the ERP system. Please provide the following details about your business.")
    details['name'] = input("What is the name of your business?\n")
    details['phone'] = input("What is the phone number of your business?\n")
    details['address'] = input("What is the address of your business?\n")
    details['type'] = input("What type of business is it (e.g., retail, manufacturing, etc.)?\n")
    details['employees'] = input("How many employees does your business have?\n")
    details['additional_info'] = input("Please describe any additional relevant information about your business.\n")
    
    save_business_details(details)
    return details

def handle_erp():
    business_details = get_business_details()
    speak("Thank you for providing the details. The ERP system is now started. What would you like to do next?")

def start_erp_system():
    global erp_system_used
    if not erp_system_used:
        handle_erp()
        erp_system_used = True
    else:
        speak("ERP system is already in use. What would you like to do next?")

    while True:
        erp_command = recognize_user_speech()
        if erp_command:
            if handle_erp_command(erp_command):
                break

def handle_erp_command(command):
    erp_commands = {
        'manage employee records': lambda: speak("Managing employee records."),
        'handle recruitment': lambda: speak("Handling recruitment."),
        'manage performance reviews': lambda: speak("Managing performance reviews."),
        'track attendance': lambda: speak("Tracking attendance."),
        'manage financial records': lambda: speak("Managing financial records."),
        'generate financial reports': lambda: speak("Generating financial reports."),
        'track expenses': lambda: speak("Tracking expenses."),
        'create budgets': lambda: speak("Creating budgets."),
        'manage customer data': lambda: speak("Managing customer data."),
        'track customer interactions': lambda: speak("Tracking customer interactions."),
        'handle customer support': lambda: speak("Handling customer support."),
        'manage projects': lambda: speak("Managing projects."),
        'assign tasks': lambda: speak("Assigning tasks."),
        'set deadlines': lambda: speak("Setting deadlines."),
        'track milestones': lambda: speak("Tracking milestones."),
        'manage supply chain': lambda: speak("Managing supply chain."),
        'track shipments': lambda: speak("Tracking shipments."),
        'manage vendors': lambda: speak("Managing vendors."),
        'perform business analytics': lambda: speak("Performing business analytics."),
        'generate dashboards': lambda: speak("Generating dashboards."),
        'predict trends': lambda: speak("Predicting trends."),
        'manage documents': lambda: speak("Managing documents."),
        'track approvals': lambda: speak("Tracking approvals."),
        'archive records': lambda: speak("Archiving records."),
        'handle compliance': lambda: speak("Handling compliance.")
    }
    
    for keyword, handler in erp_commands.items():
        if keyword in command:
            handler()
            return True
    
    return False

# Healthcare Functions
def start_healthcare_robot():
    speak("Starting Healthcare AI Robot. How can I assist you with your health today?")
    
    while True:
        command = recognize_user_speech()
        if command:
            if handle_healthcare_command(command):
                break

def handle_healthcare_command(command):
    healthcare_commands = {
        'provide health tips': lambda: speak(handle_health_tips()),
        'calculate bmi': lambda: speak(handle_bmi_calculation(command)),
        'track calories': lambda: speak(handle_calorie_tracking(command)),
        'set medication reminders': lambda: speak(handle_medication_reminders(command)),
        'provide symptoms analysis': lambda: speak(handle_symptoms_analysis(command)),
        'schedule medical appointments': lambda: speak(handle_appointment_scheduling(command)),
        'give fitness recommendations': lambda: speak(handle_fitness_recommendations(command))
    }
    
    for keyword, handler in healthcare_commands.items():
        if keyword in command:
            handler()
            return True
    
    return False

def handle_health_tips():
    tips = [
        "Stay hydrated and drink at least 8 glasses of water a day.",
        "Eat a balanced diet with plenty of fruits and vegetables.",
        "Get regular exercise to maintain a healthy weight.",
        "Get enough sleep each night.",
        "Practice good hygiene to prevent illness."
    ]
    return tips

def handle_bmi_calculation(command):
    try:
        height = float(input("Enter your height in meters: "))
        weight = float(input("Enter your weight in kilograms: "))
        bmi = weight / (height ** 2)
        return f"Your BMI is {bmi:.2f}."
    except ValueError:
        return "Invalid input. Please enter numerical values for height and weight."

def handle_calorie_tracking(command):
    try:
        calories = int(input("Enter the number of calories consumed: "))
        activity = input("Enter the type of activity performed: ")
        # Placeholder logic
        return f"Tracked {calories} calories consumed and activity: {activity}."
    except ValueError:
        return "Invalid input. Please enter a numerical value for calories."

def handle_medication_reminders(command):
    medication = input("Enter the name of the medication: ")
    time = input("Enter the time to set the reminder (HH:MM): ")
    # Placeholder logic
    return f"Reminder set for {medication} at {time}."

def handle_symptoms_analysis(command):
    symptoms = input("Enter the symptoms you are experiencing: ")
    # Placeholder logic
    return f"Analyzing symptoms: {symptoms}."

def handle_appointment_scheduling(command):
    appointment = input("Enter the details of the medical appointment: ")
    # Placeholder logic
    return f"Medical appointment scheduled: {appointment}."

def handle_fitness_recommendations(command):
    recommendations = [
        "Engage in at least 30 minutes of physical activity daily.",
        "Include strength training exercises in your routine.",
        "Take breaks and stretch regularly if sitting for long periods.",
        "Consider consulting a fitness professional for personalized advice."
    ]
    return recommendations

# FinTech Functions
def start_fintech_system():
    speak("Starting FinTech system. How can I assist you with your financial tasks today?")
    
    while True:
        command = recognize_user_speech()
        if command:
            if handle_fintech_command(command):
                break

def handle_fintech_command(command):
    fintech_commands = {
        'provide stock updates': lambda: speak(handle_stock_market_update()),
        'track investments': lambda: speak(handle_investments_tracking()),
        'manage budgets': lambda: speak(handle_budget_management()),
        'generate financial reports': lambda: speak(handle_financial_reports_generation()),
        'provide financial advice': lambda: speak(handle_financial_advice()),
        'track expenses': lambda: speak(handle_expense_tracking())
    }
    
    for keyword, handler in fintech_commands.items():
        if keyword in command:
            handler()
            return True
    
    return False

def handle_stock_market_update():
    ticker = input("Enter the stock ticker symbol: ")
    stock = yf.Ticker(ticker)
    info = stock.info
    return f"Stock update for {ticker}: {info['longName']} - ${info['currentPrice']}"

def handle_investments_tracking():
    # Placeholder logic
    return "Tracking investments."

def handle_budget_management():
    # Placeholder logic
    return "Managing budgets."

def handle_financial_reports_generation():
    # Placeholder logic
    return "Generating financial reports."

def handle_financial_advice():
    # Placeholder logic
    return "Providing financial advice."

def handle_expense_tracking():
    # Placeholder logic
    return "Tracking expenses."

# Personal AI Functions
def start_personal_ai():
    speak("Starting Personal AI. How can I assist you with personal tasks today?")
    
    while True:
        command = recognize_user_speech()
        if command:
            if handle_personal_ai_command(command):
                break

def handle_personal_ai_command(command):
    personal_ai_commands = {
        'manage calendar': lambda: speak("Managing calendar."),
        'set reminders': lambda: speak("Setting reminders."),
        'send email': lambda: speak("Sending email."),
        'play music': lambda: speak("Playing music."),
        'manage to-do list': lambda: speak("Managing to-do list."),
        'track habits': lambda: speak("Tracking habits.")
    }
    
    for keyword, handler in personal_ai_commands.items():
        if keyword in command:
            handler()
            return True
    
    return False

# General AI Functions
def handle_joke():
    return pyjokes.get_joke()

def handle_math(command):
    try:
        expression = command.replace('solve', '').strip()
        result = sp.sympify(expression).evalf()
        return f"The result is: {result}"
    except Exception as e:
        return f"Error solving math problem: {e}"

def handle_summarization(command):
    text = command.replace('summarize', '').strip()
    sentences = sent_tokenize(text)
    return f"Summary: {sentences[0]}"

def handle_dream_analysis(command):
    dream_description = command.replace('analyze my dream', '').strip()
    # Placeholder logic 
    return f"Analyzing dream: {dream_description}."

def handle_wikipedia_query(command):
    query = command.replace('search wikipedia for', '').strip()
    try:
        summary = wiki_wiki.page(query).summary
        return f"Summary from Wikipedia: {summary}"
    except Exception as e:
        return f"Error fetching Wikipedia summary: {e}"

def handle_general_query(command):
    # Placeholder logic for handling general queries
    return "Sorry, I didn't understand that command."

# Main loop
if __name__ == "__main__":
    greet_user()
    while True:
        command = recognize_user_speech()
        if command:
            if handle_command(command):
                break
