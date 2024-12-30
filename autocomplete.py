import os
from datetime import datetime
import pathlib
import google.generativeai as genai
import glob
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_gemini():
    token_path = pathlib.Path.home() / 'googleapi.txt'
    with open(token_path, 'r') as file:
        api_key = file.read().strip()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

def get_timestamps():
    logging.info("Getting timestamps...")
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    home_dir = str(pathlib.Path.home())
    rewind_dir = os.path.join(home_dir, "Rewind")
    logging.debug(f"Rewind directory path: {rewind_dir}")
    
    timestamps = []
    if os.path.exists(rewind_dir):
        for file in glob.glob(os.path.join(rewind_dir, "screenshot_*.txt")):
            timestamp = os.path.basename(file).replace("screenshot_", "").replace(".txt", "")
            timestamps.append(timestamp)
            logging.debug(f"Found timestamp: {timestamp}")
    
    return current_timestamp, sorted(timestamps), rewind_dir

def find_closest_timestamp(target_time, timestamps):
    target_dt = datetime.strptime(target_time, "%Y%m%d_%H%M%S")
    closest = min(timestamps, key=lambda x: abs(datetime.strptime(x, "%Y%m%d_%H%M%S") - target_dt))
    return closest

def ask_gemini(model, question, text_content):
    logging.info("Sending request to Gemini...")
    try:
        prompt = f"""Question: {question}
Content from screenshot: {text_content}
Please provide a summary of what was happening based on the text content."""
        
        response = model.generate_content(prompt)
        logging.info("Response received from Gemini")
        return response.text
        
    except Exception as e:
        logging.error(f"Error in Gemini request: {str(e)}")
        return f"Error generating response: {str(e)}"

def main():
    try:
        model = setup_gemini()
        current_time, timestamps, rewind_dir = get_timestamps()
        
        if not timestamps:
            print("No recorded timestamps found in Rewind directory")
            return
            
        question = input("What would you like to know about your past screenshots? ")
        logging.info(f"User question: {question}")
        
        closest_time = find_closest_timestamp(current_time, timestamps)
        text_file = os.path.join(rewind_dir, f"screenshot_{closest_time}.txt")
        
        with open(text_file, 'r') as f:
            content = f.read()
        
        response = ask_gemini(model, question, content)
        print(f"\nResponse for timestamp {closest_time}:")
        print(response)
        
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
