import os
import requests
from dotenv import load_dotenv
import pygame
import uuid
import time
import speech_recognition as sr
import customtkinter as ctk
import threading
import pyautogui
import webbrowser
import cv2
from datetime import datetime, timedelta
import subprocess
from groq import Groq
import pytesseract
from PIL import ImageGrab

# Load environment variables from .env file
load_dotenv()

# Initialize pygame mixer
pygame.mixer.init()

# Create the Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Set the system prompt
system_prompt = {
    "role": "system",
    "content": "Kamu adalah asisten yang membantu. Kamu memberikan jawaban yang sangat singkat dan dalam bahasa Indonesia yang santai dan alami."
}

# Initialize chat history
chat_history = [system_prompt]

def text_to_speech(text):
    api_key = os.environ.get("VOICERSS_API_KEY")
    url = "https://api.voicerss.org/"
    params = {
        "key": api_key,
        "hl": "id-id",
        "src": text,
        "r": "0",
        "c": "mp3",
        "f": "44khz_16bit_stereo"
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        file_name = f"response_{uuid.uuid4()}.mp3"
        with open(file_name, "wb") as f:
            f.write(response.content)
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # Wait for the music to finish playing
            pygame.time.Clock().tick(10)
        time.sleep(0.5)  # Ensure there's enough time before removing the file
        pygame.mixer.music.unload()  # Unload the music to free the file
        os.remove(file_name)  # Remove the file after playing
    else:
        print("Error:", response.status_code, response.text)

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            print("Silakan bicara...")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)

            try:
                text = recognizer.recognize_google(audio, language="id-ID")
                print("Kamu: " + text)
                process_input(text)
            except sr.UnknownValueError:
                print("Maaf, saya tidak mengerti apa yang Anda katakan.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

def process_input(user_input):
    if user_input:
        print(f"Proses perintah: {user_input}")
        if "gerakkan mouse ke" in user_input.lower():
            handle_mouse_command(user_input)
        elif "buka aplikasi" in user_input.lower():
            open_application(user_input)
        elif "tutup aplikasi" in user_input.lower():
            close_application(user_input)
        elif "ketik" in user_input.lower():
            type_text(user_input)
        elif "komunikasi" in user_input.lower():
            communicate_with_camera()
        elif "ketikan kolom pencarian" in user_input.lower():
            type_in_search_box(user_input)
        else:
            chat_response(user_input)

def handle_mouse_command(command):
    try:
        parts = command.lower().split("gerakkan mouse ke")[1].strip().split()
        if len(parts) >= 2:
            x, y = int(parts[0]), int(parts[1])
            pyautogui.moveTo(x, y)
            response_text = f"Saya telah menggerakkan mouse ke posisi ({x}, {y})."
        else:
            response_text = "Format perintah salah. Contoh: 'gerakkan mouse ke 100 200'."
        print(response_text)
        text_to_speech(response_text)
        update_chat_display("Perintah: " + command, response_text)
    except Exception as e:
        error_text = f"Maaf, saya tidak bisa menggerakkan mouse: {e}"
        print(error_text)
        text_to_speech(error_text)
        update_chat_display("Perintah: " + command, error_text)

def open_application(command):
    try:
        print(f"Membuka aplikasi dengan perintah: {command}")
        if "buka aplikasi browser" in command.lower():
            webbrowser.open('http://www.google.com')
            response_text = "Membuka browser."
        elif "buka aplikasi notepad" in command.lower():
            os.system('start notepad.exe')
            response_text = "Membuka Notepad."
        elif "buka aplikasi kalkulator" in command.lower():
            os.system('start calc.exe')
            response_text = "Membuka Kalkulator."
        else:
            response_text = "Aplikasi tidak dikenal. Contoh: 'buka aplikasi browser', 'buka aplikasi notepad', atau 'buka aplikasi kalkulator'."
        print(response_text)
        text_to_speech(response_text)
        update_chat_display("Perintah: " + command, response_text)
    except Exception as e:
        error_text = f"Maaf, saya tidak bisa membuka aplikasi: {e}"
        print(error_text)
        text_to_speech(error_text)
        update_chat_display("Perintah: " + command, error_text)

def close_application(command):
    try:
        print(f"Menutup aplikasi dengan perintah: {command}")
        if "tutup aplikasi notepad" in command.lower():
            os.system('taskkill /f /im notepad.exe')
            response_text = "Menutup Notepad."
        elif "tutup aplikasi kalkulator" in command.lower():
            os.system('taskkill /f /im calc.exe')
            response_text = "Menutup Kalkulator."
        else:
            response_text = "Aplikasi tidak dikenal atau tidak dapat ditutup. Contoh: 'tutup aplikasi notepad' atau 'tutup aplikasi kalkulator'."
        print(response_text)
        text_to_speech(response_text)
        update_chat_display("Perintah: " + command, response_text)
    except Exception as e:
        error_text = f"Maaf, saya tidak bisa menutup aplikasi: {e}"
        print(error_text)
        text_to_speech(error_text)
        update_chat_display("Perintah: " + command, error_text)

def type_text(command):
    try:
        text_to_type = command.lower().split("ketik ")[1].strip()
        pyautogui.typewrite(text_to_type)
        response_text = f"Saya telah mengetik: {text_to_type}"
        print(response_text)
        text_to_speech(response_text)
        update_chat_display("Perintah: " + command, response_text)
    except Exception as e:
        error_text = f"Maaf, saya tidak bisa mengetik: {e}"
        print(error_text)
        text_to_speech(error_text)
        update_chat_display("Perintah: " + command, error_text)

def type_in_search_box(command):
    try:
        search_query = command.lower().split("ketikan kolom pencarian ")[1].strip()
        # Screenshot the screen to find the search box using OCR
        screenshot = ImageGrab.grab()
        screenshot.save("screenshot.png")
        search_box_position = find_search_box("screenshot.png")
        if search_box_position:
            pyautogui.moveTo(search_box_position[0], search_box_position[1])
            pyautogui.click()
            pyautogui.typewrite(search_query)
            response_text = f"Saya telah mengetik di kolom pencarian: {search_query}"
        else:
            response_text = "Kolom pencarian tidak ditemukan."
        print(response_text)
        text_to_speech(response_text)
        update_chat_display("Perintah: " + command, response_text)
    except Exception as e:
        error_text = f"Maaf, saya tidak bisa mengetik di kolom pencarian: {e}"
        print(error_text)
        text_to_speech(error_text)
        update_chat_display("Perintah: " + command, error_text)

def find_search_box(image_path):
    try:
        # Use pytesseract to find the search box
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        custom_config = r'--oem 3 --psm 6'
        boxes = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)
        for i in range(len(boxes['text'])):
            if 'search' in boxes['text'][i].lower():
                (x, y, w, h) = (boxes['left'][i], boxes['top'][i], boxes['width'][i], boxes['height'][i])
                return (x + w // 2, y + h // 2)
        return None
    except Exception as e:
        print(f"Error finding search box: {e}")
        return None

def communicate_with_camera():
    response_text = "Mengaktifkan komunikasi dengan kamera..."
    print(response_text)
    text_to_speech(response_text)
    update_chat_display("Perintah: Komunikasi dengan kamera", response_text)

    def camera_thread():
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            error_text = "Maaf, saya tidak bisa mengakses kamera."
            print(error_text)
            text_to_speech(error_text)
            update_chat_display("Kesalahan", error_text)
            return

        face_detected = False
        while True:
            ret, frame = cap.read()
            if not ret:
                error_text = "Gagal menangkap frame dari kamera."
                print(error_text)
                text_to_speech(error_text)
                update_chat_display("Kesalahan", error_text)
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

            if len(faces) > 0 and not face_detected:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                response_text = "Wajah terdeteksi! Halo, bagaimana saya bisa membantu Anda?"
                print(response_text)
                text_to_speech(response_text)
                update_chat_display("Deteksi Wajah", response_text)
                face_detected = True

            cv2.imshow('Komunikasi dengan Kamera', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        response_text = "Komunikasi dengan kamera telah berakhir."
        print(response_text)
        text_to_speech(response_text)
        update_chat_display("Perintah", response_text)

    threading.Thread(target=camera_thread).start()

def chat_response(user_input):
    chat_history.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=chat_history,
        max_tokens=500,  # Set higher or remove limit if supported by API
        temperature=1.2
    )
    assistant_response = response.choices[0].message.content
    chat_history.append({
        "role": "assistant",
        "content": assistant_response
    })
    print("Asisten:", assistant_response)
    text_to_speech(assistant_response)
    update_chat_display(user_input, assistant_response)

def update_chat_display(user_text, assistant_text):
    chat_display.insert(ctk.END, f"Kamu: {user_text}\n")
    chat_display.insert(ctk.END, f"Asisten: {assistant_text}\n")
    chat_display.see(ctk.END)

# Initialize the GUI
app = ctk.CTk()
app.title("Asisten Virtual")
app.geometry("600x400")

frame = ctk.CTkFrame(app, width=580, height=340)
frame.pack(pady=10)

chat_display = ctk.CTkTextbox(frame, width=560, height=320, wrap='word')
chat_display.pack(pady=10)

# Start speech recognition in a separate thread
def start_speech_recognition():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            print("Silakan bicara...")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)

            try:
                text = recognizer.recognize_google(audio, language="id-ID")
                print("Kamu: " + text)
                process_input(text)
            except sr.UnknownValueError:
                print("Maaf, saya tidak mengerti apa yang Anda katakan.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

thread = threading.Thread(target=start_speech_recognition)
thread.daemon = True
thread.start()

app.mainloop()
