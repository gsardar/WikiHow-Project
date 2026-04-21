import requests
import os
import sys
import time
import json
from rich.console import Console
from rich.panel import Panel

BRIDGE_URL = "http://127.0.0.1:8002"
console = Console()

def ask(prompt: str, file_path: str = None) -> str:
    """
    Sends a prompt to the DeepSeek Bare Bridge.
    Ensure bridge.py is running first.
    """
    try:
        payload = {"prompt": prompt}
        if file_path:
            payload["file_path"] = os.path.abspath(file_path)
            
        r = requests.post(f"{BRIDGE_URL}/ask", json=payload, timeout=600)
        if r.status_code == 200:
            return r.json().get("response", "ERROR: No response from bridge")
        return f"HTTP_ERROR: {r.status_code}"
    except Exception as e:
        return f"CONNECTION_FAILED: {e}"

def start_new_chat():
    """Resets the DeepSeek tab to a clean state."""
    try:
        r = requests.post(f"{BRIDGE_URL}/new", timeout=10)
        return r.status_code == 200
    except:
        return False

def trigger_inspect():
    """Activates the listener in the browser to capture CSS selectors."""
    try:
        r = requests.post(f"{BRIDGE_URL}/inspect", timeout=10)
        if r.status_code == 200:
            console.print("[bold yellow]Inspector Mode Active![/bold yellow]")
            console.print("Go to the browser and click the element you want to identify.")
            return True
        return False
    except Exception as e:
        console.print(f"[bold red]Failed to start inspector: {e}[/bold red]")
        return False

def run_ui_preview():
    """Demonstrates the UI appearance without starting the bridge."""
    console.print("\n[bold blue]DeepSeek UI Preview[/bold blue] [dim](MOCK MODE)[/dim]\n")
    user_prompt = "Briefly explain the role of a WikiHow editor."
    console.print(f"[dim]Sending prompt:[/dim] [bold blue]\"{user_prompt}\"[/bold blue]")
    
    with console.status("[blue]Waiting for DeepSeek... [italic](Simulated)[/italic]", spinner="dots8Bit"):
        time.sleep(2)
    
    mock_response = (
        "A wikiHow editor is a community volunteer who ensures articles are accurate and helpful. "
        "They fix typos, patrol recent changes, and guard against vandalism."
    )
    console.print(Panel(mock_response, title="[bold green]DeepSeek Response[/bold green]", border_style="green", padding=(1, 2)))

if __name__ == "__main__":
    args = sys.argv[1:]
    
    # Check for preview flag
    if "--preview" in args:
        run_ui_preview()
        sys.exit(0)

    if "--inspect" in args:
        trigger_inspect()
        sys.exit(0)

    if args:
        user_prompt = " ".join(args)
    else:
        user_prompt = "Hello, introduce yourself briefly."

    console.print(f"\n[dim]Sending prompt:[/dim] [bold blue]\"{user_prompt}\"[/bold blue]")
    
    with console.status("[blue]Waiting for DeepSeek...", spinner="dots8Bit"):
        response = ask(user_prompt)
    
    console.print(Panel(
        response,
        title="[bold green]DeepSeek Response[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
