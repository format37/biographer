#!/usr/bin/env python3
import json
import os
import random
from datetime import datetime
from typing import Dict, List, Tuple

import ollama
import gradio as gr


class DigitalBiographer:
    def __init__(self, model_name: str = None, data_dir: str = "data", config_file: str = "config_en.json"):
        # Load configuration
        self.config = self.load_config(config_file)
        
        # Use model from config if not provided
        if model_name is None:
            model_name = self.config["model"]["name"]
        
        self.model_name = model_name
        self.data_dir = data_dir
        
        # Session tracking
        self.current_bio_session_file = None
        self.current_gen_session_file = None
        
        # Ensure data directories exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "bio"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "general"), exist_ok=True)
        
        # Initialize Ollama client
        try:
            self.client = ollama.Client()
            # Test connection
            self.client.list()
        except Exception as e:
            raise ConnectionError(self.config["error_messages"]["ollama_connection"].format(error=e))
    
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{config_file}' not found")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def generate_biographical_question(self) -> str:
        """Generate a contextual biographical prompt based on recent conversations"""
        # Try to get recent biographical conversations for context
        recent_context = self.get_recent_biographical_context()
        
        if not recent_context:
            # Fall back to base prompts if no recent conversations
            return self.get_fallback_question()
        
        # Generate contextual question based on recent conversations
        try:
            system_prompt = self.config["system_prompts"]["question_generator"]
            
            context_message = f"""Recent biographical conversations:

{recent_context}

Generate a thoughtful follow-up question for the next conversation."""
            
            question = self.chat_with_ai(context_message, system_prompt)
            
            # Clean up the response (remove quotes, extra formatting)
            question = question.strip().strip('"').strip("'")
            
            # Ensure it ends with a question mark
            if not question.endswith('?'):
                question += '?'
                
            return question
            
        except Exception as e:
            print(f"Error generating contextual question: {e}")
            return self.get_fallback_question()
    
    def get_recent_biographical_context(self, max_messages: int = 10) -> str:
        """Get recent biographical conversation context"""
        bio_dir = os.path.join(self.data_dir, "bio")
        if not os.path.exists(bio_dir):
            return ""
        
        # Get all biographical session files from bio subdirectory
        bio_files = []
        for filename in os.listdir(bio_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(bio_dir, filename)
                try:
                    mtime = os.path.getmtime(filepath)
                    bio_files.append((filepath, mtime))
                except:
                    continue
        
        if not bio_files:
            return ""
        
        # Sort by modification time (most recent first)
        bio_files.sort(key=lambda x: x[1], reverse=True)
        
        # Collect recent messages
        recent_messages = []
        messages_collected = 0
        
        for filepath, _ in bio_files:
            if messages_collected >= max_messages:
                break
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if 'messages' in data:
                    # New session format - get messages from most recent to oldest
                    session_messages = data['messages'][-max_messages:]  # Get last messages from session
                    for msg in reversed(session_messages):  # Reverse to get most recent first
                        if messages_collected >= max_messages:
                            break
                        recent_messages.append({
                            'timestamp': msg['timestamp'],
                            'user': msg['user'],
                            'assistant': msg['assistant']
                        })
                        messages_collected += 1
                        
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                continue
        
        if not recent_messages:
            return ""
        
        # Sort by timestamp (most recent first) 
        recent_messages.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Format for context
        context_parts = []
        for i, msg in enumerate(recent_messages):
            # Parse timestamp for readable format
            try:
                dt = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                time_str = dt.strftime('%Y-%m-%d %H:%M')
            except:
                time_str = "Recent"
            
            context_parts.append(f"[{time_str}]")
            context_parts.append(f"Human: {msg['user']}")
            context_parts.append(f"AI: {msg['assistant']}")
            context_parts.append("---")
        
        return '\n'.join(context_parts)
    
    def get_fallback_question(self) -> str:
        """Get a fallback question when no recent context is available"""
        # Get current time context
        current_time = datetime.now()
        day_of_week = current_time.strftime("%A")
        time_of_day = "morning" if current_time.hour < 12 else "afternoon" if current_time.hour < 18 else "evening"
        
        # Create a dynamic prompt that considers the ongoing nature of the project
        base_prompts = [
            f"How are you feeling this {day_of_week} {time_of_day}? What's been on your mind lately?",
            "What's something significant that happened to you recently? How did it make you feel or think?",
            "Is there anything you've been reflecting on or questioning about yourself or your life lately?",
            "What's been bringing you joy or concern in your daily life recently?",
            "How would you describe your current state of mind or outlook on life?",
            "What's something you've learned about yourself recently, even if it's small?",
            "Is there a moment from today, yesterday, or this week that stood out to you? Why?",
            "What are you currently curious about, struggling with, or excited about?",
            "How has your perspective on something changed recently?",
            "What would you want to remember about this particular time in your life?"
        ]
        
        return random.choice(base_prompts)
    
    def chat_with_ai(self, message: str, system_prompt: str = None, conversation_history: str = "") -> str:
        """Send message to Ollama and get response"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Parse conversation history to build context
            if conversation_history:
                # Extract previous exchanges from the history
                lines = conversation_history.split('\n')
                current_user_msg = None
                current_ai_msg = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('**You:**'):
                        if current_user_msg and current_ai_msg:
                            messages.append({"role": "user", "content": current_user_msg})
                            messages.append({"role": "assistant", "content": current_ai_msg})
                        current_user_msg = line.replace('**You:**', '').strip()
                        current_ai_msg = None
                    elif line.startswith('**AI:**') or line.startswith('**AI Biographer:**'):
                        current_ai_msg = line.replace('**AI:**', '').replace('**AI Biographer:**', '').strip()
                
                # Add the last pair if complete
                if current_user_msg and current_ai_msg:
                    messages.append({"role": "user", "content": current_user_msg})
                    messages.append({"role": "assistant", "content": current_ai_msg})
            
            # Add datetime prefix to current message for AI context
            current_time = datetime.now()
            datetime_prefix = f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] "
            message_with_datetime = datetime_prefix + message
            
            # Add current message with datetime prefix
            messages.append({"role": "user", "content": message_with_datetime})
            
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                stream=False
            )
            
            return response['message']['content']
            
        except Exception as e:
            return self.config["error_messages"]["ai_communication"].format(error=e)
    
    def start_new_session(self, session_type: str) -> str:
        """Start a new session and create a new session file"""
        timestamp = datetime.now()
        
        # Use subdirectories and new datetime format
        if session_type == "biographical":
            subdir = "bio"
        else:
            subdir = "general"
            
        session_dir = os.path.join(self.data_dir, subdir)
        filename = os.path.join(session_dir, f"{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}.json")
        
        # Initialize session file
        session_data = {
            "session_type": session_type,
            "start_time": timestamp.isoformat(),
            "messages": []
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        # Track current session file
        if session_type == "biographical":
            self.current_bio_session_file = filename
        else:
            self.current_gen_session_file = filename
        
        return filename
    
    def save_conversation(self, user_message: str, ai_response: str, session_type: str = "general"):
        """Add conversation to current session file"""
        # Determine which session file to use
        if session_type == "biographical":
            session_file = self.current_bio_session_file
        else:
            session_file = self.current_gen_session_file
        
        # Create new session if none exists
        if not session_file or not os.path.exists(session_file):
            session_file = self.start_new_session(session_type)
        
        # Load existing session data
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
        except:
            # If file is corrupted, start a new session
            session_file = self.start_new_session(session_type)
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
        
        # Add new message pair
        message_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "assistant": ai_response
        }
        
        session_data["messages"].append(message_entry)
        session_data["last_updated"] = datetime.now().isoformat()
        
        # Save updated session
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def biographical_conversation(self, message: str, history: str) -> Tuple[str, str]:
        """Handle biographical conversation with AI"""
        if not message.strip():
            return history, ""
            
        system_prompt = self.config["system_prompts"]["biographical"]
        
        response = self.chat_with_ai(message, system_prompt, history)
        
        # Save conversation (original message without datetime prefix)
        self.save_conversation(message, response, "biographical")
        
        # Add datetime prefix for history display and future AI context
        current_time = datetime.now()
        datetime_prefix = f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] "
        message_with_datetime = datetime_prefix + message
        
        # Update history with datetime prefix
        new_history = history + f"\n\n**You:** {message_with_datetime}\n\n**AI Biographer:** {response}\n\n---"
        
        return new_history, ""
    
    def general_conversation(self, message: str, history: str) -> Tuple[str, str]:
        """Handle general conversation with AI"""
        if not message.strip():
            return history, ""
            
        system_prompt = self.config["system_prompts"]["general"]
        
        response = self.chat_with_ai(message, system_prompt, history)
        
        # Save conversation (original message without datetime prefix)
        self.save_conversation(message, response, "general")
        
        # Add datetime prefix for history display and future AI context
        current_time = datetime.now()
        datetime_prefix = f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] "
        message_with_datetime = datetime_prefix + message
        
        # Update history with datetime prefix
        new_history = history + f"\n\n**You:** {message_with_datetime}\n\n**AI:** {response}\n\n---"
        
        return new_history, ""
    
    def get_biographical_welcome_message(self) -> str:
        """Get biographical welcome message without creating session file"""
        # Get recent context to determine if we're generating contextual or fallback questions
        recent_context = self.get_recent_biographical_context()
        
        if recent_context:
            # Generate contextual question
            question = self.generate_biographical_question()
            welcome_msg = self.config["messages"]["biographical_welcome"].format(question=question)
            return welcome_msg + "\n\n*✨ This question was generated based on your recent conversations.*"
        else:
            # Use fallback question
            question = self.generate_biographical_question()  # Will use fallback
            return self.config["messages"]["biographical_welcome"].format(question=question)
    
    def get_general_welcome_message(self) -> str:
        """Get general welcome message without creating session file"""
        return self.config["messages"]["general_welcome"]

    def start_biographical_session(self) -> str:
        """Start a new biographical session"""
        # Reset session tracking - new session will be created on first message
        self.current_bio_session_file = None
        
        return self.get_biographical_welcome_message()
    
    def start_general_session(self) -> str:
        """Start a new general chat session"""
        # Reset session tracking - new session will be created on first message
        self.current_gen_session_file = None
        
        return self.get_general_welcome_message()
    
    def get_data_info(self) -> str:
        """Get information about saved conversations"""
        if not os.path.exists(self.data_dir):
            return self.config["messages"]["no_conversations"]
        
        # Check both subdirectories
        bio_dir = os.path.join(self.data_dir, "bio")
        general_dir = os.path.join(self.data_dir, "general")
        
        files = []
        
        # Get files from bio directory
        if os.path.exists(bio_dir):
            bio_files = [os.path.join(bio_dir, f) for f in os.listdir(bio_dir) if f.endswith('.json')]
            files.extend(bio_files)
        
        # Get files from general directory  
        if os.path.exists(general_dir):
            general_files = [os.path.join(general_dir, f) for f in os.listdir(general_dir) if f.endswith('.json')]
            files.extend(general_files)
        
        # Also check for any legacy files in the main data directory
        legacy_files = []
        for f in os.listdir(self.data_dir):
            if f.endswith('.json'):
                legacy_files.append(os.path.join(self.data_dir, f))
        files.extend(legacy_files)
        
        if not files:
            return self.config["messages"]["no_conversations"]
        
        biographical_sessions = 0
        general_sessions = 0
        total_messages = 0
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'messages' in data:  # New session format
                        total_messages += len(data['messages'])
                        if data.get('session_type') == 'biographical' or 'bio' in filepath:
                            biographical_sessions += 1
                        else:
                            general_sessions += 1
                    else:  # Old individual message format
                        total_messages += 1
                        if data.get('session_type') == 'biographical' or 'bio' in filepath:
                            biographical_sessions += 1
                        else:
                            general_sessions += 1
            except:
                continue
        
        return self.config["messages"]["data_stats"].format(
            total_files=len(files),
            bio_sessions=biographical_sessions,
            gen_sessions=general_sessions,
            total_messages=total_messages,
            data_path=os.path.abspath(self.data_dir)
        )


def create_gradio_interface(biographer: DigitalBiographer):
    """Create Gradio web interface"""
    config = biographer.config
    ui_text = config["ui_text"]
    
    with gr.Blocks(title=ui_text["app_title"], theme=gr.themes.Soft()) as interface:
        gr.Markdown(f"# {ui_text['main_heading']}")
        gr.Markdown(ui_text["app_subtitle"])
        
        with gr.Tab(ui_text["biographical_tab"]["title"]):
            gr.Markdown(ui_text["biographical_tab"]["description"])
            
            bio_history = gr.Textbox(
                label=ui_text["biographical_tab"]["history_label"],
                lines=15,
                interactive=False,
                value=biographer.get_biographical_welcome_message()
            )
            bio_input = gr.Textbox(
                label=ui_text["biographical_tab"]["input_label"],
                placeholder=ui_text["biographical_tab"]["input_placeholder"],
                lines=3
            )
            bio_submit = gr.Button(ui_text["biographical_tab"]["submit_button"], variant="primary")
            bio_clear = gr.Button(ui_text["biographical_tab"]["clear_button"], variant="secondary")
            
            # Handle both button click and Shift+Enter
            bio_submit.click(
                biographer.biographical_conversation,
                inputs=[bio_input, bio_history],
                outputs=[bio_history, bio_input]
            )
            
            bio_input.submit(
                biographer.biographical_conversation,
                inputs=[bio_input, bio_history],
                outputs=[bio_history, bio_input]
            )
            
            bio_clear.click(
                biographer.start_biographical_session,
                outputs=[bio_history]
            )
        
        with gr.Tab(ui_text["general_tab"]["title"]):
            gr.Markdown(ui_text["general_tab"]["description"])
            
            gen_history = gr.Textbox(
                label=ui_text["general_tab"]["history_label"],
                lines=15,
                interactive=False,
                value=biographer.get_general_welcome_message()
            )
            gen_input = gr.Textbox(
                label=ui_text["general_tab"]["input_label"],
                placeholder=ui_text["general_tab"]["input_placeholder"],
                lines=2
            )
            gen_submit = gr.Button(ui_text["general_tab"]["submit_button"], variant="primary")
            gen_clear = gr.Button(ui_text["general_tab"]["clear_button"], variant="secondary")
            
            # Handle both button click and Shift+Enter
            gen_submit.click(
                biographer.general_conversation,
                inputs=[gen_input, gen_history],
                outputs=[gen_history, gen_input]
            )
            
            gen_input.submit(
                biographer.general_conversation,
                inputs=[gen_input, gen_history],
                outputs=[gen_history, gen_input]
            )
            
            gen_clear.click(
                biographer.start_general_session,
                outputs=[gen_history]
            )
        
        with gr.Tab(ui_text["data_tab"]["title"]):
            gr.Markdown(ui_text["data_tab"]["description"])
            
            data_info = gr.Textbox(
                label=ui_text["data_tab"]["info_label"],
                lines=8,
                interactive=False,
                value=biographer.get_data_info()
            )
            
            refresh_btn = gr.Button(ui_text["data_tab"]["refresh_button"])
            refresh_btn.click(
                biographer.get_data_info,
                outputs=[data_info]
            )
            
            gr.Markdown(config["messages"]["privacy_info"])
    
    return interface


def main():
    """Main function to run the Digital Biographer"""
    print("Initializing Digital Biographer...")
    
    try:
        # Initialize biographer - will load config automatically
        biographer = DigitalBiographer(config_file="config_ru.json")
        print(biographer.config["console_messages"]["connected"].format(model=biographer.model_name))
        
        # Create and launch interface
        interface = create_gradio_interface(biographer)
        
        print(biographer.config["console_messages"]["launching"])
        print(biographer.config["console_messages"]["access_url"])
        print(biographer.config["console_messages"]["stop_instruction"])
        
        interface.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            inbrowser=True
        )
        
    except ConnectionError as e:
        print(f"Error: {e}")
        print("\nMake sure Ollama is running and the model is available:")
        print("1. Start Ollama: ollama serve")
        print("2. Pull model: ollama pull qwen2.5:7b")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()