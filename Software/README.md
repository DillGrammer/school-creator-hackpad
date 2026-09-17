# Hackpad software — development build

This folder contains actual CircuitPython firmware, a Mac/Windows Python helper, and automated tests. It is **not a hardware-tested release**. Read `Feature-status.md` before relying on advanced actions.

## Install the helper

1. Install Python 3.11 or newer from python.org, including Tk support (the standard python.org installer includes it).
2. On Mac, open `Start-Mac.command`; on Windows open `Start-Windows.cmd`. First launch creates a local environment and installs dependencies from PyPI. Internet access is needed for that installation.
3. In the setup window, use **Import settings** to load your private settings file, or fill the tabs manually. Choose folder locations with **Choose…**. Missing entries disable only their associated actions.
4. Save settings. They stay in your user account's Hackpad application-data folder. Passwords and API keys are not in the firmware or public project.
5. For Quick Answer, set a vision-capable OpenAI API model and enter its key through **Set AI key privately**. The key is stored in the OS credential store. This is a separate API workflow from ChatGPT browser conversations.
6. macOS may request Accessibility/Input Monitoring for keyboard actions and Screen Recording for captures. Only enable the permissions for the Python/helper you choose to run. No permission is bypassed automatically.

If you enable the optional separate helper browser, install its Chromium runtime once with `.venv/bin/python -m playwright install chromium` on Mac, or `.venv\Scripts\python.exe -m playwright install chromium` on Windows. Log in in that separate browser when prompted. Existing browser sessions are not copied. Chat drafts are never sent automatically and video uploads are never published or scheduled.

## Install firmware

1. Download the stable CircuitPython UF2 **for Seeed Studio XIAO RP2040**, not another XIAO board: https://circuitpython.org/board/seeeduino_xiao_rp2040/
2. Enter the board's BOOTSEL mode and copy the UF2 to its boot drive. Wait for `CIRCUITPY` to appear.
3. Copy the contents of `firmware/` to the root of `CIRCUITPY`, including `lib/`, `font5x8.bin`, `engine.py`, `device.json`, `boot.py`, and `code.py`.
4. Reconnect USB. The firmware uses the exact pin map in the PCB project. Default OLED I²C address is 0x3C. In `device.json`, adjust encoder divisor (typically 2 or 4) and direction if one detent is not one menu step. Check the supplied encoder instead of assuming its pulse count.
5. Start the helper and choose Mac or Windows on the OLED. The helper scans common XIAO/CircuitPython USB vendors and confirms a protocol handshake before accepting commands. If needed select the serial port explicitly in Setup.

No UF2 has been flashed here and no physical OLED/input test has been performed. USB endpoint compatibility, memory usage and the downloaded CircuitPython release must be checked on the board. The firmware uses USB serial only; the helper is the single action dispatcher, so HID and helper commands cannot double-fire. It does not act as a standalone keyboard without the helper.

## Controls

- Boot: turn and click to choose Mac/Windows.
- Root pages: turn to Courses, Creator, Gaming (Windows), Apps, or More. Titles are brief; six labels remain visible on normal grids.
- Course and action grids: press the corresponding physical key. Small dialogs use turn-and-click.
- Back: hold bottom-right key, click encoder. The sixth key's ordinary action happens on release only if the combination did not consume it.
- CapCut: knob scrubs; click plays/pauses. Hold Volume or Trim and turn to adjust. Tap Volume enters adjustment; Trim lets you choose start/end. Hold Undo for 0.6 seconds for Redo.
- Gaming: at its root page, turn still changes categories. Click once (or press a gaming key) to enter volume control. After that, rotation controls only the foreground app's audio. Back returns to category rotation. This explicit entry avoids guessing whether a turn means category change or volume.
- Gaming keys: Fortnite / Valorant / Discord / Spotify / Next / Previous. OLED shows foreground-app icon/name, volume, and the selected headset microphone's Windows mute state. Unknown mic state displays `?`. A hardware mute switch needs device-specific verification.

## Configuration and fallbacks

School URLs and conversation URLs remain editable. The supplied Math conversation is reused; screenshots and text are prepared without pressing Send. The default reliable path presents a local draft plus an Open Conversation button and screenshot. Optional browser attachment depends on the actual page having its expected editor/file input; it refuses to overwrite a nonempty draft.

CapCut bindings are intentionally explicit in Setup. Enter comma-separated key names, such as `command,z` for an actual verified Mac Undo binding. Each action checks that CapCut is foreground before injecting keys. There are no assumed bindings for volume, trimming or presets; if the installed application does not expose a suitable shortcut, that operation needs a native accessibility adapter and currently reports missing configuration. Do not invent key combinations to make a control appear complete.

Import Recent identifies a stable recent supported file. On Mac, the native import adapter enters the path and checks the selected filename before pressing Import; this adapter still needs an end-to-end helper test. Windows currently copies the path for manual selection.

For Photos on Mac, choose Import → Photos → Open Photos, select one photo or video in Photos, then choose Import chosen on the pad. The helper exports that selected original into its retained imported-media folder, opens CapCut and requests import. macOS Automation permission for Photos is required. The Photos adapter is implemented against the installed Photos scripting dictionary but has not been integration-tested. Live Photos that export both a still and a video require choosing the desired exported file with Selected. Do not delete retained imported media while a CapCut project references it. Windows uses Selected instead.

Export opens the configured dialog, showing the configured Fitness destination; it does not yet verify/apply export settings or detect completion automatically. Set the completed output in Setup before Prepare Upload.

On Windows, an empty app path triggers discovery of exact-name Fortnite, VALORANT, Discord, Spotify or CapCut shortcuts in the user/shared Start Menus and Desktop. A configured path takes precedence. Missing shortcuts still require choosing the app in Setup; discovery has automated filesystem tests but has not been tried on the user's gaming PC.

## Tests

Run `python3 -m unittest discover -s tests -v` from this folder. Tests cover state transitions, held-key consumption, grid dimensions, framebuffer rendering, and non-overwriting copies. They do not prove hardware timing, platform permissions, application UI behavior or physical fit.

## Dependencies

OLED libraries/font come from the official Adafruit repositories; licenses are under `firmware/licenses/`. Dependency hashes are recorded in the packaged manifest. The desktop requirements are in `helper/requirements.txt`. Runtime credentials, browser profiles, screenshots and private settings must never be committed to the public repository.


### Active Word document → class folder

The course Copy key now targets the Word document being edited in the active Safari tab on Mac. It uses Word’s File → Create a Copy → Download a copy command, waits for a new complete DOCX matching that document’s title, and copies it without overwriting existing class files. The original online document stays open. Set each class folder in Setup. Safari must download automatically into Downloads, or set `word_downloads_folder` to its actual destination; Ask for each download requires manual intervention. The helper needs Mac Accessibility permission. English Word control labels were inspected in Safari; the helper’s native adapter itself still requires an end-to-end runtime test. Windows support for this action is not implemented.


### Validation update

The Mac dependency installation and import checks pass, including Tk after installing the missing Homebrew Tk component. The setup window itself has not been launched through computer control because that tool blocks Terminal. Startup now tracks the requirements file and retries dependency installation after failures or changes. Mac CapCut defaults were read from its Shortcuts window: Space, Command-Z, Command-Shift-Z, Command-I, Command-E. Advanced commands remain unconfigured. Upload preparation locally decodes the complete selected video, requires 1080×1920 at approximately 30 fps, checks that the file did not change, and stops on cancellation before attachment. It never publishes.
