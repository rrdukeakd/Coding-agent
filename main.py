import openai
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Root directory for generated projects
PROJECT_ROOT = Path("./ai_generated_project")
PROJECT_ROOT.mkdir(exist_ok=True)

# System prompt that defines the agent's role
SYSTEM_PROMPT = """
You are a full-stack development AI agent.
Your job is to:
 Generate backend and frontend folder structures
 Create files with proper code
 Modify existing files as needed
 Use Python, JS, HTML, CSS, Streamlit, Flask, React, etc.
 Return file operations as: # FILE: filename
 Maintain context from prior interactions
"""

history = [{"role": "system", "content": SYSTEM_PROMPT}]
print(
    "\n🤖 AI Dev Agent: Ready to build full-stack projects in your terminal. Type 'exit' to quit.\n"
)


def save_code_blocks(response_text):
    current_file = None
    buffer = []
    for line in response_text.splitlines():
        if line.strip().startswith("# FILE:"):
            if current_file and buffer:
                write_to_file(current_file, "\n".join(buffer))
                buffer = []
            current_file = line.strip().replace("# FILE:", "").strip()
        elif current_file:
            buffer.append(line)

    if current_file and buffer:
        write_to_file(current_file, "\n".join(buffer))


def write_to_file(filename, content):
    file_path = PROJECT_ROOT / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)
    print(f"✅ Written: {file_path}")


def run_command(command):
    try:
        print(f"\n> Running command: {command}")
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e.stderr}")


while True:
    user_input = input("🧑 You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Exiting the AI Dev Agent.")
        break

    history.append({"role": "user", "content": user_input})

    try:
        response = openai.chat.completions.create(
            model="gpt-4", messages=history, temperature=0.3, max_tokens=2000
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})

        print("\n🤖 AI Agent:")
        print(reply)

        # Extract and save any code blocks to files
        save_code_blocks(reply)

        # Check if response includes shell commands to run
        if "# RUN:" in reply:
            for line in reply.splitlines():
                if line.startswith("# RUN:"):
                    command = line.replace("# RUN:", "").strip()
                    run_command(command)

    except Exception as e:
        print(f"❌ Error communicating with OpenAI: {e}")
