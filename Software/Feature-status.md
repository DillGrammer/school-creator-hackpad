# Feature status — September 17, 2026

A function having source code is not equivalent to being validated on the user's computer or hardware.

| Area | Implemented | Remaining verification/work |
|---|---|---|
| Input/menu firmware | Actual state machine, physical pins, debounce, OLED grids, OS selection, global Back, held controls | Flash and test actual XIAO/OLED/encoder; confirm detent divisor |
| Helper setup | GUI, folder pickers, private JSON import, OS key store | Mac dependencies installed and imported successfully; GUI launch requires user action because Terminal is blocked by computer control; Windows installation untested |
| USB protocol | Handshake, bounded queues, duplicate IDs, cancellation, reconnect, OS mismatch rejection | Physical USB testing |
| Courses | Configured URL launch, drafts, screenshot capture, folder picker, rename, username entry; active Safari Word download-and-copy adapter | Word adapter source not yet run end-to-end; Mac Accessibility permission; class folders; Windows Word adapter not implemented |
| Quick Answer | On-demand capture, API request, short OLED answer, explanation log, cancellation | API model/key and real capture tests |
| ChatGPT drafts | Local draft fallback; optional browser fill/attachment without Send | Validate current ChatGPT editor/attachment behavior and login |
| CapCut basic controls | Foreground-checked configurable shortcuts; Mac play/pause, undo, redo, import and export defaults read from CapCut | Test commands on media; Windows shortcuts and advanced controls unverified |
| CapCut volume/trim/text/transition | Dispatcher and configurable bindings | Native app adapter where no shortcut exists; preset selection not implemented |
| Media import | Recent/selected file handling; Mac native picker adapter; selected-original Photos export and separate Open/Import menu | End-to-end helper test for Mac picker and Photos permissions/export; Windows uses manual path fallback |
| Export | Export shortcut and Fitness destination prompt | Set/verify 1080×1920 30 fps settings, execute export, verify completion automatically |
| Upload preparation | Optional file-input attachment; manual fallback; no publish/schedule code | Real video decoding now rejects incomplete files and non-1080×1920/30 fps exports; both real upload editors still require validation |
| Gaming | Launch targets, exact-name installed Windows shortcut discovery, Spotify-specific transport, per-app volume, foreground icon, selected headset capture-endpoint mute | Windows and actual headset tests |
| Case | Revision 1.1 STEP/STL and native Fusion F3D; corrected handedness and knob position; solid and mesh checks | Physical fit check; actual kit dimensions |
| Submission | Sanitized packages; Stardance design project 63122 created with factual description and AI declaration | Public repository, authentic required project evidence, advanced integration work; funding submission remains disabled |

Do not submit this as a fully tested or physically assembled product. Do not invent hours, devlogs, photographs, build evidence or eligibility claims. Generated mockups are not photos of a real build.
