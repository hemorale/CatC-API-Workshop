# Environment Setup Instructions

To run this project, you need to define the following environment variables:

- `DNAC_IP`: IP address of the Cisco DNAC/CatC instance
- `DNAC_USERNAME`: Your DNAC/CatC username
- `DNAC_PASSWORD`: Your DNAC/CatC password

You can define these environment variables in different ways depending on your operating system. Choose one of the methods below:

---

## 🔐 Option 1: Using a `.env` File (Recommended for Development)

1. Create a file named `.env` in the project root.
2. Add the following contents:

    ```env
    DNAC_IP=192.168.1.1
    DNAC_USERNAME=admin
    DNAC_PASSWORD=your_password_here
    ```

3. Make sure your Python code loads the `.env` file using `python-dotenv`:

    ```python
    from dotenv import load_dotenv
    load_dotenv()
    ```

> ✅ This method is secure and portable, and keeps secrets out of the source code.

---

## 🪟 Windows

### Temporary (for Command Prompt or PowerShell session):

```cmd
set DNAC_IP=192.168.1.1
set DNAC_USERNAME=admin
set DNAC_PASSWORD=your_password_here
```

### Permanent (User Environment Variables via PowerShell):

```powershell
[System.Environment]::SetEnvironmentVariable("DNAC_IP", "192.168.1.1", "User")
[System.Environment]::SetEnvironmentVariable("DNAC_USERNAME", "admin", "User")
[System.Environment]::SetEnvironmentVariable("DNAC_PASSWORD", "your_password_here", "User")
```

---

## 🍎 macOS and 🐧 Linux

### Temporary (for current shell session):

```bash
export DNAC_IP=192.168.1.1
export DNAC_USERNAME=admin
export DNAC_PASSWORD=your_password_here
```

### Permanent (add to your shell configuration file):

For Bash (`~/.bashrc` or `~/.bash_profile`):

```bash
export DNAC_IP=192.168.1.1
export DNAC_USERNAME=admin
export DNAC_PASSWORD=your_password_here
```

For Zsh (`~/.zshrc`):

```bash
export DNAC_IP=192.168.1.1
export DNAC_USERNAME=admin
export DNAC_PASSWORD=your_password_here
```

After editing the file, apply the changes:

```bash
source ~/.bashrc   # or source ~/.zshrc
```

---

## ✅ Verification

To check that the environment variables are set correctly, you can run:

```bash
echo $DNAC_IP          # macOS/Linux
echo %DNAC_IP%         # Windows
```

Or print from Python:

```python
import os
print(os.getenv("DNAC_IP"))
```

---

## ⚠️ Security Tip

Do **not** commit your `.env` file or credentials to version control. Use `.gitignore` to exclude it:

```bash
# .gitignore
.env
```

---
