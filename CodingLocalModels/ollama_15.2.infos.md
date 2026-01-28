ollama launch is a new command that sets up and runs your favorite tools like Claude Code, Codex, OpenCode, Clawdbot, and Droid with local or cloud models. No environment variables or config files needed. 
 
Get Started 
Download Ollama 0.15.2+, then download model(s) to run: 

 
GLM 4.7 Flash (~23GB VRAM required with 64k tokens context length) 
 
ollama pull glm-4.7-flash
 
GLM 4.7 (cloud model via Ollama's cloud with full context length) 
 
ollama pull glm-4.7:cloud
 
Ollama's cloud offers a generous free tier for you to get started and try different models. 
Claude Code 
 
ollama launch claude 
 
Clawdbot 
Install Clawdbot and follow its onboarding via clawdbot onboard. 

Configure it to run with Ollama:
ollama launch clawdbot

OpenCode
ollama launch opencode
 
Codex 
ollama launch codex
 
