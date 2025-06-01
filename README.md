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

3. **Access:**
visit http://localhost:7860
