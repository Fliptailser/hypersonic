import mido

def add_beat(structs, time, message, length, args):
    is_downbeat = args
    
    beats = structs['beats']
    
    beat_length = length / 960.

    if is_downbeat:
        beats.append((1, time, beat_length))
    else:
        beats.append((beats[-1][0] + 1, time, beat_length))
        
            
def add_bomb(structs, time, message, length, args):
    lane = args
    targets = structs['targets']
    
    targets.append(('bomb', lane, time, length))
    
def add_tap(structs, time, message, length, args):
    lane = args
    targets = structs['targets']
    
    targets.append(('tap', lane, time, None))
    
def add_hold(structs, time, message, length, args):
    lane = args
    targets = structs['targets']
    
    targets.append(('hold', lane, time, length))

'''
    The key for getting game objects from MIDI notes.
    
'''
MIDI_KEY = {
    48: (add_beat, True),
    51: (add_beat, False),
    
    68: (add_tap, 'top'),
    67: (add_hold, 'top'),
    66: (add_bomb, 'top'),
    
    65: (add_tap, 'mid'),
    64: (add_hold, 'mid'),
    63: (add_bomb, 'mid'),
    
    62: (add_tap, 'bot'),
    61: (add_hold, 'bot'),
    60: (add_bomb, 'bot')
}
       

       
'''
    Parses a MIDI file and creates the appropriate game elements for it.

    Input: The name for the song being played. TODO: specifics. For example, "Song 2 by Blur" might have the name Blur_Song2. These'll probably end up mapped on a dict when we have a selection menu.
    Output: {'targets' : [...], 'signals' : [...], 'beats' : [...], 'tempo' : [...]}
'''
def parse_MIDI_chart(song_name):
    mid = mido.MidiFile('../tracks/' + song_name + '.mid')

    structs = {'targets' : [], 'signals' : [], 'beats' : [], 'tempo' : []}
    
    # Get tempo data and create data for tempo mapping
    t = 0
    ticks = 0
    ticks_per_beat = 960
    sec_per_beat = 0
    for message in mid.tracks[0]:
        ticks += message.time
        # sec = ticks / (ticks per beat) * (seconds per beat)
        t += 1.0 * message.time / ticks_per_beat * sec_per_beat
        if message.type == 'set_tempo':
            # (sec/beat) =  (microseconds/beat) / (microseconds/sec)
            sec_per_beat = 1.0 * message.tempo / 1000000
            structs['tempo'].append((t, ticks))
                
    ticks = 0
    # Read MIDI notes
    open_messages = {}
    for message in mid.tracks[1]:
        ticks += message.time
        if not isinstance(message, mido.MetaMessage) and message.note in MIDI_KEY:
            if message.type == 'note_on':
                # save the message & time until we find the note_off
                open_messages[message.note] = (message, ticks)
            elif message.type == 'note_off':
                # process the finished MIDI note
                callback, args = MIDI_KEY[message.note]
                on_message, on_time = open_messages[message.note]
                callback(structs, on_time, on_message, ticks - on_time, args)
                del open_messages[message.note]
    
    # cap off the tempo map (extrapolate to the end of the track using the final tempo)
    last_point = structs['tempo'][-1]
    d_ticks = ticks - last_point[1]
    structs['tempo'].append((last_point[0] + d_ticks / ticks_per_beat * sec_per_beat, ticks))
    
    return structs