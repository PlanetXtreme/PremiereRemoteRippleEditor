READ THIS DOCUMENTATION FROM ORIGINAL FIRST.
https://github.com/sebinside/PremiereRemote

REQUIRED: Place files into starter folder, C:\Program Files\Adobe\Adobe Premiere Pro 2025\CEP\extensions\Your_Extension
REQUIRED: Install NodeJS here https://nodejs.org/en/download
After that, run CMD as administrator, cd to the host directory (C:\Program Files\Adobe\Adobe Premiere Pro 2025\CEP\extensions\Your_Extension\host), do "npm install".
Inside "host" folder, run "REBUILD_NPM_BATCH.bat." Originally it was required to do "NPM run build" after cding into the correct directory, but now you can double click this function and execute this command instantly, and it automatically tries to elevate commands. YOU NEED TO DO THIS TO APPLY ANY EDITS/CODE CHANGES (as described in original documentation).

Bonus of this fork: Inside the Premiere window for PremiereRemote, there is a button labeled "Open AHK Script", which opens the file explorer directory of the extension itself, allowing you to quickly activate the AHK Script when opening Premiere.

///////////////////////////\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

Additionally, this package comes with a few pre-built keybinds in the included AHK script:
1. Automatically changing selected tracks to muted/unmuted (by looking at level of first selected track, is it over/under 0dB, and subsequently forcing all tracks to be -inf or 0dB) [Keybind z, ideally remove that keybind in Premiere's Keybind editor for simplicity]
2. Better ripple delete (puts playhead at the end of the track instead of the beginning) [requires setting keybind in Premiere to Alt+Shift+D]
3. Even faster playback (presses character 's' at end of every successful action - when binded to "Shuttle Right" and other "s" keybind is disabled, allows for faster playback, therefore processing, of footage.)

Finally, this starter project is slightly better than original because it shows you how PremierePro can respond to your inputs (which is described *as possible* by original documentation but not well explained/documented).
AS A DEVELOPER, ONLY EDIT THE "host" folder. That is the only folder you should be editing when working on your own hotkeys/js functions. Inside host/src/index.tsx is the js functions that are linked to the AHK script. Remember, when editing, run the bat file to auto-run 'npm run build.' Then restart Premiere to see the new functions.
Happy scripting!



