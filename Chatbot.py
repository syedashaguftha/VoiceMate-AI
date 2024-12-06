import speech_recognition as sr
import datetime
import webbrowser
import os
import pyttsx3
import pywhatkit as kit
import pyautogui
import time
import google.generativeai as ai
from datetime import datetime as dt
import googletrans
import gtts
import pygame
import threading
from plyer import notification

# Initialize Google Generative AI
API_KEY = 'AIzaSyB1kneFazjmvCCbUSH6HnEaXPhR6lMUNXA'
ai.configure(api_key=API_KEY)
model = ai.GenerativeModel("gemini-pro")
chat = model.start_chat()

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good morning sir!")
    elif hour >= 12 and hour < 18:
        speak("Good afternoon sir!")
    else:
        speak("Good evening sir!")

    speak("I'm VoiceMate AI, please tell me how may I help you")


def takeCommand():
    # It takes microphone input from user and returns string output
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...!")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...!")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        # print(e)
        print("Say that again please...!")
        return "none"
    return query.lower()


def search_google(query):
    google_search_url = f"https://www.google.com/search?q={query}"
    webbrowser.open(google_search_url)


def search_youtube(query):
    youtube_search_url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(youtube_search_url)


def send_whatsapp_message(phone_number, message):
    # Send the WhatsApp message immediately
    kit.sendwhatmsg_instantly(phone_number, message)

    # Wait for a few seconds to ensure the message is typed
    time.sleep(10)  # Adjust the sleep time if needed based on your system's performance

    # Press 'Enter' to send the message
    pyautogui.press('enter')


def run_chatbot():
    speak("Chatbot activated. How can I help you today?")
    while True:
        query = takeCommand()

        if 'stop' in query or 'quit' in query:
            speak("Chatbot deactivated. Goodbye!")
            break
        else:
            response = chat.send_message(query)
            response_text = response.text
            print("Chatbot: ", response_text)
            speak(response_text)


def set_reminder(remind_datetime, task):
    delta_seconds = (remind_datetime - dt.now()).total_seconds()
    if delta_seconds > 0:
        print(f"Reminder set for {remind_datetime.strftime('%Y-%m-%d %H:%M')}: '{task}'.")
        speak(f"Reminder set for {remind_datetime.strftime('%Y-%m-%d %H:%M')}: '{task}'.")
        timer = threading.Timer(delta_seconds, remind_task, args=[task])
        timer.start()


def remind_task(task):
    print(f"Reminder: It's time for your scheduled task '{task}'!")
    speak(f"Reminder: It's time for your scheduled task '{task}'!")

    # Display a system tray notification
    notification_title = "Reminder"
    notification_message = f"It's time for your scheduled task:\n'{task}'!"
    notification.notify(
        title=notification_title,
        message=notification_message,
        app_icon=None,  # You can set an icon path if desired
        timeout=10  # Notification will stay for 10 seconds
    )


def countdown_timer(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        timer = f'{mins:02d}:{secs:02d}'
        print(timer, end='\r')
        time.sleep(1)
        seconds -= 1

    speak("Time's up!")
    speak("Time's up!")
    speak("Time's up!")
    speak("Time's up!")
    speak("Time's up!")
    print("Time's up!")
    speak("Time's up!")


def translate_text():
    # Supported languages
    language_codes = {
        "english": "en",
        "hindi": "hi",
        "kannada": "kn",
        "tamil": "ta",
        "telugu": "te",
        "malayalam": "ml",
        "bengali": "bn",
        "marathi": "mr",
        "gujarati": "gu",
        "punjabi": "pa",
        "urdu": "ur"
    }

    def get_language_code(language_name):
        return language_codes.get(language_name.lower())

    def listen_for_language(prompt):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            speak(prompt)
            print(prompt)
            audio = recognizer.listen(source)
            try:
                language = recognizer.recognize_google(audio, language='en-in').lower()
                print(f"Recognized language: {language}")
                return language
            except sr.UnknownValueError:
                speak("Sorry, I didn't catch that. Please try again.")
                return listen_for_language(prompt)
            except sr.RequestError:
                speak("Sorry, there was an error with the recognition service. Please try again.")
                return listen_for_language(prompt)

    # Prompt for input and output languages
    input_language = listen_for_language("Please specify the input language.")
    output_language = listen_for_language("Please specify the output language.")

    input_lang_code = get_language_code(input_language)
    output_lang_code = get_language_code(output_language)

    if not input_lang_code or not output_lang_code:
        speak("Unsupported language specified. Please restart the program and try again.")
        raise ValueError("Unsupported language specified.")

    # Recognize the text
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Speak now")
        print("Speak now")
        voice = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(voice, language=input_lang_code)
            print(f"Recognized text: {text}")
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Please try again.")
            raise
        except sr.RequestError:
            speak("Sorry, there was an error with the recognition service. Please try again.")
            raise

    # Translate the text
    translator = googletrans.Translator()
    translation = translator.translate(text, dest=output_lang_code)
    print(f"Translated text: {translation.text}")

    # Convert translated text to speech
    converted_audio = gtts.gTTS(translation.text, lang=output_lang_code)
    audio_file = "translated_audio.mp3"
    converted_audio.save(audio_file)

    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(1)

    # Ensure the file is closed and then delete it
    pygame.mixer.music.unload()
    os.remove(audio_file)


if __name__ == "__main__":
    wishMe()
    while True:
        query = takeCommand().lower()

        if 'open stackoverflow' in query:
            webbrowser.open("stackoverflow.com")

        elif 'what is the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")

        elif 'open code' in query:
            codepath = "C:\\Users\\Asus\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            os.startfile(codepath)

        elif 'google search' in query:
            speak("What do you want to search on Google?")
            google_query = takeCommand().lower()
            search_google(google_query)

        elif 'youtube search' in query:
            speak("What do you want to search on YouTube?")
            youtube_query = takeCommand().lower()
            search_youtube(youtube_query)

        elif 'send whatsapp' in query:
            speak("Please provide the phone number including the country code.")
            phone_number = takeCommand().lower()
            speak("What is the message?")
            whatsapp_message = takeCommand().lower()
            send_whatsapp_message(phone_number, whatsapp_message)

        elif 'open chatbot' in query:
            run_chatbot()

        elif 'set reminder' in query:
            speak("Enter the date to set a reminder (YYYY-MM-DD):")
            remind_date = input("Enter the date to set a reminder (YYYY-MM-DD): ")
            speak("Enter the time to set a reminder (HH:MM):")
            remind_time = input("Enter the time to set a reminder (HH:MM): ")
            speak("Enter the task for the reminder:")
            task = input("Enter the task for the reminder: ")

            try:
                remind_datetime = datetime.datetime.strptime(f"{remind_date} {remind_time}", "%Y-%m-%d %H:%M")
                set_reminder(remind_datetime, task)
            except ValueError:
                speak("Invalid date or time format. Please try again.")

        elif 'countdown timer' in query:
            speak("Enter the countdown time in seconds:")
            countdown_seconds = int(input("Enter the countdown time in seconds: "))
            countdown_timer(countdown_seconds)

        elif 'translate text' in query:
            translate_text()
