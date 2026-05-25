import speech_recognition as sr
import webbrowser
import time
import urllib.parse
import requests
import os
from google import genai

# NOTE: You should regenerate this API key in the Google Cloud Console soon, 
# as it has been exposed in plain text during our testing!
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.2
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

WAKE_WORDS = ["lamina", "lumina", "laminar", "laina", "alina", "lemina", "lumena", "hey lamina"]

def speak(text):
    """Uses the native macOS voice, bypassing pyttsx3 bugs."""
    print(f"🗣️ Lamina: {text}")
    # Remove single quotes to prevent breaking the terminal command
    safe_text = str(text).replace("'", "")
    os.system(f"say '{safe_text}'")

def aiResponse(question):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question,
    )
    text = response.text
    cleaned_text = text.replace("*", "")
    return cleaned_text
        
def getNews():
    api_key = "YOUR_NEWS_API_KEY"
    url = f"https://newsapi.org/v2/everything?q=technology&apiKey={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data["status"] != "ok":
            speak("Sorry, could not fetch news")
            return
        
        articles = data["articles"]
        if len(articles) == 0:
            speak("No news found")
            return
        
        speak("Here are today's top headlines")

        print("\n" + "="*50)
        print("📰 TODAY'S TOP HEADLINES")
        print("="*50 + "\n")
        
        for i in range(7):
            if i >= len(articles):
                break
            
            title = articles[i]["title"]
            print(f"{i+1}. {title}\n")
            
            # The native speak function naturally waits before reading the next line
            speak(f"Headline {i+1}: {title}")
        
        speak("Those were today's top headlines")
        
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, I could not fetch the news")

def processCommand(c):
    c = c.lower()
    print(f"🔍 Heard: '{c}'")

    news_words = ["news", "headlines", "headline", "new", "knows", "nose", "olds", "update", "updates", "happening"]
    
    if "open google" in c:
        webbrowser.open("https://www.google.com/")
    elif "open facebook" in c:
        webbrowser.open("https://www.facebook.com/")
    elif "open instagram" in c:
        webbrowser.open("https://www.instagram.com/")
    elif "open snapchat" in c:
        webbrowser.open("https://www.snapchat.com/")
    elif "open youtube" in c:
        webbrowser.open("https://www.youtube.com/")
    elif "play" in c:               
        song = c.replace("play", "").strip()    
        speak(f"Searching {song} on YouTube")   
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(song)}"         
        webbrowser.open(search_url)     
    elif any(word in c for word in news_words):
        getNews()
    else:
        answer = aiResponse(c)
        speak(answer)
        
def listen_from_microphone(prompt, timeout=10, phrase_time_limit=12):
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print(prompt)
            return recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except Exception as e:
        print(f"Microphone error: {e}")
        return None

def has_wake_word(text):
    text = text.lower()
    return any(wake_word == text.strip() or wake_word in text.split() for wake_word in WAKE_WORDS)

if __name__ == "__main__":
    speak("Initialising Lamina")
    
    while True:
        audio = listen_from_microphone("Say something!")
        if audio is None:
            break

        print("recognizing...")
        try:
            text = recognizer.recognize_google(audio)
            print("lamina thinks you said: " + text)

            if has_wake_word(text):
                print("Wake word detected: lamina")
                
                # Replaced engine.say with our new reliable speak function
                speak("Yes Hitesh")
                
                # Because the new speak function blocks the code until it finishes talking,
                # you actually don't even need the time.sleep(1) here anymore! The mic 
                # won't open until Lamina completely finishes saying "Yes Hitesh".

                audio = listen_from_microphone("Listening for your command...")
                if audio is None:
                    continue
                
                command = recognizer.recognize_google(audio)
                print("Google thinks you said:", command)
                processCommand(command)
                
        except Exception as e:
            pass # Fails silently if it didn't catch speech properly, keeping the loop clean