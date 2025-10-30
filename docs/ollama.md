# Install Ollama in your PC

1. Go to https://ollama.com
2. Go to **Download** and get the command for the installer by executing the following command:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
3. Restart the computer to complete NVIDIA CUDA driver install

# Install the model
4. Choose your model (clic **Models**):
5. Download and set up the chosen LLM on your machine (you’ll find a command to run it in the upper-right hand corner of the model page):
```bash
ollama run llama3.3
```
    The model will run and you can start asking questions

To get other models, run the following command:
```bash
ollama pull gemma3
```