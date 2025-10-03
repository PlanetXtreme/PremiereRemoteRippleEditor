

/**
 * ALL functions defined here are visible via the localhost service.
 */
export const host = {
  /**
   * @swagger
   *
   * /kill:
   *      get:
   *          description: This method is only there for debugging purposes.
   *                       For more information, please have a look at the index.js file.
   */
  kill: function () { },

  /**
   * @swagger
   * /yourNewFunction?param1={param1}&param2={param2}:
   *      get:
   *          description: Your new function, ready to be called!
   *          parameters:
   *              - name: param1
   *                description: Just a sample parameter
   *                in: path
   *                type: string
   *              - name: param2
   *                description: Just another sample parameter
   *                in: path
   *                type: string
   */
  //createAlert: function (param1, param2) {
  //  alert(param1 + " " + param2);
  //},

    checkSelectionForRipple: function () {
        var sequence = app.project.activeSequence;
        if (sequence) {
            var selectedVideoClips = [];
            // Only counts video clips (best-case if video clips have multiple connected audio tracks)
            for (var i = 0; i < sequence.videoTracks.numTracks; i++) {
                var track = sequence.videoTracks[i];
                for (var j = 0; j < track.clips.numItems; j++) {
                    var clip = track.clips[j];
                    if (clip.isSelected()) {
                        selectedVideoClips.push(clip);
                    }
                }
            }

            var videoClipCount = selectedVideoClips.length;
            if (videoClipCount === 0) {
                return 'zero_clips'

            } else if (videoClipCount === 1) {
                //var theClip = selectedVideoClips[0];
                //var marker = sequence.markers.createMarker(theClip.start.seconds);
                //marker.name = "AHK_RIPPLE_MARKER";
                return 'one_clip'

            } else {
                // Find the rightmost clip
                var rightmostClip = selectedVideoClips[0];
                for (var k = 1; k < selectedVideoClips.length; k++) {
                    if (selectedVideoClips[k].start.seconds > rightmostClip.start.seconds) {
                        rightmostClip = selectedVideoClips[k];
                    }
                }
                //var marker = sequence.markers.createMarker(rightmostClip.start.seconds);
                //marker.name = "AHK_RIPPLE_MARKER";
                return 'multiple_clips'
            }
        }
        return 'no_sequence'
    },

createMarkerOnLastClip: function () {
        var sequence = app.project.activeSequence;
        function gatherSelectedClips(tracks) {
            for (var i = 0; i < tracks.numTracks; i++) { for (var j = 0; j < tracks[i].clips.numItems; j++) { var clip = tracks[i].clips[j]; if (clip.isSelected()) { selectedClips.push(clip); } } }
        }
        if (sequence) {
            var selectedClips = [];
            gatherSelectedClips(sequence.videoTracks);
            gatherSelectedClips(sequence.audioTracks);

            if (selectedClips.length > 0) {
                var rightmostClip = selectedClips[0];
                for (var k = 1; k < selectedClips.length; k++) {
                    if (selectedClips[k].start.seconds > rightmostClip.start.seconds) {
                        rightmostClip = selectedClips[k];
                    }
                }
                var marker = sequence.markers.createMarker(rightmostClip.start.seconds);
                marker.name = "AHK_RIPPLE_MARKER";
                return "complete"; 
            } 
        }
        // If anything failed (no sequence, no clips), return an error.
        return "failed";
    },

    goToLastMarkerAndDelete_NonResponse: function() {
        var sequence = app.project.activeSequence;
        if (sequence) {
            var markers = sequence.markers;
            var marker = markers.getFirstMarker();
            while (marker !== undefined) {
                if (marker.name == "AHK_RIPPLE_MARKER") {
                    var markerTime = marker.start.ticks;
                    sequence.setPlayerPosition(markerTime);
                    markers.deleteMarker(marker);
                    break; 
                }
                marker = markers.getNextMarker(marker);
            }
        }
    },
goToLastMarkerAndDelete: function() {
        var sequence = app.project.activeSequence;
        if (sequence) {
            var markers = sequence.markers;
            var marker = markers.getFirstMarker();
            var foundMarker = false;

            while (marker !== undefined) {
                if (marker.name == "AHK_RIPPLE_MARKER") {
                    var markerTime = marker.start.ticks;
                    sequence.setPlayerPosition(markerTime);
                    markers.deleteMarker(marker);
                    
                    foundMarker = true;
                    break; 
                }
                marker = markers.getNextMarker(marker);
            }

            if (foundMarker) {
                return "complete";
            } else {
                return "failed";
            }
        }
        return "failed"; // No sequence found
    },

    deleteLastMarker: function() {
        var sequence = app.project.activeSequence;
        if (sequence) {
            var markers = sequence.markers;
            var marker = markers.getFirstMarker();
            while (marker !== undefined) {
                if (marker.name == "AHK_RIPPLE_MARKER") {
                    //var markerTime = marker.start.ticks;
                    //sequence.setPlayerPosition(markerTime);
                    markers.deleteMarker(marker);
                    break; 
                }
                marker = markers.getNextMarker(marker);
            }
        }

    },
    muteSelectedAudioTracks: function () {
        var showAlerts = false;
        if (showAlerts) { alert("DEBUG-0: Starting muteSelectedAudioTracks function."); }

        var sequence = app.project.activeSequence;
        if (sequence) {
            var foundASelectedClip = false;

            for (var i = 0; i < sequence.audioTracks.numTracks; i++) {
                var track = sequence.audioTracks[i];
                for (var j = 0; j < track.clips.numItems; j++) {
                    var clip = track.clips[j];

                    if (clip.isSelected()) {
                        foundASelectedClip = true;
                        if (showAlerts) { alert("DEBUG-1: Found selected clip: '" + clip.name + "'."); }
                        
                        var foundTheComponent = false;

                        for (var k = 0; k < clip.components.numItems; k++) {
                            var component = clip.components[k];
                            
                            if (component.matchName === "Internal Volume Stereo") {
                                foundTheComponent = true;
                                if (showAlerts) { alert("DEBUG-2: Found 'Internal Volume Stereo' component."); }
                                
                                component.enabled = true; 
                                var foundTheLevel = false;

                                for (var l = 0; l < component.properties.numItems; l++) {
                                    var property = component.properties[l];
                                    
                                    if (property.displayName === "Level") {
                                        foundTheLevel = true;
                                        if (showAlerts) { alert("DEBUG-3: Found 'Level' property. Setting value directly."); }
                                        
                                        property.setValue(-287, true); //mutes
                                        
                                        if (showAlerts) { alert("SUCCESS! The audio level for '" + clip.name + "' has been muted."); }
                                        break; 
                                    }
                                }
                                if (!foundTheLevel && showAlerts) {
                                     alert("FAILURE: Did NOT find a property named 'Level'.");
                                }
                                break; 
                            }
                        }
                        if (!foundTheComponent && showAlerts) {
                            alert("FAILURE: Did NOT find a component with matchName 'Internal Volume Stereo'.");
                        }
                    }
                }
            }
            if (!foundASelectedClip && showAlerts) {
                alert("INFO: Script finished, but no clips were selected.");
            } else if (showAlerts) {
                alert("DEBUG-FINAL: Script has finished processing all selected clips.");
            }
        } else {
            if (showAlerts) { alert("FAILURE: Could not find an active sequence."); }
        }
    },
    unmuteAudioTracks: function () {
        var showAlerts = false;
        if (showAlerts) { alert("DEBUG-0: Starting unmuteAudioTracks function."); }
        var sequence = app.project.activeSequence;
        if (sequence) {
            var foundASelectedClip = false;

            for (var i = 0; i < sequence.audioTracks.numTracks; i++) {
                var track = sequence.audioTracks[i];
                for (var j = 0; j < track.clips.numItems; j++) {
                    var clip = track.clips[j];

                    if (clip.isSelected()) {
                        foundASelectedClip = true;
                        if (showAlerts) { alert("DEBUG-1: Found selected clip: '" + clip.name + "'."); }
                        var foundTheComponent = false;

                        for (var k = 0; k < clip.components.numItems; k++) {
                            var component = clip.components[k];
                            
                            if (component.matchName === "Internal Volume Stereo") {
                                foundTheComponent = true;
                                if (showAlerts) { alert("DEBUG-2: Found 'Internal Volume Stereo' component."); }
                                
                                component.enabled = true; 
                                var foundTheLevel = false;

                                for (var l = 0; l < component.properties.numItems; l++) {
                                    var property = component.properties[l];
                                    
                                    if (property.displayName === "Level") {
                                        foundTheLevel = true;
                                        if (showAlerts) { alert("DEBUG-3: Found 'Level' property. Setting value to 0 dB."); }
                                        
                                        // setting to 1 is 15dB, not 0dB
                                        property.setValue(0.1778279393114, true); // 0.1778279393114 is neutral, level 0dB+- for audio
                                        
                                        if (showAlerts) { alert("SUCCESS! The audio level for '" + clip.name + "' has been reset to 0 dB."); }
                                        break; 
                                    }
                                }
                                if (!foundTheLevel && showAlerts) {
                                     alert("FAILURE: Did NOT find a property named 'Level'.");
                                }
                                break; 
                            }
                        }
                        if (!foundTheComponent && showAlerts) {
                            alert("FAILURE: Did NOT find a component with matchName 'Internal Volume Stereo'.");
                        }
                    }
                }
            }
            if (!foundASelectedClip && showAlerts) {
                alert("INFO: Script finished, but no clips were selected.");
            } else if (showAlerts) {
                alert("DEBUG-FINAL: Script has finished processing all selected clips.");
            }
        } else {
            if (showAlerts) { alert("FAILURE: Could not find an active sequence."); }
        }
    },
    getAudioLevelValue: function () { //useful function to call for help
        var sequence = app.project.activeSequence;
        if (sequence) {
            var clipFound = false;
            for (var i = 0; i < sequence.audioTracks.numTracks; i++) {
                var track = sequence.audioTracks[i];
                for (var j = 0; j < track.clips.numItems; j++) {
                    var clip = track.clips[j];

                    if (clip.isSelected()) {
                        clipFound = true;
                        for (var k = 0; k < clip.components.numItems; k++) {
                            var component = clip.components[k];

                            if (component.matchName === "Internal Volume Stereo") {
                                for (var l = 0; l < component.properties.numItems; l++) {
                                    var property = component.properties[l];
                                    
                                    if (property.displayName === "Level") {
                                        var currentValue = property.getValue();
                                        alert("The internal script value for the current audio level is:\n\n" + currentValue);
                                        return; 
                                    }
                                }
                            }
                        }
                    }
                }
            }
            if (!clipFound) {
                alert("Please select a single audio clip that you have manually set to 0.0 dB and run again.");
            }
        }
    },
    goToLastSelectedClip: function () {
        var sequence = app.project.activeSequence;
        function gatherSelectedClips(tracks) {
                for (var i = 0; i < tracks.numTracks; i++) {
                    for (var j = 0; j < tracks[i].clips.numItems; j++) {
                        var clip = tracks[i].clips[j];
                        if (clip.isSelected()) {
                            selectedClips.push(clip);
                        }
                    }
                }
            }
        if (sequence) {
            var selectedClips = [];

            gatherSelectedClips(sequence.videoTracks);
            gatherSelectedClips(sequence.audioTracks);

            // If there are any clips still selected...
            if (selectedClips.length > 0) {
                // Find the one that is now furthest to the right.
                var rightmostClip = selectedClips[0];
                for (var k = 1; k < selectedClips.length; k++) {
                    if (selectedClips[k].start.seconds > rightmostClip.start.seconds) {
                        rightmostClip = selectedClips[k];
                    }
                }
                
                // Move the playhead directly to that clip's new start time.
                // No markers needed.
                sequence.setPlayerPosition(rightmostClip.start.ticks);
            } 
        }
    },
    swapAudioTracksVolume: function () {
        var neutralVolumeValue = 0.1778279393114; // The "arbitrary" value for 0.0 dB
        var muteVolumeValue = 0;                   // The value for silence (-infinity dB)
        var muteThreshold = 0.16;                  // threshold to determine if a clip is "unmuted"

        var sequence = app.project.activeSequence;
        if (sequence) {
            
            // Gather ALL selected audio clips
            var allSelectedClips = [];
            for (var i = 0; i < sequence.audioTracks.numTracks; i++) {
                var track = sequence.audioTracks[i];
                for (var j = 0; j < track.clips.numItems; j++) {
                    var clip = track.clips[j];
                    if (clip.isSelected()) {
                        allSelectedClips.push(clip);
                    }
                }
            }
            if (allSelectedClips.length === 0) {
                return;
            }

            // Inspect the FIRST selected clip
            var referenceClip = allSelectedClips[0];
            var referenceLevel = muteVolumeValue; // Default to "muted"
            
            for (var k = 0; k < referenceClip.components.numItems; k++) {
                var component = referenceClip.components[k];
                if (component.matchName === "Internal Volume Stereo") {
                    for (var l = 0; l < component.properties.numItems; l++) {
                        var property = component.properties[l];
                        if (property.displayName === "Level") {
                            referenceLevel = property.getValue(); // Get its current audio level
                            break;
                        }
                    }
                    break;
                }
            }

            // Decide what our target audio level should be
            var targetValue;
            if (referenceLevel > muteThreshold) {
                // If the reference clip is "unmuted", our goal is to mute everything.
                targetValue = muteVolumeValue;
            } else {
                // If the reference clip is "muted", our goal is to unmute everything.
                targetValue = neutralVolumeValue;
            }

            // Apply the decision to ALL selected clips
            for (var i = 0; i < allSelectedClips.length; i++) {
                var clipToModify = allSelectedClips[i];
                for (var k = 0; k < clipToModify.components.numItems; k++) {
                    var component = clipToModify.components[k];
                    if (component.matchName === "Internal Volume Stereo") {
                        component.enabled = true;
                        for (var l = 0; l < component.properties.numItems; l++) {
                            var property = component.properties[l];
                            if (property.displayName === "Level") {
                                // Set the level to our determined target value.
                                property.setValue(targetValue, true);
                                break;
                            }
                        }
                        break;
                    }
                }
            }
        }
    },
//include more functions here maaaun





};

// THE BELOW function(s) are only used internally. DEVELOPERS, DO NOT EDIT THESE.
export const framework = {
  enableQualityEngineering: function () {
    app.enableQE();
  }
};
