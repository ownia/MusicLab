/*
 * Chord Trigger Script for MIDIPLUS TINY
 */

var noteOn1 = 67;     // G4
var noteOn2 = 60;     // C4
var noteOn3 = 59;     // B3
var triggerKey1 = 65; // F3
var triggerKey2 = 70; // C6

function HandleMIDI(event) {
    // Trigger chord 1: F3 -> G4 + C4
    if (event instanceof NoteOn && event.pitch == triggerKey1) {
        Trace("F3 pressed -> G4 and C4\n");

        var n1 = new NoteOn;
        n1.pitch = noteOn1;
        n1.velocity = event.velocity;
        n1.send();

        var n2 = new NoteOn;
        n2.pitch = noteOn2;
        n2.velocity = event.velocity;
        n2.send();

    } else if (event instanceof NoteOff && event.pitch == triggerKey1) {
        Trace("F3 released -> stop G4 and C4\n");

        var n1 = new NoteOff;
        n1.pitch = noteOn1;
        n1.send();

        var n2 = new NoteOff;
        n2.pitch = noteOn2;
        n2.send();

    // Trigger chord 2: C6 -> G4 + B3
    } else if (event instanceof NoteOn && event.pitch == triggerKey2) {
        Trace("C6 pressed -> G4 and B3\n");

        var n1 = new NoteOn;
        n1.pitch = noteOn1;
        n1.velocity = event.velocity;
        n1.send();

        var n2 = new NoteOn;
        n2.pitch = noteOn3;
        n2.velocity = event.velocity;
        n2.send();

    } else if (event instanceof NoteOff && event.pitch == triggerKey2) {
        Trace("C6 released -> stop G4 and B3\n");

        var n1 = new NoteOff;
        n1.pitch = noteOn1;
        n1.send();

        var n2 = new NoteOff;
        n2.pitch = noteOn3;
        n2.send();

    // Pass through all other MIDI events unchanged
    } else {
        Trace("Pass through");
        event.send();
        event.trace();
    }
}
