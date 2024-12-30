import os
from datetime import datetime, timedelta
import pathlib
import google.generativeai as genai
import glob
import logging
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.theme import Theme

# Custom theme for rich
custom_theme = Theme({
    "info": "cyan",
    "timestamp": "green",
    "question": "yellow",
    "response": "bright_white",
    "error": "bold red"
})

console = Console(theme=custom_theme)

# Configure logging with rich handler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

def setup_gemini():
    with Progress(
        SpinnerColumn(),
        TextColumn("[info]Initializing Gemini API...[/info]"),
        transient=True,
    ) as progress:
        progress.add_task("", total=None)
        token_path = pathlib.Path.home() / 'googleapi.txt'
        with open(token_path, 'r') as file:
            api_key = file.read().strip()
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-pro')

def get_timestamps():
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    home_dir = str(pathlib.Path.home())
    rewind_dir = os.path.join(home_dir, "Rewind")
    
    timestamps = []
    if os.path.exists(rewind_dir):
        with Progress(
            SpinnerColumn(),
            TextColumn("[info]Scanning Rewind directory...[/info]"),
            transient=True,
        ) as progress:
            task = progress.add_task("", total=None)
            for file in glob.glob(os.path.join(rewind_dir, "screenshot_*.txt")):
                timestamp = os.path.basename(file).replace("screenshot_", "").replace(".txt", "")
                timestamps.append(timestamp)
    
    return current_timestamp, sorted(timestamps), rewind_dir

def find_closest_timestamp(target_time, timestamps):
    target_dt = datetime.strptime(target_time, "%Y%m%d_%H%M%S")
    closest = min(timestamps, key=lambda x: abs(datetime.strptime(x, "%Y%m%d_%H%M%S") - target_dt))
    return closest

def format_timestamp(timestamp):
    dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
    return dt.strftime("%B %d, %Y at %I:%M:%S %p")

def ask_gemini(model, question, text_contents, timestamps):
    try:
        prompt = f"""You are Rewind, an AI memory assistant. Your task is to analyze screenshots from a user's computer and help them remember what they were doing. Be conversational, friendly, and concise.

User Question: "{question}"

Here are the relevant screenshots, from most recent to oldest:

{text_contents}

When responding:
1. Start with a brief, natural acknowledgment of the question.
2. Provide a clear, direct answer to the question if possible.
3. Describe what you see in the screenshots in a conversational way, focusing on the most relevant information.
4. If you notice any interesting details or patterns across the screenshots, point them out.
5. If the question asks about timing, be specific about dates and times.
6. End with a brief, relevant conclusion or observation.

Remember, you're helping the user recall their recent activities, so be helpful and specific."""

        with Progress(
            SpinnerColumn(),
            TextColumn("[info]Analyzing your memories...[/info]"),
            transient=True,
        ) as progress:
            progress.add_task("", total=None)
            response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        console.print(f"[error]Error in Gemini request: {str(e)}[/error]")
        return f"Error generating response: {str(e)}"

def search_timestamps(timestamps, start_time, end_time):
    start_dt = datetime.strptime(start_time, "%Y%m%d_%H%M%S")
    end_dt = datetime.strptime(end_time, "%Y%m%d_%H%M%S")
    return [ts for ts in timestamps if start_dt <= datetime.strptime(ts, "%Y%m%d_%H%M%S") <= end_dt]

def main():
    try:
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]✨ Rewind Memory Assistant[/bold cyan]\n[dim]Your personal time-travel companion[/dim]",
            border_style="cyan"
        ))
        
        model = setup_gemini()
        current_time, timestamps, rewind_dir = get_timestamps()
        
        if not timestamps:
            console.print("[error]No recorded rewinds found in your timeline[/error]")
            return
        
        console.print(f"\n[info]📚 I've found {len(timestamps)} moments in your timeline[/info]")
        
        question = Prompt.ask("\n[question]🤔 What would you like to rewind to?[/question]")
        
        if any(keyword in question.lower() for keyword in ["when", "last time", "previous"]):
            search_range = Prompt.ask("[question]How far back should I search? (e.g., '1 day', '1 week', '1 month')[/question]")
            
            number, unit = search_range.split()
            number = int(number)
            if unit in ['day', 'days']:
                delta = timedelta(days=number)
            elif unit in ['week', 'weeks']:
                delta = timedelta(weeks=number)
            elif unit in ['month', 'months']:
                delta = timedelta(days=number*30)  # Approximate
            
            end_time = datetime.now()
            start_time = end_time - delta
            
            relevant_timestamps = search_timestamps(timestamps, start_time.strftime("%Y%m%d_%H%M%S"), end_time.strftime("%Y%m%d_%H%M%S"))
            
            if not relevant_timestamps:
                console.print("[error]No rewinds found in the specified time range.[/error]")
                return
            
            timestamps = relevant_timestamps
        
        # Read content from the most recent 5 timestamps (or all if less than 5)
        text_contents = []
        for ts in timestamps[-5:]:
            text_file = os.path.join(rewind_dir, f"screenshot_{ts}.txt")
            with open(text_file, 'r') as f:
                content = f.read()
            text_contents.append(f"Timestamp: {format_timestamp(ts)}\nContent:\n{content}\n{'='*50}")
        
        text_contents = "\n".join(reversed(text_contents))  # Reverse to have most recent first
        
        response = ask_gemini(model, question, text_contents, timestamps)
        
        # Format and display response
        console.print("\n[timestamp]🕒 Rewind analysis complete[/timestamp]")
        console.print(Panel(    
            Text(response, style="response"),
            title="[bold]💭 Rewind Retrieved[/bold]",
            border_style="cyan"
        ))
        
        console.print("\n[dim]Feel free to ask about another rewind...[/dim]")
        
    except Exception as e:
        console.print(f"[error]⚠️ Oops! Something went wrong: {str(e)}[/error]")

if __name__ == "__main__":
    main()
