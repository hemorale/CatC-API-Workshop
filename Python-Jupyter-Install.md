## 1. Install Python (if not already installed)

- Windows or macOS: [Download and install the official Python package](https://www.python.org/downloads/).
- Linux: Use your distribution’s package manager (e.g., sudo apt-get install python3 on Ubuntu/Debian).

Make sure that Python is added to your system PATH so you can use python and pip from the terminal.

---

## 2. Create a Virtual Environment (Recommended)

It’s a best practice to use a dedicated virtual environment for your projects. 
1. Open a terminal or command prompt in your project’s directory.
2. Run one of the following commands (depending on your OS):

   - Windows:
     
     python -m venv venv
     .\venv\Scripts\activate
     
   - macOS/Linux:
     
     python3 -m venv venv
     source venv/bin/activate
     
Your shell prompt should change to indicate you’re now inside the virtual environment.

---

## 3. Install Jupyter

Within the activated virtual environment, install Jupyter with:
pip install jupyter
This will fetch and install the Jupyter notebook package and its dependencies.

---

## 4. Launch Jupyter Notebook

After installation, launch Jupyter Notebook from the same activated terminal with:
jupyter notebook
- This command will open a new browser window (or tab) at http://localhost:8888/tree, showing the Jupyter interface.
- You can create new notebooks, open existing ones, and manage your project’s files from here.

---

## 5. (Optional) Install JupyterLab

JupyterLab is the next-generation interface for Jupyter, offering a more modern UI. You can install it with:
pip install jupyterlab
Then start it with:
jupyter lab
It provides the same underlying notebook functionalities but a more flexible interface.

---

## 6. Organize Your Notebooks

Inside your virtual environment, you can manage packages using pip install for everything you need to use in your notebook. Keeping your libraries updated and pinned in a requirements.txt file is often helpful:
pip freeze > requirements.txt
---

### Summary

1. Install Python if not installed.  
2. Create and activate a virtual environment.  
3. Run pip install jupyter.  
4. Launch Jupyter notebook with jupyter notebook.  
5. (Optional) For a more advanced UI, install and launch JupyterLab.  

Now you’re ready to start creating and running notebooks for the lab
