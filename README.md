# Digital Biographer

## Project Overview

Digital Biographer is a privacy-first local AI-powered conversation system designed to preserve and capture the subjective essence of a person through regular biographical sessions. Unlike conventional memory that exists in the minds of others, this project aims to create a comprehensive digital representation of an individual's inner world, thoughts, and perspectives.

## 🚀 Quick Start

### Prerequisites
- Docker recommended (but not required)
- GPU recommended (but not required)

### Installation

1. **Ollama GPU LLM server:**
```
git clone https://github.com/format37/ollama.git
cd ollama
sudo chmod +x serve_ollama.sh
sudo chmod +x logs.sh
sudo chmod +x pull_model.sh
./compose.sh
./pull_model.sh huihui_ai/deepseek-r1-abliterated:8b
./logs.sh
```
2. **Biographer:**
```bash
git clone https://github.com/format37/biographer.git
cd biographer
sudo chmod +x compose.sh
sudo chmod +x logs.sh
./compose.sh
./logs.sh
```

3. **Access:** visit http://localhost:7860

## ✨ Features

### 🎭 Biographical Sessions
- **Deep Self-Reflection:** 30+ thoughtful questions designed to capture your authentic voice
- **Preserve Your Perspective:** Document your worldview, values, and unique thoughts
- **Private & Judgment-Free:** Safe space for expressing ideas that might not have other outlets

### 💬 General Chat
- **Daily AI Assistant:** Ask questions, get help, casual conversations
- **Context Aware:** Maintains conversation history within sessions
- **Always Available:** Patient digital companion for any topic

### 🔒 Privacy & Data Control
- **100% Local Operation:** All processing on your machine, verified offline capability
- **Your Data, Your Control:** Conversations saved as editable JSON files
- **No External Transmission:** Nothing leaves your computer during normal operation
- **Transparent Storage:** Human-readable format in `data/` directory

### ⌨️ User Experience
- **Keyboard Shortcuts:** Shift+Enter to send messages
- **Dual Interface:** Choose between web interface or command-line
- **Real-time Saving:** All conversations automatically preserved with timestamps

## 🏗️ Architecture

- **AI Backend:** Ollama running locally
- **Models:** Compatible with any Ollama model (default: qwen2.5:7b)
- **Interface:** Gradio web app + command-line option
- **Storage:** Timestamped JSON files
- **Privacy:** Fully offline operation

## 📊 Data Format

Each conversation is saved as structured JSON:
```json
{
  "timestamp": "2025-01-06T...",
  "session_type": "biographical",
  "user": "Your message",
  "assistant": "AI response"
}
```

## 🎯 Use Cases

### Personal Development
- Structured self-reflection through guided questions
- Track personal growth and changing perspectives over time
- Work through thoughts in a non-judgmental environment

### Legacy Preservation
- Capture your authentic voice beyond what others remember
- Document unique perspectives and reasoning
- Create a comprehensive personal archive

### Daily Assistant
- Get help with questions and problems
- Practice conversations or work through ideas
- Always-available, patient digital companion

## 🛠️ Technical Requirements

- **RAM:** 8GB+ recommended
- **Storage:** Minimal (conversations are small JSON files)
- **GPU:** Optional but recommended for faster responses
- **Network:** Internet only needed for initial setup

## 🔧 Customization

- **Change Models:** Edit model name in the Python files
- **Adjust Questions:** Modify the biographical question pool
- **Data Location:** Configure storage directory
- **Interface:** Choose web or command-line interface

## 🚨 Important Notes

- Keep Ollama running in background: `ollama serve`
- All data stays on your machine - you have complete control
- Conversations can be edited or deleted anytime
- The system is designed for long-term personal use

## 🤝 Contributing

This is a personal archival tool, but suggestions and improvements are welcome through issues and pull requests.

## 📄 License

[Your chosen license]

---

**Start preserving your authentic voice today.** Begin with a biographical session and discover what makes your perspective unique.