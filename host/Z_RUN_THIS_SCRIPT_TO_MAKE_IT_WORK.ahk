#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%

; Force script to run as administrator (may be required)
if not A_IsAdmin
{
    Run *RunAs "%A_ScriptFullPath%"
    ExitApp
}

~z:: ;sample function without returns. Either mutes or unmutes audio tracks (find the function in host/src/index.tsx)
    ;TrayTip, Audio Swap, Checking selection and toggling mute..., 2000
    Run, "C:\Windows\System32\curl.exe" "http://localhost:8081/swapAudioTracksVolume", %A_ScriptDir%, Hide
return

~x:: ; goes to end of last selected clip, ideally mutes everything.
    ; TrayTip, Audio Swap, toggling mute and going to end of last selected clip, 2000
    ; Step 1: Go to Last Clip End and WAIT for confirmation
    whr_jump := ComObjCreate("WinHttp.WinHttpRequest.5.1")
    whr_jump.Open("GET", "http://localhost:8081/goToLastClipEnd", false)
    whr_jump.Send()
    jumpResponse := whr_jump.ResponseText
    whr_jump := "" ; Release the COM object

    if InStr(jumpResponse, "complete")
    {
        Send, {Space} ;can be ran at same time as unmuted/muting command
        Run, "C:\Windows\System32\curl.exe" "http://localhost:8081/swapAudioTracksVolume", %A_ScriptDir%, Hide
	Send, {s}
        ;TrayTip, Action Success, Audio clip should be muted and jump should have occurred, 2000
    }
    else if InStr(jumpResponse, "no_clips")
    {
        TrayTip, Action Canceled, No clips were selected to navigate to., 2000
    }
    else
    {
        TrayTip, Script Error, Could not move playhead to clip end., 2000
    }
return

+d::  ; Shift+D
    ; immediately pause playback (this forces the timeline responsiveness to be quicker)
    Send, {Space} ; can improve performance in some cases by stopping playback during multi-actions
                                                                                                                    ; Step 1: Check the selection and capture the result
    whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")
    whr.Open("GET", "http://localhost:8081/checkSelectionForRipple", false)
    whr.Send()
    responseString := whr.ResponseText
    whr := "" ; Release the COM object
                                                                                                                    
    if InStr(responseString, "multiple_clips")                                                                      ; Case 1: Multiple clips were selected
    {
        ;TrayTip, Multi-Clip Action, Creating marker and waiting for confirmation..., 2000

        ; Create marker and wait for Premiere Pro to reply.
        whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")
        whr.Open("GET", "http://localhost:8081/createMarkerOnLastClip", false)
        whr.Send()
        markerResponse := whr.ResponseText
        whr := "" ; Release the COM object

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
            whr_jump := "" ; Release the COM object

            if InStr(jumpResponse, "complete") ; Check if Premiere Pro confirmed that the jump and delete was successful
            {
                ;TrayTip, Multi-Clip Action, Successfully jumped to last marker and deleted it in multi-clip ripple!, 2000
                Sleep, 100
                Send, {Space}
		Send, {s}
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
	Send, {s}
        ;TrayTip, Single-Clip Action, Succesfully Performed simple ripple-delete., 2000
    }
    else                                                                                                            ; Case 3: Zero clips were selected, or an error occurred
    {
        Send, {Space} ;start playback again
	Send, {s}
        TrayTip, Action Canceled, No video clips were selected., 2000
    }
return
