# Qubee AI Demo

This folder contains demo materials for Qubee AI.

## Screenshots

Add screenshots showing:
1. Web interface with input text
2. Corrections being displayed
3. Grammar suggestions
4. Before/After comparison

## Demo GIF

Create an animated GIF showing:
- Typing text with errors
- Clicking "Check Spelling"
- Viewing corrections
- Accepting/rejecting suggestions

## How to Create Demo Materials

### Screenshots
1. Start the server: `python main.py`
2. Open `http://localhost:8082`
3. Type example text: "Ani bishan dhuguu fedh"
4. Click "Check Spelling"
5. Take screenshots at each step

### GIF Recording
Use tools like:
- **Windows**: ScreenToGif
- **Mac**: Kap, Gifox
- **Linux**: Peek, SimpleScreenRecorder

### Example Test Cases

```
Input: Ani bishan dhuguu fedh
Output: ani bishaan dhuguu fedha

Input: Isheen mana deeme
Output: isheen mana deemte

Input: Waaqayo nagaa kenna
Output: Waaqayyo nagaa kenna
```

## File Naming

- `screenshot-01-input.png` - Initial input screen
- `screenshot-02-checking.png` - Processing
- `screenshot-03-results.png` - Results displayed
- `demo.gif` - Animated demonstration
- `before-after.png` - Side-by-side comparison

---

**Note**: Screenshots will be added after UI improvements are complete.
