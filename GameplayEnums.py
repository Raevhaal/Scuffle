from enum import Enum


class MoveState(Enum):
    neutral = 0
    crouching = 1
    downed_supine = 2  # face up
    downed_prone = 3  # face down
    hit_or_guard = 4
    starting_attack = 5
    guard_stand = 6
    guard_crouch = 7

    crouch_rising = 10
    guard_stand_start = 11
    guard_stand_release = 12
    guard_stand_to_crouch = 13
    guard_fast_duck_then_sidestep = 14 #looks like a duck and sidestep happens only on extremly fast step and guard
    guard_crouch_and_start_guarding = 15
    guard_crouch_start = 16
    guard_crouch_release = 17
    guard_release_and_stand = 18 #releasing guard at the same time as standing?
    guard_crouch_to_stand = 19
    guard_lying_to_stand = 20  # ???
    jump_up = 21
    jump_forward = 22
    jump_back = 23
    forwardstep_start = 24
    forwardstep_middle = 25
    forwardstep_walk = 26
    forwardstep_medium_stop = 27
    forwardstep_big_stop = 28
    forwardstep_bigger_stop = 29
    forwardstep_running_stop = 30
    running_unknown_31 = 31 #only accessible if running in another 8way direction first?
    running_unknown_32 = 32

    backstep_start = 33
    backstep_middle = 34
    backstep_backwalk = 35
    backstep_medium_stop = 36
    backstep_big_stop = 37


    backright_start = 39
    backright_start_middle = 40
    backright_start_sidewalk = 41
    backright_start_medium_stop = 42
    backright_start_big_stop = 43

    sidestep_right_start = 45
    sidestep_right_middle = 46
    sidestep_right_sidewalk = 47
    sidestep_right_medium_stop = 48
    sidestep_right_big_stop = 49

    forward_right_start = 51
    forward_right_middle = 52
    forward_right_sidewalk = 53
    forward_right_medium_stop = 54
    forward_right_big_stop = 55

    #59, 61, 44, and 38 are all backwalk weird states

    sidestep_left_start = 63  # all sidesteps start with this
    sidestep_left_middle = 64  # only the smallest sidesteps don't have this
    sidestep_left_sidewalk = 65  # you can get 8 way run moves without this
    sidestep_left_medium_stop = 66  # requires a 64 but not a 65
    sidestep_left_big_stop = 67  # only for 65 steps?

    forward_left_start = 69
    forward_left_middle = 70
    forward_left_sidewalk = 71
    forward_left_medium_stop = 72
    forward_left_big_stop = 73


    forwardstep_short_stop = 75
    forwardleft_short_stop = 76
    forwardright_short_stop = 77
    sidestep_left_short_stop = 78
    sidestep_right_short_stop = 79
    backstep_short_stop = 80
    backleft_short_stop = 81
    backright_short_stop = 82
    move_animation_playing = 83
    move_animation_playing_crouching = 84  # ??? not tech crouches, but actually crouching state? flags on forced crouched?

    move_animation_forward_throw = 86
    move_animation_back_throw = 87
    move_animation_airborne = 88  # true for juggles but also aerial attacks?
    move_finished = 89
    move_finished_crouching = 90 #????
    recovering_forward_throw = 91
    recovering_back_throw = 92
    recovering_from_heavy_block = 93  # occurs on guard breaks but also tira's gloomy 66k

    standing_to_supine = 97
    standing_to_prone = 98
    backturned_to_facing = 106 #hold towards opponent from backturn
    backturned_step_right = 107 #directions on these two moves are switched since we're backturned
    backturned_step_left = 108

    guard_turn_left = 109 #happens when you guard after backturn
    guard_turn_right = 110 #may not be guard only?
    downed_supine_to_standing = 113
    downed_prone_to_standing = 114
    downed_prone_to_standing_backturned = 115




class HitLevel(Enum):
    high_49 = 0x49
    high_6d = 0x6D #tira 4K


    mid_4b = 0x4b #common #doesn't hit grounded (if a ground hitting move has this, check second hitbox?)
    mid_24 = 0x24  # hits grounded
    mid_6f = 0x6f  # crouching mid?

    low_37 = 0x37 #common #hits grounded
    low_13 = 0x13 #crouching low? #doesn't hit grounded
    low_7 = 0x07 #unblockable #nightmare's charged stomp

    sm_5b = 0x5b
    sm_7f = 0x7F  # soul charge activation, also ivy backturned B+K

    sl_1b = 0x1b
    sl_31 = 0x1f
    sl_63 = 0x63

    throw = 0x81 #most throws
    throw_ast = 0xC1 #astaroth throws
    throw_mid = 0x82 #mids

    UB_mid_43 = 0x43 #maybe only at end?
    UB_mid_67 = 0x67  # maybe only at end?
    UB_mid_47 = 0x47

    UB_high_41 = 0x41
    UB_high_63 = 0x63 #from editing move list



class LaunchType(Enum):

    none = 0x0
    STN = 0x01
    LNC = 0x02
    KND = 0x03
    THROW = 0xAA




class HitEffect(Enum):
    #Not launches (frame data displayed correctly)
    hit_00 = 0x0 #(cinematic incoming??)
    hit_01 = 0x1 #no sell flinch right
    hit_05 = 0x5
    hit_09 = 0x9 #slight bend right
    hit_0d = 0xd
    hit_11 = 0x11 #jab right flinch
    hit_15 = 0x15 #jab left flinch
    hit_17 = 0x17
    hit_19 = 0x19 #very slight whiplash
    hit_1d = 0x1d #whiplash flinch
    hit_21 = 0x21 #flinch back
    hit_25 = 0x25 #= flinch back (most standard hit???)
    hit_2b = 0x2b #slight lift flinch
    hit_2c = 0x2c #fencing(?)
    hit_30 = 0x30 #fencing stagger
    hit_36 = 0x36 #stagger back hands out (c'mon) (other default hit state)
    hit_3a = 0x3a #similar to 0x36?
    hit_3e = 0x3e
    hit_46 = 0x46
    hit_4a = 0x4a
    hit_4e = 0x4e
    hit_52 = 0x52 #flinch left in place
    hit_56 = 0x56
    hit_5a = 0x5a
    hit_5e = 0x5e #very slight flinch right
    hit_62 = 0x62 #the slightest of up flinches
    hit_66 = 0x66 #stagger/turn to the right
    hit_6a = 0x6a #stagger/turn to the left
    hit_6e = 0x6e
    hit_6f = 0x6f
    hit_72 = 0x72 #(throw animation? geralt throat slash?)
    hit_74 = 0x74
    hit_7e = 0x7e
    hit_82 = 0x82
    hit_86 = 0x86
    hit_8a = 0x8a #spinning (ends front)
    hit_8e = 0x8e #= grab left shoulder
    hit_92 = 0x92
    hit_96 = 0x96 #look down
    hit_9a = 0x9a #crouching flinch
    hit_9e = 0x9e #flinch down
    hit_a2 = 0xa2 #crouch flinch
    hit_a6 = 0xa6 #crouch flinch
    hit_aa = 0xaa  # = reversal edge/flinch forward
    hit_ae = 0xae
    hit_b2 = 0xb2 #head nod down flinch
    hit_b6 = 0xb6
    hit_be = 0xbe #kneeling flinch
    hit_ba = 0xbe
    hit_c2 = 0xc2
    hit_c6 = 0xc6 #slight stagger back (first hit into 0x36)
    hit_ca = 0xca #looking up
    hit_ce = 0xce #looking up flinch
    hit_d2 = 0xd2
    hit_d6 = 0xd6
    hit_d7 = 0xd7
    hit_da = 0xda #= ??
    hit_de = 0xde #flinch up
    hit_e2 = 0xe2 #stomach lift
    hit_e6 = 0xe6
    hit_ea = 0xea #slight jerk back
    hit_ed = 0xed
    hit_ee = 0xee #jerk back
    hit_f1 = 0xf1
    hit_f2 = 0xf2 #rapid flinches???
    hit_f4 = 0xf4 #flinch foward (hip thrust)
    hit_f6 = 0xf6 #same as f4??
    hit_f7 = 0xf7
    hit_f8 = 0xf8
    hit_fa = 0xfa
    hit_fe = 0xfe #double over stomach grab
    hit_ff = 0xff


    #frame data displays correctly for these as well, despite have animations or hex number kinda like launchers
    hit_102 = 0x102 #4 step stagger back stomach grab
    hit_103 = 0x103 #stagger left
    hit_104 = 0x104 #stagger right (no backward movement)
    hit_106 = 0x106 #knock on butt (stays fairly close)
    hit_10a = 0x10a #soul charge (long pull)
    hit_10e = 0x10e #slow pull, roll to feet (WS)
    hit_11e = 0x11e #flinch left trip
    hit_126 = 0x126 #(trip flinch as well??)
    hit_12e = 0x12e #right leg lift flinch
    hit_132 = 0x132 #leg lift flinch
    hit_142 = 0x142 #right leg lift flinch (again)
    hit_14a = 0x14a #grab leg
    hit_14e = 0x14e #leg lift off balance flinch
    hit_15e = 0x15e #= trip flinch
    hit_16e = 0x16e #kneeling/prayer flinch
    hit_16f = 0x16f #hands on the ground flinch
    hit_172 = 0x172 #crouch flinch??? used in rapid succession combos
    hit_177 = 0x177 #legs knocked out to left
    hit_178 = 0x178 #knock to all fours

    hit_2e1 = 0x2e1 #electric writhe (see 0x2de, but frame data accurate???)

    hit_30a = 0x30a #= spinning electric stun
    hit_332 = 0x332 #electric kneel
    hit_362 = 0x362 #knocked on butt stun
    hit_36e = 0x36e #stomach grab stun (no knockdown)


    #Launches, knockdowns, or crumples. Frame data here is often wrong


    #hit_16e = 0x16e #(?) facing down simple launch #????
    hit_116 = 0x116 #1.5 spin pull
    hit_182 = 0x182 #shorter pull (?)
    hit_186 = 0x186 #ice skater spin pull
    hit_18a = 0x18a #ice skater spin to the right + pull
    hit_18e = 0x18e  # ice skater spin left, pull
    hit_1ba = 0x1ba #(1 flip long pull, face down)(sometimes not that long?)
    hit_1bb = 0x1bb #pull left and flip (WS to the side)
    hit_1bc = 0x1bc #pull right and flip
    hit_1b6 = 0x1b6 #ground smash, legs forward, head back
    hit_1c6 = 0x1c6 #smash into ground
    hit_1d6 = 0x1d6 #ground slam back first
    hit_1de = 0x1de #rock sliding pull
    hit_1e6 = 0x1e6 #rocket launch (straight up, straight down)


    hit_226 = 0x226 #(ground bounce launch no spin face up)
    hit_229 = 0x229 #(no spin launch/face down)
    hit_237 = 0x237 #(simple launch)
    hit_23b = 0x23b #same as 0x237?? (wall spalts)
    hit_23c = 0x23c #(2 rotation launch) (does not wall splat for some moves, others ws to left, finicky)
    hit_23d = 0x23d #1.5 end over end spin, lands on side
    hit_23e = 0x23e #end over end lands on shoulder
    hit_240 = 0x240 #(3? rotation launch, seems high)
    hit_245 = 0x245 #multiple reverse spins
    hit_246 = 0x246 #1 spin hi pull
    hit_249 = 0x249 #set up launch
    hit_252 = 0x252 #ift/medium short pull
    hit_256 = 0x256 #lifted back, momentum completes roll onto face
    hit_258 = 0x258  # slung right

    hit_26a = 0x26A #(pulled back launch)
    hit_26e = 0x26E #(same as 26a?)
    hit_26f = 0x26F #ice skater spin to left + pull
    hit_286 = 0x286 #half spin land on head launch
    hit_28e = 0x28e #similar to 286?
    hit_296 = 0x296 #similar to 0x286???
    hit_29a = 0x29a #similar to 0x286???
    hit_2aa = 0x2aa #side spin land on head launch
    hit_2a6 = 0x2a6 # same as 2aa????
    hit_2ae = 0x2ae #face plant feet go back and out

    hit_2ba = 0x2ba #(?) slow fall back to butt (crumple??)
    hit_2ca = 0x2ca #slow fall forward knees first
    hit_2da = 0x2da #falling back crumple (c'mon stance)
    hit_2d2 = 0x2d2 #falling forward crumple
    hit_2de = 0x2de #electric writhe

    hit_2e2 = 0x2e2 #spin around fall back(forward) crumple
    hit_31a = 0x31a  # crumple fall right
    hit_326 = 0x326 #turn around and crumple landing face down
    hit_336 = 0x336 #falling back crumple (crouching stance)
    hit_33e = 0x33e #crumple kneel fall forward
    hit_342 = 0x342 #electric crumple
    hit_346 = 0x346 #launch crumple
    hit_34a = 0x34a #knocked up and back crumple forward
    hit_34e = 0x34e #smash knockdown crumple
    hit_35e = 0x35e #go limp crumple



    hit_37a = 0x37a #stomach grab crumple forward
    hit_38a = 0x38a #concussed crumple fall back
    hit_392 = 0x392 #twisting side fall right
    hit_39e = 0x39e #back and forth stun/crumple

    #for throws only
    hit_3a3 = 0x3a3 #throw(?)



    #untested
    hit_100 = 0x100
    hit_105 = 0x105

    hit_107 = 0x107
    hit_108 = 0x108
    hit_109 = 0x109
    hit_10d = 0x10d

    hit_112 = 0x112
    hit_11a = 0x11a
    #...


CRUMPLES = [
            HitEffect.hit_2ba, HitEffect.hit_2da, HitEffect.hit_2d2, HitEffect.hit_2de, HitEffect.hit_2e2, HitEffect.hit_2ca,
            HitEffect.hit_31a, HitEffect.hit_326, HitEffect.hit_336, HitEffect.hit_33e, HitEffect.hit_342, HitEffect.hit_346, HitEffect.hit_34a, HitEffect.hit_34e,
            HitEffect.hit_38a, HitEffect.hit_392, HitEffect.hit_39e]

KNOCKDOWNS = [HitEffect.hit_116, HitEffect.hit_182, HitEffect.hit_186, HitEffect.hit_18a, HitEffect.hit_18e,
              HitEffect.hit_1b6, HitEffect.hit_1ba, HitEffect.hit_1bb, HitEffect.hit_1bc, HitEffect.hit_1c6, HitEffect.hit_1de, HitEffect.hit_1d6, HitEffect.hit_1e6,
              ]

LAUNCHES = [HitEffect.hit_226, HitEffect.hit_229, HitEffect.hit_237, HitEffect.hit_23b, HitEffect.hit_23c, HitEffect.hit_23d, HitEffect.hit_23e,
            HitEffect.hit_240, HitEffect.hit_245, HitEffect.hit_246, HitEffect.hit_249, HitEffect.hit_252, HitEffect.hit_256, HitEffect.hit_258, HitEffect.hit_26a, HitEffect.hit_26e, HitEffect.hit_26f,
            HitEffect.hit_286, HitEffect.hit_28e, HitEffect.hit_296, HitEffect.hit_29a, HitEffect.hit_2a6, HitEffect.hit_2aa, HitEffect.hit_2ae]


EXCEPTIONS = [HitEffect.hit_2e1.value, HitEffect.hit_30a.value, HitEffect.hit_332.value, HitEffect.hit_362.value, HitEffect.hit_36e.value]

def HitEffectToLaunchType(he):
    if he == HitEffect.hit_3a3.value:
        return 'THROW'
        #return LaunchType.THROW

    if he in EXCEPTIONS:
        return ''
    if he >= 0x2ba:
        return LaunchType.STN.name
    if he >= 0x200:
        return LaunchType.LNC.name #todo 0x116 might be a reverse exception here?
    if he >= 0x180:
        return LaunchType.KND.name

    return ''


def ReadInputDirectionCode(code):
    is_f = ((code & 0x04) > 0)
    is_b = ((code & 0x08) > 0)
    is_d = ((code & 0x10) > 0)
    is_u = ((code & 0x20) > 0)

    if is_f and is_u:
        return 9
    if is_f and is_d:
        return 3
    if is_b and is_d:
        return 1
    if is_b and is_u:
        return 7
    if is_u:
        return 8
    if is_f:
        return 6
    if is_d:
        return 2
    if is_b:
        return 4
    return ' '


def ReadInputButtonCode(code):
    is_a = ((code & 0x01) > 0)
    is_b = ((code & 0x02) > 0)
    is_k = ((code & 0x04) > 0)
    is_g = ((code & 0x08) > 0)

    if not is_a and not is_b and not is_k and not is_g:
        return ' '

    return '{:01x}'.format(code)







