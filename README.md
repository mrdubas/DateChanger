## DateChanger
![Capture](https://github.com/user-attachments/assets/5347582a-0720-4aa8-9315-bfe39f47cb7f)

A lightweight Windows utility built with PyQt5 that lets you **copy** or **manually set** file creation and modification timestamps via a simple drag-and-drop GUI.

---

### Features

- **Drag & Drop**  
  Drag a file into the first field to get timestamps
  Drag a file into the second field to apply or edited timestamps to that file

- **Manual Date/Time Editing**  
  Two date-time pickers allow you to tweak the “Created” and “Modified” times before applying

- **Field-specific Reset**  
  Click the ⭯ button next to either date-time picker to reset only that field to the current system date/time

- **Clear All & Reset**  
  Click Clear to remove all file paths, reset both date-time pickers to now, and return the app to its initial state

- **Always-On-Top Toggle**  
  Use the “Always on top” option in the window menu to keep the app above all other windows
  ![Capture2](https://github.com/user-attachments/assets/0e94dbc6-f518-4f80-a2b2-ff1dfa3bd918)

### How It Works
![Timeline](https://github.com/user-attachments/assets/ac24b8d8-3304-4eaf-a8bc-ffb3f3e0cf6d)

### Run from Source & Build Executable
- **Run from Source**  
  If you prefer to work with the raw `DateChanger.pyw` script instead of a pre-built executable, first install the required dependencies:  
  ```cmd
  pip install PyQt5 win32_setctime
- **Build Executable**  
  Or to create your own Windows `DateChanger.exe`, simply run the bundled build script: `build.bat`
