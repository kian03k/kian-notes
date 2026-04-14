# WSL 2 + Miniconda + PyCharm: The Ultimate Python Development Setup on Windows

This guide provides a step-by-step, best-practice approach to setting up a professional Python development environment on Windows using WSL 2 (Windows Subsystem for Linux), Miniconda, and PyCharm. This combination delivers native Linux performance with the convenience of the Windows UI, making it the gold standard for Python data science and backend development.

## Table of Contents
1.  [Why This Stack?](Python%20Env%20Setup%20for%20wsl2.md#why-this-stack)
2.  [Part 1: Setting Up WSL 2 & Miniconda](Python%20Env%20Setup%20for%20wsl2.md#part-1-setting-up-wsl-2--miniconda)
3.  [Part 2: Connecting PyCharm to WSL](Python%20Env%20Setup%20for%20wsl2.md#part-2-connecting-pycharm-to-wsl)
4.  [Part 3: Best Practices & Troubleshooting](Python%20Env%20Setup%20for%20wsl2.md#part-3-best-practices--troubleshooting)
5.  [Summary Checklist](Python%20Env%20Setup%20for%20wsl2.md#summary-checklist)

---

## Why This Stack?

*   **Native Linux Kernel**: Run your code in a real Linux environment, ensuring production-like compatibility.
*   **Lightning Fast I/O**: By storing code within the WSL filesystem, you avoid the performance penalty of accessing Windows drives (`/mnt/c/`).
*   **Seamless Integration**: PyCharm's built-in WSL support allows you to use the Linux Python interpreter directly, with full debugging, terminal, and GUI (via WSLg) support.
*   **Clean Environment Management**: Miniconda allows you to create isolated Python environments for each project, preventing dependency conflicts.
*   **Resource Efficiency**: Miniconda is a lightweight alternative to Anaconda, containing only `conda` and its dependencies, allowing you to install only what you need.

---

## Part 1: Setting Up WSL 2 & Miniconda

### Step 1: Install and Update WSL 2 (if not already done)

If you haven't installed WSL 2, open **PowerShell as Administrator** and run:

```powershell
# Install WSL and set the default version to WSL 2
wsl --install
wsl --set-default-version 2
```

After installation, restart your computer if prompted. Launch the installed Linux distribution (e.g., Ubuntu) from the Start Menu to complete the initial user setup.

### Step 2: Update Your WSL Distribution

Once inside your WSL terminal (e.g., Ubuntu), update the package lists and upgrade existing packages:

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 3: Download and Install Miniconda

We use Miniconda over the full Anaconda distribution for its **lightweight nature and speed**. It provides the same `conda` environment management without the bloat of 250+ pre-installed packages.

```bash
# 1. Download the latest Miniconda installer for Linux (x86_64)
#    (For ARM64 architectures, replace the link accordingly)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh

# 2. Run the installation script
bash ~/miniconda.sh
```

### Step 4: Follow the Installation Prompts

1.  **License Agreement**: Press and hold **Enter** or the **Spacebar** to scroll through. Type `yes` and press Enter to accept.
2.  **Installation Location**: Press **Enter** to accept the default location (`/home/your_username/miniconda3`).
3.  **Initialization (Critical Step)**: When asked:
    `Do you wish the installer to initialize Miniconda3 by running conda init? [yes|no]`
    **Type `yes` and press Enter.** This automatically configures your shell (`.bashrc`) to recognize `conda` commands.

### Step 5: Activate the Configuration

```bash
# Reload the shell configuration to make conda available immediately
source ~/.bashrc
```

You should now see the `(base)` prefix in your terminal prompt, indicating you are in the base conda environment.

### Step 6: Verify and Optimize

1.  **Verify Installation**:
    ```bash
    conda --version
    ```

2.  **Speed Up Package Downloads (Essential for users outside the US/Europe)**:
    Configure Conda to use a faster mirror, such as the Tsinghua University mirror. This drastically improves download speeds.
    ```bash
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
    conda config --set show_channel_urls yes
    ```

3.  **Update Conda Itself**:
    ```bash
    conda update -n base -c defaults conda -y
    ```

### Step 7: Create Your First Project Environment (Best Practice)

**Golden Rule:** Never use the `base` environment for your projects. Create a dedicated, isolated environment for each project.

```bash
# Create an environment named 'my_project' with Python 3.10
conda create -n my_project python=3.10 -y

# Activate the new environment
conda activate my_project

# (Optional) Install common data science libraries
conda install numpy pandas matplotlib scikit-learn -y
# Or use pip within the conda environment (it's perfectly safe)
# pip install torch torchvision
```

> **Note**: When `my_project` is active, your terminal prompt will change to `(my_project)`.

---

## Part 2: Connecting PyCharm to WSL

This is the most powerful part of the setup. PyCharm Professional has native support for WSL, treating it as a remote interpreter without the complexity of SSH.

### Step 1: Open Your Project from the WSL Filesystem

**Crucial Rule:** You **must** open your project directly from the `\\wsl$` network path. **Do not** store your code on the Windows drive (e.g., `C:\Users\...`) and try to use it from WSL – this leads to severe I/O slowdowns and permission issues.

1.  Launch PyCharm (Professional Edition required for WSL support).
2.  Click **Open**.
3.  In the file explorer, navigate to the **`\\wsl$`** location in the sidebar.
4.  Drill down into your distribution (e.g., `Ubuntu`) -> `home` -> `your_linux_username`.
5.  Select your project folder (or create a new one here).

### Step 2: Configure the Python Interpreter

1.  Once the project is open, go to **`File`** -> **`Settings`** (on Windows) or **`PyCharm`** -> **`Settings`** (on macOS).
2.  Navigate to **`Project: <your_project_name>`** -> **`Python Interpreter`**.
3.  Click the gear icon ⚙️ in the top-right corner and select **`Add`**.
4.  In the left panel, choose **`On WSL`**. PyCharm will automatically detect your installed WSL distributions.
5.  Now, select the interpreter type:
    *   Choose **`Conda Environment`**.
    *   Select **`Existing environment`**.
    *   In the **`Interpreter`** dropdown, PyCharm usually auto-discovers all your conda environments. Look for the one you created (`my_project`). The path should look like:
        `/home/your_username/miniconda3/envs/my_project/bin/python`
    *   If it's not in the list, click the `...` button and manually browse to that path.

### Step 3: Finalize and Verify

1.  Click **`OK`**.
2.  PyCharm will index the remote interpreter. This might take a few minutes for a new environment.
3.  Once done, the Python interpreter in the bottom-right corner of PyCharm should display `my_project`.
4.  **Test it**: Open or create a Python file (e.g., `test.py`), write `print("Hello from WSL!")`, and run it. The output will execute in your WSL environment.
5.  **Check the Terminal**: Open the built-in PyCharm terminal (`View` -> `Tool Windows` -> `Terminal`). You will see that it automatically opens a `bash` session within your WSL distribution and activates your project's conda environment.

---

## Part 3: Best Practices & Troubleshooting

Adhering to these rules will save you countless hours of debugging.

### 1. File Location: The Golden Rule

*   **✅ DO**: Store your project code **inside the WSL filesystem**.
    *   Path in PyCharm: `\\wsl$\Ubuntu\home\username\projects\my_project`
    *   Path in WSL: `/home/username/projects/my_project`
*   **❌ DO NOT**: Store your code on the Windows drive (e.g., `C:\Users\username\projects`) and access it from WSL via `/mnt/c/...`.
    *   **Why**: File I/O through the `/mnt/c/` mount point is **10-50x slower**. This will cause `pip install`, `git` operations, and application startup to feel sluggish or hang. It can also lead to filesystem permission errors, especially with Docker.

### 2. Line Endings (CRLF vs. LF)

Linux uses `LF` (`\n`) for line endings, while Windows uses `CRLF` (`\r\n`). This can cause shell scripts (`.sh`) to fail with errors like `bash^M: bad interpreter`.

*   **Check in PyCharm**: Look at the bottom-right corner of the editor. You should see **`Unix (LF)`**.
*   **Fix**: If you see **`Windows (CRLF)`**, click on it and select **`Unix (LF)`** to convert the file.
*   PyCharm usually handles this automatically for files created within the WSL project.

### 3. GUI Display (WSLg)

On modern Windows 11/10 with WSLg (Windows Subsystem for Linux GUI), plotting libraries like Matplotlib and Seaborn will automatically display their figures in a native Windows window.

*   **Test**: Run `notepad` in your WSL terminal. If it opens a Notepad window on Windows, WSLg is working.
*   **For headless servers or if you don't want pop-ups**: Add the following to your Python scripts to save plots to files instead of displaying them.
    ```python
    import matplotlib
    matplotlib.use('Agg') # Use non-interactive backend
    import matplotlib.pyplot as plt
    # ... your plotting code ...
    plt.savefig('my_plot.png')
    ```

### 4. WSL 2 Memory Management (Performance Tuning)

By default, WSL 2 can consume a large amount of Windows memory for caching, which might slow down your host OS. You can cap its resource usage.

1.  Create a file named **`.wslconfig`** in your **Windows user folder** (`C:\Users\YourWindowsUsername\`).
2.  Add the following configuration to limit memory and swap:
    ```ini
    [wsl2]
    memory=8GB        # Limits WSL 2 to 8GB of RAM (adjust as needed)
    swap=4GB          # Limits swap file size
    localhostForwarding=true
    ```
3.  **Restart WSL** for the changes to take effect:
    ```powershell
    # In PowerShell (Admin) or CMD
    wsl --shutdown
    ```
    Then, restart your WSL terminal or PyCharm.

### 5. Common Pitfalls

*   **"conda: command not found" in a new terminal**: Manually run `source ~/.bashrc` or restart your terminal session.
*   **Permission Denied when accessing files**: Ensure your files are owned by your WSL user (`/home/username/...`). Files on `/mnt/c/` can have complex permission mappings.
*   **PyCharm can't find the interpreter**: Make sure you opened the project via `\\wsl$`, not a Windows path. Go to `File` -> `Settings` -> `Project` -> `Python Interpreter`, and try re-adding it via the `On WSL` option.

---

## Summary Checklist

- [ ] **WSL 2** installed and updated (`wsl --install`, `sudo apt update`).
- [ ] **Miniconda** installed in WSL and initialized.
- [ ] **(Optional) Conda mirror configured** for faster downloads.
- [ ] **Project environment created** (`conda create -n my_project python=3.x -y`).
- [ ] **PyCharm project opened via `\\wsl$`**.
- [ ] **Python Interpreter configured** in PyCharm using the **`On WSL`** option, pointing to your `my_project` conda environment.
- [ ] **Code stored exclusively in the WSL filesystem** (e.g., `/home/username/projects/`).

You are now set up with a professional, high-performance, and isolated Python development environment that leverages the best of both Linux and Windows. Happy coding!