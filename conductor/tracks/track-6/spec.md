# Specification: Manual Override & Shadow Mode

## Overview
The system must be collaborative. If a human touches a control, the AI must yield. While in manual mode, the AI enters "Shadow Mode" to record State-Action pairs for future learning.

## Requirements
1.  **Control Authority Toggle:**
    -   Implement a `ControlAuthority` flag in C#.
    -   Any manual parameter change (e.g., from a future UI/MIDI) must set `ControlAuthority = Human`.
2.  **Shadow Mode Logging:**
    -   In Python, if `ControlAuthority == Human`, start logging (Feature Vector, Action Vector) to SQLite.
3.  **Automatic yield:**
    -   The AI should only regain control after a period of manual inactivity or an explicit "AI Takeover" command.
4.  **Action Vector:**
    -   Define an action vector: `[CompressionRatio, Width, EQ_Low, EQ_Mid, EQ_High]`.

## Success Criteria
- [ ] Manual changes instantly override AI intents.
- [ ] Python detects manual mode and starts high-frequency logging.
- [ ] SQLite database contains valid State-Action pairs.
