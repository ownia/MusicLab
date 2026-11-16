#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from typing import Optional

# Add swift-f0 to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'swift-f0'))

from swift_f0 import SwiftF0, segment_notes, export_to_midi, plot_pitch, plot_notes, plot_pitch_and_notes, export_to_csv


def process_audio(
    input_file: str,
    output_basename: Optional[str] = None,
    tempo: int = 120,
    fmin: Optional[float] = None,
    fmax: Optional[float] = None,
    pitch_hold_ms: float = 80.0,
    generate_plots: bool = True,
) -> dict:
    """
    Process an audio file and generate MIDI and LilyPond outputs.
    
    Args:
        input_file: Path to input audio file
        output_basename: Base name for output files (without extension)
        tempo: MIDI tempo in BPM
        fmin: Minimum detection frequency in Hz
        fmax: Maximum detection frequency in Hz
        pitch_hold_ms: Penalty parameter for note segmentation
        generate_plots: Whether to generate visualization plots
    
    Returns:
        Dictionary containing paths to output files
    """
    # Check input file
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Determine output basename
    if output_basename is None:
        output_basename = os.path.splitext(os.path.basename(input_file))[0]
    
    # Get output directory
    output_dir = os.path.dirname(input_file) or '.'
    
    # Output file paths
    midi_path = os.path.join(output_dir, f"{output_basename}.midi")
    lily_path = os.path.join(output_dir, f"{output_basename}.lily")
    csv_path = os.path.join(output_dir, f"{output_basename}_pitch.csv")
    
    output_files = {
        'midi': midi_path,
        'lilypond': lily_path,
        'csv': csv_path,
    }
    
    if generate_plots:
        output_files['pitch_plot'] = os.path.join(output_dir, f"{output_basename}_pitch.jpg")
        output_files['notes_plot'] = os.path.join(output_dir, f"{output_basename}_notes.jpg")
        output_files['combined_plot'] = os.path.join(output_dir, f"{output_basename}_pitch_notes.jpg")
    
    print(f"Processing: {input_file}")
    print(f"Output basename: {output_basename}")
    print()
    
    # Initialize detector
    f0 = SwiftF0()
    
    # Detect pitch
    print("Detecting pitch...")
    detect_kwargs = {}
    if fmin is not None:
        detect_kwargs['fmin'] = fmin
    if fmax is not None:
        detect_kwargs['fmax'] = fmax
    
    result = f0.detect_file(input_file, **detect_kwargs)
    
    print(f"  Duration: {result.timestamps[-1]:.2f}s")
    print(f"  Frames: {len(result.timestamps)}")
    
    # Calculate voiced statistics
    voiced = result.confidence >= 0.5
    if voiced.any():
        mean_f0 = result.pitch_hz[voiced].mean()
        print(f"  Mean F0 (voiced): {mean_f0:.1f} Hz")
    print()
    
    # Export CSV
    print("Exporting pitch data to CSV...")
    export_to_csv(result, csv_path)
    print(f"  Saved: {csv_path}")
    
    # Segment notes
    print("Segmenting notes...")
    notes = segment_notes(result, pitch_hold_ms=pitch_hold_ms)
    print(f"  Found {len(notes)} notes")
    
    if not notes:
        print("Warning: No notes detected. Output files will not be created.")
        return output_files
    
    # Export MIDI
    print("Exporting to MIDI...")
    export_to_midi(notes, midi_path, tempo=tempo)
    print(f"  Saved: {midi_path}")
    
    # Convert MIDI to LilyPond using midi2ly
    print("Converting MIDI to LilyPond using midi2ly...")
    try:
        subprocess.run(
            ['midi2ly', midi_path, '-o', lily_path],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"  Saved: {lily_path}")
    except FileNotFoundError:
        print("  Warning: midi2ly not found. Skipping LilyPond conversion.")
        print("  Install LilyPond to enable this feature.")
    except subprocess.CalledProcessError as e:
        print(f"  Error running midi2ly: {e.stderr}")
    
    # Generate plots
    if generate_plots:
        print("Generating plots...")
        
        plot_pitch(result, show=False, output_path=output_files['pitch_plot'])
        print(f"  Saved: {output_files['pitch_plot']}")
        
        plot_notes(notes, show=False, output_path=output_files['notes_plot'])
        print(f"  Saved: {output_files['notes_plot']}")
        
        plot_pitch_and_notes(result, notes, show=False, output_path=output_files['combined_plot'])
        print(f"  Saved: {output_files['combined_plot']}")
    
    print()
    print("Done!")
    print()
    print("To compile LilyPond to PDF:")
    print(f"  lilypond {lily_path}")
    
    return output_files


def main():
    parser = argparse.ArgumentParser(
        description='Audio to sheet music - Convert audio to MIDI and LilyPond using swift_f0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s audio.wav
  %(prog)s audio.wav output
  %(prog)s audio.wav output --tempo 140
  %(prog)s audio.wav output --fmin 80 --fmax 1000
  %(prog)s audio.wav output --no-plots
        '''
    )
    
    parser.add_argument('input', help='Input audio file')
    parser.add_argument('output', nargs='?', help='Output basename (optional)')
    parser.add_argument('--tempo', type=int, default=120, help='MIDI tempo in BPM (default: 120)')
    parser.add_argument('--fmin', type=float, help='Minimum detection frequency (Hz)')
    parser.add_argument('--fmax', type=float, help='Maximum detection frequency (Hz)')
    parser.add_argument('--pitch-hold-ms', type=float, default=80.0, 
                        help='Note segmentation penalty; higher = fewer, longer notes (default: 80)')
    parser.add_argument('--no-plots', action='store_true', help='Skip plot generation')
    
    args = parser.parse_args()
    
    try:
        process_audio(
            input_file=args.input,
            output_basename=args.output,
            tempo=args.tempo,
            fmin=args.fmin,
            fmax=args.fmax,
            pitch_hold_ms=args.pitch_hold_ms,
            generate_plots=not args.no_plots,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
