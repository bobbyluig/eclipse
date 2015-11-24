# Moves servo in a sine wave between 1 and 2 ms.
begin
    60 64 68 71 74 77 79 80 80 79 78 76 73 70 66 62
    58 54 50 47 44 42 41 40 40 41 43 46 49 52 56
    all_frames
repeat

sub all_frames
    begin
        depth
    while
        100 times
        0 servo
        100 delay
    repeat
    return