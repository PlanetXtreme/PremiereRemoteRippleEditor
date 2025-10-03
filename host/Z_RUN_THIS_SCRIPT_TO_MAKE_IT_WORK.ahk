#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%

; Force script to run as administrator (may be required)
if not A_IsAdmin
{
    Run *RunAs "%A_ScriptFullPath%"
    ExitApp
}

; z:: ; "Z" or "z" ;replaced by better mute/unmute function, but this still works just by replacing the other "z" keybind
;     ; mutes audio
;     Run, "C:\Windows\System32\curl.exe" "http://localhost:8081/muteSelectedAudioTracks", %A_ScriptDir%, Hide
;     ; TrayTip, Hotkey Triggered, z pressed - audio track muted!, 2000
; return 
; 
; x:: ; "X" or "x"
;     ; unmutes audio
;     Run, "C:\Windows\System32\curl.exe" "http://localhost:8081/unmuteAudioTracks", %A_ScriptDir%, Hide
;     ; TrayTip, Hotkey Triggered, x pressed - audio track UNmuted!, 2000
; return 

z:: ;sample function without returns. Either mutes or unmutes audio tracks (find the function in host/src/index.tsx)
    TrayTip, Audio Swap, Checking selection and toggling mute..., 2000
    Run, "C:\Windows\System32\curl.exe" "http://localhost:8081/swapAudioTracksVolume", %A_ScriptDir%, Hide
return

+d::  ; Shift+D
    ; immediately pause playback (this forces the timeline responsiveness to be quicker)
    Send, {Space} ; can improve performance in some cases by stopping playback during multi-actions
                                                                                                                    ; Step 1: Check the selection and capture the result
    ; responseString := ComObjCreate("WScript.Shell").Exec("curl ""http://localhost:8081/checkSelectionForRipple""").StdOut.ReadAll() ;this way does not run headless. The following 4 lines are a headless fix
    whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")
    whr.Open("GET", "http://localhost:8081/checkSelectionForRipple", false)
    whr.Send()
    responseString := whr.ResponseText
                                                                                                                    
    if InStr(responseString, "multiple_clips")                                                                      ; Case 1: Multiple clips were selected
    {
        ;TrayTip, Multi-Clip Action, Creating marker and waiting for confirmation..., 2000

        ; Create marker and wait for Premiere Pro to reply.
        whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")
        whr.Open("GET", "http://localhost:8081/createMarkerOnLastClip", false)
        whr.Send()
        markerResponse := whr.ResponseText

        ; Only proceed if Premiere Pro reported back "complete"
        if InStr(markerResponse, "complete")
        {
            Send, !+d ;forces ripple delete action (custom keybind)
            Sleep, 200 ; A small, blind sleep is still wise here to let the UI process the major delete action.

            ; Playhead to last placed marker - waits for response from Premiere.
            whr_jump := ComObjCreate("WinHttp.WinHttpRequest.5.1")
            whr_jump.Open("GET", "http://localhost:8081/goToLastMarkerAndDelete", false)
            whr_jump.Send()
            jumpResponse := whr_jump.ResponseText

            if InStr(jumpResponse, "complete") ; Check if Premiere Pro confirmed that the jump and delete was successful
            {
                TrayTip, Multi-Clip Action, Successfully jumped to last marker and deleted it in multi-clip ripple!, 2000
                Sleep, 100
                Send, {Space}
            }
            else
            {
                TrayTip, Script Error, Could not find the marker after the ripple delete., 2000
            }
        }
        else
        {
            TrayTip, Action Canceled, Premiere failed to create the necessary marker., 2000
        }
    }
    else if InStr(responseString, "one_clip")                                                                       ; Case 2: Exactly one clip was selected
    { ; Only do ripple delete
        Send, !+d
        Sleep, 200 ;probably good to have a delay here
        Send, {Space}
        TrayTip, Single-Clip Action, Succesfully Performed simple ripple-delete., 2000
    }
    else                                                                                                            ; Case 3: Zero clips were selected, or an error occurred
    {
        Send, {Space} ;start playback again
        TrayTip, Action Canceled, No video clips were selected., 2000
    }
return
