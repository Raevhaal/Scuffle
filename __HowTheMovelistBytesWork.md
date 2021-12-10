# How the movelist works
###### A work in progress
###### Or
###### Documentation for those hoping to parse the Soul Calibur 6 movelist


### Overview
Each character in Soul Calibur comes with a static chunk of memory that serves as the source for many or all values
associated with frame data. Startup, active frames, block stun, etc... For our purposes we'll refer to this block of
static memory as the 'movelist'.
 
As you read this document, you may benefit from following the code MovelistParser.py.

You can also view these bytes with the SCUFFLE move viewer, launchable from the menu (SCUFFLE > Move Viewer) or use
a hex editor to view the movelists in /movelists.

##### Movelist Structure
* A movelist starts with 30 bytes **header**. It always starts with the bytes 'KH11' and then lists a series of useful
addresses, the number of moves, and some useful breakpoints in how the moves are catagorized.
* After the header comes the list of **moves**. Characters have about 3 thousand moves. Each move is 72 bytes and 
consists of an animation to play, various modifiers to that animation (faster, slower, less weapon movement, 
what animation to blend with during transition). In addition there are indexes for all hitboxes associated with the move 
and the address of the move's cancel block (many interesting things happen in the cancel block).
* After the list of moves comes the list of **attacks**. A character has only a few hundred attacks. Each attack is 112 bytes.
Some moves have multiple attacks such as Seong Mina's spear tip moves (one attack for the spear shaft, one for the spear tip).
Each attack has physics properties for various hit states (pushback on block, how high they are launched, etc.), startup 
frames, block/hit/counter stun frames, and other highly relevant frame data variables.
* After the list of moves comes one or multiple short **unknown** blocks.
* The final block and majority of the bytes in the file consist of the list of **cancel blocks**. Each move has one
and exactly one cancel block. The cancel block has no set size and can be zero bytes, ten bytes, or thousands of bytes long. The bytes serve as
a finite state machine or simple interpreted/compiled language. They control, among other things:
    * Move cancels
    * TC/TJ/REV/GI frames
    * Recovery frames
    * Button commands
    * Lethal hit properties
    * Throw/Super sequences (?)
    * Tracking(?)
 

##### What's not in the movelist
* Hitbox location and placement seems to be stored at least partly with the move animation.
* The character's name or other identifier
* Any current state information, the movelist is completely static.


### Header
* 30 bytes
* [00-0B] Constant. String 'KH11' or Int 0x3131484b or Byte Array [4B 48 31 31 00 00 00 00 00 00 00 00]
* [0C-0E] Short int: the total number of moves listed (plus one)
* [0E-0F] Short int: total number of ???, undetermined
* [10-13] Address of where the list of attacks begins
* [14-17] Address of undetermined block (that is, the block's purpose is undetermined, the address is quite clear)
* [18-1B] Address of 2nd undetermined block
* [1C-1D] Always zero, but probably starting index of first grouping of moves
* [1E-1F] Number of moves in the first grouping
* [20-21] Starting index of second grouping of moves (always the same as previous number)
* [22-23] Number of moves in second grouping
* [24-25] Starting index of third group-
* ... And so on, there's four groupings you get the idea
* [2C-2F] Always the same bytes [86 1A 40 00]


### Moves
* 70 bytes
* Animation id
* Various animation modifiers
* Address of cancel block associated with this move
* Up to 6 attack indexes

### Attacks
* 112 bytes
* Physics
* Startup/Active Frames/Block Stun etc.
* Launch type
* Block type (for example force crouching)

### Unknown bytes 1

### Unknown bytes 2
* May have something to do with cinematics?

### Cancel Block
* No fixed length, must be interpreted. Most commands come in sets of 3 bytes although there are occasional 1 byte commands.
* In three byte commands, the first byte is the instruction (MOVE, IF, STORE) while the next two are the arguments.
* Arguments that span two bytes are big endian ([BIG BYTE] [SMALL BYTE]).
* Some instructions take two seperate arguments, one from each byte.

#### Commands
* 01 [xx xx]
  * Begins every cancel block. The arguments denote the 'type' of cancel blocks. Goes up to 00 0a. Most are simply 00 00, but neutral is 
  always 00 08. Characters have the same or similar numbers of 00 02 to 00 0a cancel blocks, so these likely denote universal moves like
  sidestep or soul charge.
* 89 [xx xx] or 8b [xx xx]
  * Used to pass arguments to future instructions.
  * Conceptually these serve as buffers or queues not single registers. Multiple calls can be made.
* 5a [xx] [xx]
  * The first byte is unknown (but only comes in a few specific values)
  * The second byte is the number of instructions (3 byte increments) to go back and read as arguments
  * Seems to evaluate the arguments and write a TRUE/FALSE value.
* 28 [xx xx]
  * Reads the last TRUE/FALSE value written by a 5a instruction.
  * If triggered, it JUMPS to address given by its bytes (relative to the start of the cancel block)
  * So 28 00 5d will skip to the 0x5d byte of the cancel block and continue execution from there if the last 5a instruction was True.
* 25 [xx] [xx]
  * Connects this state with another state using the last [2nd byte] number of instructions
  * One of the instructions is always 8b [xx xx] which defines the state to make a connection to.
  * The first byte denotes the type of connection:
    * 07 : Cancels, the character's move id changes and all execution of this move and block ceases
    * 0d : Appends, the state is evaluated *in addition* to this state. Useful for stances that share commands, as well as conditions
    like crouching or being in soul charge.
    * 14 : ??? seems like a variation on 07
    * 03 : ??? variation on 0d ?
    * 26 : ???
* 2a [xx xx]
  * The same as 28 [xx xx], but switches only on values written by 25 [xx] [xx] instructions.
* 02
  * Denotes the end of the cancel block
* 96/08/... other single bytes
  * Unclear if these are also an end, a return value, or an instruction that doesn't need arguments
* 8a [xx xx]
  * Seems to some kind of replacement for 89 or 8b, unclear exactly how they work.
* 13 [xx xx]
  * Only yoshimitsu has these, no idea.
* 19 [xx] [xx]
  * Similar to 25 [xx] [xx] but different. Tend to be used in the neutral/backturned cancel block where 25 [xx][xx] might otherwise be expected.
  
#### Byte Codes

##### Encoded vs Decoded Move Id's
* A move id is the index of a move in the move list and is used extensively in Cancel Blocks.
* In order to (presumabely?) preserve commonality between characters, move ids are encoded in such a way that many
universal moves will share the same move id between characters.
* In order to do this, the leftmost 4 bits are reserved for the **section** the block is in.
* The header file divides the move indexes into four sections.
* Encoded move ids are stored as **[y][x][xx]** where y is 0, 1, 2, or 3 and denotes one of the 4 move index quadrants and the rest of the bytes
are the offset from the start of that quadrant.
* To get the decoded move id, drop the leftmost bits and add the appropriate offset.

###### Example
0x30CC is the universal encoded move id for 'currently in soul charge'. This indicates it can be found in the 
fourth section with an offset of 0x0CC. For Voldo, his header bytes shows that his fourth section has an offset of 0x98C.
The index of Voldo's soul charge move is 0x0CC + 0x98C. For Xianghua, her header bytes have a fourth block offset of
0x949 so her soul charge move is indexed at 0x0CC + 0x949.

#### Known Patterns
 * 8b [0x3020] 89 [recovery state] 89 [early cancelable frames] 89 [??] 25 [0d 04]
   * Very common pattern located near the beginning of a cancel block.
   * The [recovery state] is usually 00 c8 for standing or 00 c9 for crouching.
   * [early cancelable frames] is the number of frames early an animation can be canceled. Some moves, like throws,
   require the whole animation to play out. Generally this is between 0 and 10 frames although it can be edited to 
   make moves cancelable for their entire duration (setting this number to a value higher than the total frames will force the entire animation to play).

 * 8b [00 06] 8b [xx xx] a5 [xx xx]
   * This condition is checking for a button press. Valid button press codes are 00 01 for A, 00 02 for B, 00 04 for K, and
   00 08 for G. For two or more buttons, the values are added but stored in the right byte, so 03 00 for A+B and 09 00 for A+G.
 
 * 8b [00 20] ...
   * Same as 8b [00 06] except checking for button hold.
   
 * 8b [move id] 89 [xx xx] 89 [xx xx] 25 [07 xx]
   * Signifies a transition to [move id]. The first argument to 89 is the frame we leave this move on, the second argument
   is the frame we enter the next move on.
   
 * 8b [0x30cc] [move id]...
   * Same as above except this is only accessible in soul charge
   
 * 8b [0x305d] [type] [start] [stop] ... 25 0d [xx]
   * TC/TJ/possibly other frames
   * [start] and [stop] are 2(?) frames before state takes effect and ends

 * 8b [0x3064] ...
   * GI frames/armor frames
   * Includes the type of GI (armor/GI), the frames active, either the level (high/low/all) or damage amount 
   absorbed (for armor), some booleans indicating what exactly is GI'd (Horizontal/Vertical/Kick/???).
   
 * 8b 07 d1 ....
   * Plays a voice clip ("You're open!")
  
 * 8b 30 a3 ... [6 or more args]
   * 'Electric' effect for guard breaks. 
   * Includes the frames to show electricity, the type/number of trails to show, and when the 'flash' goes off.
   
 * 
   
 

  
  




