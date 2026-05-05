git init
git config user.email "you@example.com"
git config user.name "Your Name"
git add .
git commit -m "Initial commit"

mkdir -p .devcontainer
cat <<EOL > .devcontainer/devcontainer.json
{
    "name": "My Codespace",
    "image": "mcr.microsoft.com/vscode/devcontainers/python:3.8",
    "postStartCommand": "python3 /workspaces/tool/zero.py",
    "customizations": {
        "vscode": {
            "settings": {
                "python.pythonPath": "/usr/local/bin/python"
            },
            "extensions": [
                "ms-python.python"
            ]
        }
    }
}
EOL

git add .devcontainer/devcontainer.json
git commit -m "Add postStartCommand to run Python script automatically"
git push origin main
