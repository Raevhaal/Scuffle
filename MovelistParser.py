
'''
see HowTheMovelistBytesWork.md for a full description of how the movelist is parsed
'''


import struct
from MovelistEnums import *
import GameplayEnums
import copy

def b4i (bytes, index : int):
    return struct.unpack('I', bytes[index: index + 4])[0]

def b2i (bytes, index : int , big_endian = False):
    if not big_endian:
        return struct.unpack('H', bytes[index: index + 2])[0]
    else:
        return struct.unpack('>H', bytes[index: index + 2])[0]

def b1i (bytes, index : int):
    return struct.unpack('B', bytes[index: index + 1])[0]

def b4f (bytes, index : int):
    return struct.unpack('f', bytes[index: index + 4])[0]

def encode_move_id(decoded_move_id, movelist):
    move_id = decoded_move_id
    if move_id > movelist.block_T_start:  # this is kinda an escape value for stances??? and neutral???
        move_id -= movelist.block_T_start
        move_id += 0x3000
    elif move_id > movelist.block_S_start:
        move_id -= movelist.block_S_start
        move_id += 0x2000
    elif move_id > movelist.block_R_start:
        move_id -= movelist.block_R_start
        move_id += 0x1000
    return move_id

def decode_move_id(encoded_move_id, movelist):
    move_id = encoded_move_id
    if move_id >= 0x3000:  # this is kinda an escape value for stances??? and neutral???
        move_id -= 0x3000
        move_id += movelist.block_T_start
    elif move_id >= 0x2000:
        move_id -= 0x2000
        move_id += movelist.block_S_start
    elif move_id >= 0x1000:
        move_id -= 0x1000
        move_id += movelist.block_R_start
    return move_id

class FrameData:
    def __init__(self, id, com, t, startup, block_stun, hit_launch, hit_stun, counter_launch, counter_stun, damage, attack_type, active_frames, recovery, delta, extra_info):
        self.id = id
        self.com = com
        self.whiff = t
        self.imp = startup
        self.bstun = block_stun
        self.hlaunch = hit_launch
        self.hstun = hit_stun
        self.claunch = counter_launch
        self.cstun = counter_stun
        self.dam = damage
        self.attack_type = attack_type
        self.active = active_frames
        self.rec = recovery
        self.delta = delta
        self.notes = extra_info

    def __repr__(self):
        id = self.id
        cl = self.claunch
        c = self.cstun
        hl = self.hlaunch
        h = self.hstun
        b = self.bstun

        rec = self.rec
        com = self.com
        s = self.imp
        at = self.attack_type
        d = self.dam
        act = self.active
        t = self.whiff
        tf = self.notes

        if cl == hl and c == h:
            cl = ''
            c = ''
        else:
            c = FrameData.StringifyAdvantage(rec - c)


        gap = 0
        if self.delta != 0:
            gap = self.imp + self.delta - 1

        #str = "{:^3}|{:^7}|{:^4}|{:^2}|{:^7}|{:^7}|{:^7}|{:^4}|{:^4}|{:^1}|{:^4}|{}".format(id, '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12')
        str = "{:^3}|{:^7}|{:^4}|{:^2}|{:^5}|{:^7}|{:^7}|{:^2}|{:^4}|{:^1}|{:^3}|{:^3}|{:^3}|{}".format(
            id,
            com[-7:],
            s,
            at,
            '{}'.format(FrameData.StringifyAdvantage(rec - b)),
            '{} {}'.format(hl, FrameData.StringifyAdvantage(rec - h)),
            '{} {}'.format(cl, c),
            d,
            '[gd]',#'{:^4}',
            act,
            t,
            rec - 1,
            gap,
            ' '.join(tf),
        )
        return str

    def StringifyAdvantage(f : int):
        flipped = f * -1
        if flipped >= 0:
            return '+{}'.format(flipped)
        else:
            return '{}'.format(flipped)

class Move:
    LENGTH = 0x48
    def __init__(self, bytes, movelist, move_id):
        self.movelist = movelist
        self.move_id = move_id

        self.bytes = bytes
        self.modified_bytes = None

        self.animation = b4i(bytes, 0x00)
        self.unknown_04 = b4i(bytes, 0x04)
        self.motion_multiplier = b4f(bytes, 0x08)
        self.speed_multiplier = b4f(bytes, 0x0C)
        self.unknown_10 = b4i(bytes, 0x10)

        self.unknown_multiplier = b4i(bytes, 0x30)
        self.total_frames = b2i(bytes, 0x34)
        self.cancel_address = b4i(bytes, 0x38)

        self.attack_indexes = []
        count = 0
        while count < 6:
            attack_index = b2i(bytes, 0x3C + 2 * count)
            if attack_index == 0xFFFF:
                break
            else:
                self.attack_indexes.append(attack_index)
            count += 1

    def get_modified_bytes(self):
        if self.modified_bytes == None:
            return self.bytes
        else:
            return self.modified_bytes

    def set_cancel(self, cancel):
        self.cancel = cancel

    def set_attacks(self, attacks):
        self.attacks = attacks

    def get_weight_to_move_id(self, move_id):
        link = self.cancel.get_link_to_move_id(move_id)
        if link == None:
            return None, None
        else:
            is_block_stun_applied = False

            cancel_weight = link.weight
            if len(self.attacks) > 0:
                startup = self.attacks[0].startup
            else:
                startup = 0
            if link.leave_on > startup:
                cancel_weight -= startup
                is_block_stun_applied = True
            return cancel_weight, is_block_stun_applied

    def get_no_hitbox_startup(self):
        startup = self.cancel.get_fastest_exit(self.total_frames)
        return startup

    def get_frame_data(self, delta = 0):
        data = []

        cf = self.cancel.get_cancelable_frames()

        tf = self.cancel.get_technical_frames()

        for attack in self.attacks:
            if attack.physics_grounded[0] > 0:
                tf.append('GRND')
                break

        for a in self.attacks:
            startup = a.startup
            t = self.total_frames - cf
            recovery = t - startup


            block_stun = a.block_stun
            hit_stun = a.hit_stun
            counter_stun = a.counter_stun

            cl = a.counter_launch
            #c = recovery - counter_stun

            attack_type = a.hit_level
            try:
                attack_type = GameplayEnums.HitLevel(attack_type).name
            except Exception as e:
                pass

            active_frames = a.active - a.startup + 1

            com = self.movelist.get_command_by_move_id(self.move_id)

            data.append(FrameData(self.move_id, com, t, startup + 1, block_stun, a.hit_launch, a.hit_stun, cl, counter_stun, a.damage, attack_type, active_frames, recovery, delta, tf))
        return data

    def get_gui_guide(self):
        guide = [
            (0x00, 0x04, b4i, "animation id"),
            (0x04, 0x08, b4i, "???"),
            (0x08, 0x0c, b4f, "weapon(?) motion(?) multiplier"),
            (0x0c, 0x10, b4f, "animation speed multiplier (no change in total frames)"),

            (0x10, 0x14, b4i, "transition/blending animation"),
            (0x14, 0x16, b2i, "???"),
            (0x16, 0x18, b2i, "???"),
            (0x18, 0x1c, b4f, "?float?transition?"),
            (0x1c, 0x20, b4f, "?float?transition?"),
            (0x20, 0x24, b4i, "???"),
            (0x24, 0x28, b4i, "???"),
            (0x28, 0x2C, b4i, "???"),
            (0x2C, 0x30, b4i, "???"),

            (0x30, 0x34, b4f, "move speed multiplier (multiplies total frames)"),
            (0x34, 0x36, b2i, "total animation frames"),
            (0x36, 0x38, b2i, "???"),
            (0x38, 0x3C, lambda x, y: '{:04x}'.format(b4i(x, y)), "address of cancel information"),

            (0x3C, 0x3E, b2i, "hitbox 1 index"),
            (0x3E, 0x40, b2i, "hitbox 2 index"),
            (0x40, 0x42, b2i, "hitbox 3 index"),
            (0x42, 0x44, b2i, "hitbox 4 index"),
            (0x44, 0x46, b2i, "hitbox 5 index"),
            (0x46, 0x48, b2i, "hitbox 6 index"),
        ]
        return self.bytes, guide


class Attack:
    LENGTH = 0x70
    def __init__(self, bytes):
        self.bytes = bytes
        self.modified_bytes = None

        self.hitbox = b2i(self.bytes, 0) #hitbox limb?? 40 40 = right leg? 80 80 = left leg ??
        self.mystery_02 = b2i(self.bytes, 2) #Counter({128: 125, 0: 43, 17: 21, 2560: 18, 1: 14, 6144: 11, 2048: 10, 512: 10, 2: 9, 6784: 8, 51: 8, 4096: 6, 162: 4, 4608: 4, 34: 4, 513: 4, 640: 3, 641: 3, 3: 2, 129: 2, 3072: 1, 2099: 1})

        #physics is stored as 6 bytes; or 3 2 byte pairs(?) [magnitude, left/right vector, up/down/back/forward vector]
        #somewhat unclear how the number maps to a direction
        self.physics_hit_normal = (b2i(self.bytes, 0x08), b2i(self.bytes, 0x0a), b2i(self.bytes, 0x0c))

        self.physics_hit_launch = (b2i(self.bytes, 0x0e), b2i(self.bytes, 0x10), b2i(self.bytes, 0x12))

        self.physics_counter_normal = (b2i(self.bytes, 0x14), b2i(self.bytes, 0x16), b2i(self.bytes, 0x18))

        self.physics_counter_launch = (b2i(self.bytes, 0x1a), b2i(self.bytes, 0x1c), b2i(self.bytes, 0x1e))

        self.physics_airborne = (b2i(self.bytes, 0x20), b2i(self.bytes, 0x22), b2i(self.bytes, 0x24))

        self.physics_block = (b2i(self.bytes, 0x26), b2i(self.bytes, 0x28), b2i(self.bytes, 0x2a))

        self.physics_grounded = (b2i(self.bytes, 0x2c), b2i(self.bytes, 0x2e), b2i(self.bytes, 0x30))

        self.hit_level = b1i(self.bytes, 0x32)
        #0x33?
        self.strange_guard = b2i(self.bytes, 0x34) #this number is 0, 1, 2, 4, 8, or 16 (for tira). Changing it can change if it can cause guard crushes as well as influence the guard damage
        self.startup = b2i(self.bytes, 0x36)
        self.active = b2i(self.bytes, 0x38) #usually 1 or 2 higher than startup, possible when active frames end?
        self.damage = b2i(self.bytes, 0x3A)


        self.block_stun = b2i(self.bytes, 0x44)
        self.hit_stun = b2i(self.bytes, 0x46)
        self.counter_stun = b2i(self.bytes, 0x48)

        self.b2 = b2i(self.bytes, 0x4A) #for all but maybe 5 moves (for Tira), these values are the exact same as the stun value,
        self.h2 = b2i(self.bytes, 0x4C)
        self.c2 = b2i(self.bytes, 0x4E)

        self.hit_effect = b2i(self.bytes, 0x50) #this may be two sepearate 1 byte enums
        self.hit_launch = GameplayEnums.HitEffectToLaunchType(self.hit_effect)

        self.counter_effect = b2i(self.bytes, 0x52)
        self.counter_launch = GameplayEnums.HitEffectToLaunchType(self.counter_effect)

        self.mystery_54 = b1i(self.bytes, 0x54) #Counter({0: 172, 17: 74, 5: 23, 12: 8, 18: 8, 11: 7, 29: 6, 8: 3, 32: 2, 33: 2, 24: 2, 35: 1, 9: 1, 41: 1, 30: 1})
        self.mystery_55 = b1i(self.bytes, 0x55) #Always 4

        self.block_effect = b1i(self.bytes, 0x56)  #CE forces crouching     #Counter({214: 57, 184: 32, 218: 25, 202: 22, 200: 14, 179: 13, 206: 12, 167: 12, 169: 11, 170: 10, 173: 10, 226: 8, 185: 7, 233: 6, 174: 6, 181: 6, 248: 5, 188: 5, 208: 4, 209: 4, 223: 4, 232: 4, 203: 3, 222: 3, 228: 3, 183: 3, 251: 3, 194: 2, 195: 2, 201: 2, 216: 2, 220: 2, 221: 2, 224: 2, 207: 1, 225: 1, 239: 1, 186: 1, 189: 1})
        self.mystery_57 = b1i(self.bytes, 0x57) #Always 3

        self.mystery_58 = b1i(self.bytes, 0x58) #almost always the same as 0x56, 20 or so differences, just frame guard effect perhaps???

        self.mystery_5A = b2i(self.bytes, 0x5A) #changes guard damage, 0 is 0, 0x0002 makes guard damage 512 # Counter({65533: 225, 0: 31, 2: 14, 40: 12, 20: 5, 6: 4, 80: 4, 8: 4, 10: 3, 120: 3, 50: 2, 9: 1, 15: 1, 25: 1, 9999: 1})

        self.mystery_5C = b2i(self.bytes, 0x5C) #Counter({0: 257, 32: 32, 40: 12, 1: 8, 33: 1, 41: 1})

        self.strange_guard2 = b2i(self.bytes, 0x5E) #Another, possibly primary, guard crush determiner, but not the sole one?

        self.mystery_60 = b2i(self.bytes, 0x60) #always the same as 0x5e, possibly another just guard??? see 0x58

        self.mystery_62 = b2i(self.bytes, 0x62) #????

        self.mystery_64 = b2i(self.bytes, 0x64)  # ????

        self.mystery_66 = b2i(self.bytes, 0x66)  # ????

        self.ffff_1 = b4i(self.bytes, 0x68)  # ????
        self.ffff_2 = b4i(self.bytes, 0x6C)  # ????

    def get_modified_bytes(self):
        if self.modified_bytes == None:
            return self.bytes
        else:
            return self.modified_bytes

    def get_gui_guide(self):
        guide = [
            (0x00, 0x02, b2i, "???"),
            (0x02, 0x04, b2i, "hitbox width/hitbox... height(?)"),

            (0x04, 0x08, b2i, "???"),

            (0x08, 0x0e, b2i, "physics on hit (pushback) [magnitude ; left|right ; up|down|forward|back]"),
            (0x0e, 0x14, b2i, "physics on hit (launch distance)"),
            (0x14, 0x1a, b2i, "physics on counter (pushback?)"),
            (0x1a, 0x20, b2i, "physics on counter (launch?)"),
            (0x20, 0x26, b2i, "physics on airborne"),
            (0x26, 0x2c, b2i, "physics on block "),
            (0x2c, 0x32, b2i, "physics on grounded"),



            (0x32, 0x33, b1i, "hit level (high/low/unblockable/etc.)"),
            (0x33, 0x34, b1i, "???"),
            (0x34, 0x36, b2i, "hit spark type (contributes to guard damage)"),
            (0x36, 0x38, b2i, "begin active frames (startup)"),
            (0x38, 0x3A, b2i, "end active frames"),
            (0x3A, 0x3C, b2i, "damage"),

            (0x3C, 0x40, b4i, "???"),
            (0x40, 0x44, b4i, "???"),
            (0x44, 0x46, b2i, "frames of block stun"),
            (0x46, 0x48, b2i, "frames of hit stun"),
            (0x48, 0x4a, b2i, "frames of counterhit stun"),
            (0x4a, 0x4c, b2i, "???"),
            (0x4c, 0x4e, b2i, "???"),

            (0x4e, 0x50, b2i, "???"),
            (0x50, 0x52, b2i, "hit effect (type of launch/crouching recovery/etc.)"),
            (0x52, 0x54, b2i, "counter effect"),
            (0x54, 0x56, b2i, "block effect"),
            (0x56, 0x58, b2i, "???"),
            (0x58, 0x5a, b2i, "???"),
            (0x5a, 0x5c, b2i, "guard damage override (otherwise uses hit spark size and type calc)"),
            (0x5c, 0x5e, b2i, "???"),
            (0x5e, 0x60, b2i, "guard damage contributor"),
            (0x60, 0x62, b2i, "???"),

            (0x62, 0x64, b2i, "hit spark size (contributes to guard damage)"),
            (0x64, 0x66, b2i, "???"),

            (0x66, 0x68, b2i, "???"),
            (0x68, 0x6c, b2i, "???"),
            (0x6c, 0x70, b2i, "???"),
        ]
        return self.bytes, guide



class Cancel:
    def __init__(self, movelist, bytes, address, move_id):
        self.movelist = movelist
        self.address = address
        self.bytes = bytes
        self.modified_bytes = None
        if len(self.bytes) >= 3:
            self.type = int(self.bytes[2])
        else:
            self.type = -1
        self.move_id = move_id
        self.links = Movelist.links_from_bytes(self, self.movelist)

    def get_modified_bytes(self):
        if self.modified_bytes == None:
            return self.bytes
        else:
            return self.modified_bytes

    def condense_all_shortcuts(self):
        extra_links = []
        for link in self.links:
            if link.is_shortcut:
                extra_links.append((link, self.movelist.move_ids_to_cancels[link.move_id].links))
                #TODO: replace 8a arguments with passed in arguments from original link?

        for shortcut_link, link_list in extra_links:
            for link in link_list:
                copy_link = copy.copy(link)
                copy_link.leave_on = shortcut_link.leave_on
                copy_link.enter_in = shortcut_link.enter_in
                self.links.append(copy_link)
                #if self.move_id == 424:
                    #print(link)


    def update_goto_instructions(self, new_bytes, old_bytes):
        diff = len(new_bytes) - len(old_bytes)
        i = 0
        first_index = -1
        while i < len(new_bytes) and i < len(old_bytes):
            if new_bytes[i] != old_bytes[i]:
                first_index = i
                break
            i += 1


        if first_index == -1 or diff == 0:
            return new_bytes
        else:
            updated_bytes = b''
            z = 0
            while z < len(new_bytes):
                inst = new_bytes[z]
                try:
                    inst = CC(inst)
                except:
                    pass

                if not inst in Movelist.THREE_BYTE_INSTRUCTIONS:
                    updated_bytes += new_bytes[z:z+1]
                    z += 1
                else:
                    if not inst in [CC.PEN_28, CC.PEN_29, CC.PEN_2A]:
                        updated_bytes += new_bytes[z:z+3]
                        z += 3
                    else:
                        updated_bytes += new_bytes[z:z+1]
                        goto = b2i(new_bytes, z + 1, big_endian=True)
                        if goto > first_index:
                            goto += diff
                        updated_bytes += goto.to_bytes(2, byteorder='big')
                        z += 3
            return updated_bytes


    def get_link_to_move_id(self, move_id):
        for link in self.links:
            if link.move_id == move_id:
                return link
        return None

    def get_fastest_exit(self, total_frames):
        exit = total_frames - self.get_cancelable_frames()
        for link in self.links:
            if link.is_to_attack_or_stance(self.movelist):
                if link.leave_on < exit:
                    exit = link.leave_on
        return exit

    def has_at_least_one_button_press(self):
        for link in self.links:
            if link.is_button_press():
                return True
        return False

    def get_last_call_address_index(bytes): #hypothesis: this is the GOTO address for when the move reaches it's totoal frames (maybe?) usually the last 0-3 lines
        try:
            split = bytes.split(b'\x8b\x00\x09\xa5\x01\x01\x96\x28')[1]
            final_address_index = b2i(split, 0, big_endian=True)
            return final_address_index
        except:
            return len(bytes) - 1

    def get_cancelable_frames(self): #the number of frames 'early' the move can be canceled
        try:
            right_split = self.bytes.split(b'\x8b\x30\x20')[1]
            cancelable_frames = int(right_split[5]) #usually this is something like 89 00 c9 89 00 0a where we want the 0a
        except:
            #print('Unable to find cancelable frames for move {}'.format(self.move_id))
            cancelable_frames = 0

        return cancelable_frames

    def get_basic_condition_by_index(self, target_index):
        CONDITION_BREAKS = [CC.START, CC.PEN_2A, CC.PEN_28, CC.PEN_29, CC.EXE_19, CC.EXE_25, CC.EXE_13,]
        condition = Condition(None, 0, len(self.bytes))
        index = 0
        condition_start = 0
        while index < len(self.bytes):
            try:
                inst = CC(self.bytes[index])
            except:
                inst = self.bytes[index]

            if not inst in Movelist.THREE_BYTE_INSTRUCTIONS:
                index += 1
            elif not inst in [CC.PEN_2A, CC.PEN_29, CC.PEN_28]:
                index += 3
            else:
                dest = b2i(self.bytes, index + 1, big_endian=True)
                '''while (dest + 6 < len(self.bytes)):
                    try:
                        if CC(self.bytes[dest + 3]) in [CC.PEN_2A, CC.PEN_29, CC.PEN_28]:
                            dest += b2i(self.bytes, dest + 4, big_endian=True)
                        else:
                            break
                    except:
                        break'''

                if index + 3 <= target_index < dest + 7:
                    req = [self.bytes[condition_start:index]]
                    #print(req)
                    condition.add_requirements(req)
                index += 3

            if inst in CONDITION_BREAKS:
                condition_start = index

        return condition

    def get_conditions(self):
        instructions = []
        i = 0
        while i < len(self.bytes):
            try:
                inst = CC(self.bytes[i])
            except:
                inst = self.bytes[i]
            if not (inst in Movelist.THREE_BYTE_INSTRUCTIONS):
                i += 1
                #throw away single variable instructions
            else:
                args = b2i(self.bytes, i+1, big_endian=True)
                instructions.append((inst, args, i))
                i += 3

        conditions = []

        counter = 0
        for inst, arg, line in instructions:
            if inst in [CC.PEN_2A, CC.PEN_29, CC.PEN_28]:
                new_condition = Condition(inst, line, arg)
                for cond in conditions:
                    if cond.start <= line < cond.end:
                        if cond.type == CC.PEN_28 or CC.PEN_29 :
                            #the CC.PEN_2A conditions are slightly tricky so lets try throwing them away and see if that causes any issues
                            new_condition.add_requirements(cond.requirements)
                if inst == CC.PEN_28:
                    if_instruction, if_arg, if_line = instructions[counter - 1]
                    if if_instruction == CC.ARG_89 or if_instruction == CC.ARG_8B:
                        new_condition.add_requirements([(self.bytes[if_line:if_line + 3])])
                    elif if_instruction == CC.EXE_A5:
                        instruction_length = if_arg & 0x00FF
                        start_index = instructions[counter - (instruction_length + 1)][2]
                        new_condition.add_requirements([(self.bytes[start_index:line])])
                    else:
                        print('Unexpected if instruction: {} {} {}'.format(if_instruction.name, if_arg, if_line))

                conditions.append(new_condition)

            counter += 1

        byte_to_condition = {}
        conditions.sort(key=lambda x: len(x.requirements), reverse=True)
        for c in conditions:
            for z in range(c.start, c.end, 1):
                if not z in byte_to_condition:
                    byte_to_condition[z] = c

        return byte_to_condition

    def parse_neutral_with_conditions(self):
        move_ids_to_commands = {}
        bytes_to_conditions = self.get_conditions()
        i = 0
        while_crouching = False
        while i < len(self.bytes):
            try:
                inst = CC(self.bytes[i])
            except:
                inst = self.bytes[i]
            if not inst in Movelist.THREE_BYTE_INSTRUCTIONS:
                i += 1
            else:
                if inst == CC.EXE_19:
                    instruction_length = b1i(self.bytes, i + 2)
                    try:
                        state_inst = CC(self.bytes[i-3])
                        checked_instructions = instruction_length
                        while checked_instructions > 0:
                            if state_inst == CC.ARG_8B:
                                state = b2i(self.bytes, i - 2 - ((instruction_length - checked_instructions) * 3), big_endian=True)
                                #print(decode_move_id(state, self.movelist))
                                if i in bytes_to_conditions:
                                    com = bytes_to_conditions[i].get_command()
                                    if while_crouching:
                                        com = 'WC {}'.format(com)
                                    #print(bytes_to_conditions[i])
                                    move_ids_to_commands[state] = com
                                break
                            elif state_inst == CC.ARG_89:
                                args = b2i(self.bytes, i - 2, big_endian=True)
                                if args == 0x161:
                                    pass
                                    #while_crouching = True
                                checked_instructions -= 1
                            else:
                                checked_instructions -= 1
                        if checked_instructions <= 0:
                            raise AssertionError()

                    except:
                        pass
                        #print('unexpected state encountered while parsing for 19 {}'.format(self.bytes[i-3:i]))
                        #print(Movelist.bytes_as_string(self.bytes[i - (instruction_length * 3):i + 3]))
                i += 3
        return move_ids_to_commands



    def get_technical_frames(self):
        infinite_set = (0x7FFF, 0x7600)
        notes = []

        splits = self.bytes.split(b'\x8b\x30\x5d')  # TC, TJ, and possibly airborne frames
        if len(splits) > 1:
            for split in splits[1:]:  # 8b xx xx 89 xx xx 89 xx xx #either 89 can be replaced by an 8b 7f ff for the start/end of a move
                type = b2i(split, 1, big_endian=True)
                start = b2i(split, 4, big_endian=True)
                stop = b2i(split, 7, big_endian=True)

                if start in infinite_set:
                    start = 0
                else:
                    start += 1
                if stop in infinite_set:
                    stop = ''
                else:
                    stop += 2  # possible that stop should only be +1 here but +2 matches our backfiller output

                if type == 2:
                    notes.append('TC[{}-{}]'.format(start, stop))
                elif type == 4:
                    notes.append('TJ[{}-{}]'.format(start, stop))
                elif type == 0x28:  # airborne???
                    pass
                elif type == 0x62:  # even more airborne???
                    pass

        splits = self.bytes.split(b'\x8b\x30\x64')#GI frames
        if len(splits) > 1:
            for split in splits[1:]:
                type_a = b2i(split, 1, big_endian=True) #mostly 0x149, 0x14a for armored/invincible?
                start = b2i(split, 4, big_endian=True)
                stop = b2i(split, 7, big_endian=True)
                type_b = b2i(split, 10, big_endian=True) # for GI 325/323 seem to both be mid/high, 322 seems to be lows #for armor, this seems to be damage absorbable before break
                vs_h = b2i(split, 13, big_endian=True) == 0x01 #horizontals
                vs_v = b2i(split, 16, big_endian=True) == 0x01 #verticals
                vs_k = b2i(split, 19, big_endian=True) == 0x01 #most kicks are horizontals so only really useful for horizontal impacts?
                vs_unk = b2i(split, 22, big_endian=True) == 0x01 #???

                if start in infinite_set:
                    start = 0
                else:
                    start += 2
                if stop in infinite_set:
                    stop = ''
                else:
                    stop += 3

                gi_effective_against = ''
                if vs_h:
                    gi_effective_against += ('H')
                if vs_v:
                    gi_effective_against += ('V')
                if vs_k and vs_h: #seems like most kicks are horizontals???
                    gi_effective_against += ('K')

                if type_a == 0x14a:
                    red_or_green = 'REV{}{}{}'.format('{', type_b, '}')
                else:
                    if type_b == 0x142:
                        gi_effective_against = gi_effective_against.swapcase()
                    red_or_green = 'GI{}{}{}'.format('{', gi_effective_against, '}')

                notes.append('{}[{}-{}]'.format(red_or_green, start, stop))
        return notes


    def get_gui_guide(self):
        guide = []

        index = 0
        list_of_bytes = []
        goto_blocks = []
        current_bytes = b''

        while index < len(self.bytes):
            current_bytes += self.bytes[index: index + 1]

            try:
                inst = CC(int(self.bytes[index]))
            except:
                list_of_bytes.append((current_bytes, 'ERROR PARSING', index))
                break

            if inst == CC.END:
                list_of_bytes.append((current_bytes, 'END', index))
                break
            elif inst in Movelist.THREE_BYTE_INSTRUCTIONS:
                args_bytes = self.bytes[index + 1: index + 3]
                current_bytes += args_bytes
                args = b2i(args_bytes, 0, big_endian=True)
                first_arg = int(args_bytes[0])
                second_arg = int(args_bytes[1])
                index += 3

                if inst == CC.START:
                    list_of_bytes.append((current_bytes, 'START (type {})'.format(args), index))
                    current_bytes = b''
                if inst == CC.EXE_A5:
                    list_of_bytes.append((current_bytes, 'SET A5 (condition {})'.format(first_arg), index))
                    current_bytes = b''
                if inst == CC.EXE_25:
                    try:
                        state_index = (index - 3) - (second_arg * 3)
                        state = b2i(self.bytes, state_index + 1, big_endian=True)
                        is_soul_charge = False
                        if state == 0x30CC: #soul charge, 3018 may be Tira/Gloomy only?
                            is_soul_charge = True
                            state_index = state_index + 3
                            state = b2i(self.bytes, state_index + 1, big_endian=True)


                        alias = decode_move_id(state, self.movelist)

                        state_args = Movelist.bytes_as_string(self.bytes[state_index + 3: index - 3])
                        if is_soul_charge:
                            tag = '<sc>'
                        else:
                            tag = '<b>'
                        state = '{}[id:{}{}{}]'.format(state, tag, alias, tag)
                    except:
                        state = 'ERROR'
                        state_args = 'ERROR'


                    if first_arg == 0x07:
                        list_of_bytes.append((current_bytes, 'SWITCH {} ({})'.format(state, state_args), index))
                    elif first_arg == 0x0d:
                        list_of_bytes.append((current_bytes, 'ADD {} ({})'.format(state, state_args), index))
                    else:
                        list_of_bytes.append((current_bytes, 'STATE {} ?? ({}) '.format(state, state_args), index))
                    current_bytes =  b''
                if inst == CC.EXE_19:
                    list_of_bytes.append((current_bytes, 'neutral cancel(???)'.format(first_arg), index))
                    current_bytes = b''
                if inst == CC.EXE_13:
                    list_of_bytes.append((current_bytes, 'yoshimitsu only ??? backturned mantis stance?'.format(first_arg), index))
                    current_bytes = b''
                if inst == CC.PEN_2A:
                    list_of_bytes.append((current_bytes, 'GOTO: {:04x}'.format(args), index))
                    goto_blocks.append((index, args))
                    current_bytes = b''
                if inst == CC.PEN_28:
                    list_of_bytes.append((current_bytes, 'IF [last a5] GOTO: {:04x}'.format(args), index))
                    current_bytes = b''
                    goto_blocks.append((index, args))
                if inst == CC.PEN_29:
                    list_of_bytes.append((current_bytes, 'IF ??? GOTO{:04x}'.format(args), index))
                    current_bytes = b''
                    goto_blocks.append((index, args))

            else:
                index += 1
                list_of_bytes.append((current_bytes, 'RETURN ({})'.format(inst.value), index))
                current_bytes =  b''

        guide = []
        index_to_line_number = {}
        counter = 0
        last_i = 0
        for bytes, desc, i in list_of_bytes:
            guide.append((Movelist.bytes_as_string(bytes), '{:04x}: {}'.format(last_i, desc)))
            for j in range(last_i, i):
                index_to_line_number[j] = counter
            last_i = i
            counter += 1
        index_to_line_number[i] = counter - 1

        goto_line_to_line = []
        for x, y in goto_blocks:
            goto_line_to_line.append((index_to_line_number[x], index_to_line_number[y]))
        #print(goto_line_to_line)

        return guide, goto_line_to_line

class Condition:
    def __init__(self, type : CC, start, end):
        self.type = type
        self.start = start
        self.end = end
        self.requirements = []

    def __repr__(self):
        set_as_string = ' | '.join([Movelist.bytes_as_string(x) for x in self.requirements])
        repr = '{} {}-{} : {}'.format(self.type, self.start, self.end, set_as_string)
        return repr

    def add_requirements(self, new_requirement):
        for element in new_requirement:
            requirement = element
            if not requirement in self.requirements:
                self.requirements.append(requirement)

    def get_command(self):
        dir = ''
        for t in reversed(self.requirements):
            arg = Condition.get_arg_if_match(t, CC.ARG_89)
            if arg != None:
                dir = arg
                break
        if not dir in range(1, 10, 1):
            dir = '?'

        button = ''
        for t in reversed(self.requirements):
            arg = Condition.get_arg_if_match(t, CC.ARG_8B)
            if arg != None:
                try:
                    button = PaddedButton(arg).name
                except:
                    button = '???'
                break



        return '{} {}'.format(dir, button)



    def get_arg_if_match(t, cc):
        if len(t) == 3:
            try:
                inst = CC(t[0])
                if inst == cc:
                    args = b2i(t, 1, big_endian=True)
                    return args
            except:
                pass
        return None




class Link:
    def __init__(self, cancel, cancel_index, conditions, args, move_id, encoded_move_id, type, sc_only, is_last_call, is_shortcut):
        self.cancel = cancel
        self.cancel_index = cancel_index
        self.conditions = conditions
        self.args = args
        self.move_id = move_id
        self.encoded_move_id = encoded_move_id
        self.type = type
        self.sc_only = sc_only
        self.is_last_call = is_last_call
        self.hold = False
        self.is_shortcut = is_shortcut

        self.delta = self.parse_edge()

        #self.button_press = self.parse_button()
        if (0xff < self.move_id < self.cancel.movelist.block_Q_length):
            self.button_press = self.better_parse_button()
        else:
            self.button_press = None

        self.auto_cancel = self.parse_auto_cancel()



    def __repr__(self):
        com = self.get_command_string()
        pa = Movelist.bytes_as_string(self.args)
        pp = ' ; '.join(['{} [{}]'.format(x[0], Movelist.bytes_as_string(x[1])) for x in self.conditions])
        return '{:04x}: 25 {:02x} LINK: <b>{}<b> {} [o:{} i:{} delta:{}] RAW: ({}) -> [{}]'.format(self.cancel_index, self.type, self.move_id, com, self.leave_on, self.enter_in, self.delta, pa,  pp)

    def parse_edge(self):
        args_split = []
        for i in range(0, len(self.args), 3):
            if self.args[i] == 0x89:
                args_split.append(b2i(self.args, i + 1, big_endian=True))

        if len(args_split) == 0:
            leave_on = 0
            enter_in = 0

        if len(args_split) == 1:
            leave_on = args_split[0]
            enter_in = 0

        if len(args_split) == 2:
            leave_on = args_split[-1]
            enter_in = args_split[-2]

        if len(args_split) > 2:
            leave_on = args_split[-2]
            enter_in = args_split[-1]

        self.leave_on = leave_on
        self.enter_in = enter_in
        #self.weight = self.leave_on - self.enter_in
        self.weight = self.leave_on
        return self.leave_on - self.enter_in

    def is_to_attack_or_stance(self, movelist):
        #attacks exist between 256 and the end of the first block in the movelist (block Q)
        #stances exist in the fourth block (block T) and seem to always start with 0x32 (so 0x3200+ could be a stance?)
        if not self.is_last_call:
            if self.move_id < len(movelist.all_moves):
                if self.move_id > 0x0100 and self.move_id < movelist.block_Q_length and self.sc_only == False:
                    return True
                if self.encoded_move_id >= 0x3200 and self.encoded_move_id < 0x3216:

                    if movelist.all_moves[self.move_id].cancel.has_at_least_one_button_press():
                        return True
        return False




    def get_command_string(self):
        com = ''
        if self.auto_cancel and not self.button_press:
            com = '.'
        elif self.hold:
            com = '[{}]'.format(self.button_press.name)
        elif self.button_press == None:
            com = '?'
        else:
            com = self.button_press.name

        if self.sc_only:
            com = '*{}'.format(com)

        return com

    def get_graph_weight(self):
        if self.hold or self.is_button_press():
            return 10
        else:
            return 1

    def better_parse_button(self):
        condition = self.cancel.get_basic_condition_by_index(self.cancel_index)
        for byte_array in condition.requirements:
            if len(byte_array) >= 6:
                arg_1 = b2i(byte_array, 1, big_endian=True)
                arg_2 = b2i(byte_array, 4, big_endian=True)
                if byte_array[0:1] == b'\x8b':
                    if arg_1 == InputType.Press.value or arg_1 == InputType.No_SC_Press.value:
                        if enum_has_value(PaddedButton, arg_2):
                            return PaddedButton(arg_2)
                    if arg_1 == InputType.Direction_PRESS.value or arg_1 == InputType.Direction_HOLD.value or arg_1 == InputType.Direction_ALT.value:
                        return PaddedButton.d
                    if arg_1 == InputType.OnContact.value:
                        try:
                            return PaddedButton(arg_2)
                        except Exception:
                            #print('UNKNOWNS {} {}'.format(arg_1, arg_2))
                            return PaddedButton.U

                    if arg_1 == InputType.Hold.value:
                        if enum_has_value(PaddedButton, arg_2):
                            self.hold = True
                            return PaddedButton(arg_2)
                    if arg_1 == InputType.DoubleTap.value:
                        if arg_2 == PaddedButton.dd.value:
                            return PaddedButton(arg_2)
        return None




    def parse_button(self):
        for type, c in self.conditions:
            index = 0

            while index < len(c) - 5:
                b = int(c[index]) #we're looking for the pattern 8b 00 06 8b [button argument]
                if b == 0x8b:
                    arg_1 = b2i(c, index + 1, big_endian=True)
                    if (int(c[index + 3]) == 0x8b):
                        arg_2 = b2i(c, index + 4, big_endian=True)

                        if arg_1 == InputType.Press.value or arg_1 == InputType.No_SC_Press.value:
                                if enum_has_value(PaddedButton, arg_2):
                                    return PaddedButton(arg_2)
                        if arg_1 == InputType.Direction_PRESS.value or arg_1 == InputType.Direction_HOLD.value:
                            return PaddedButton.d
                        if arg_1 == InputType.OnContact.value:
                            try:
                                return PaddedButton(arg_2)
                            except Exception:
                                return PaddedButton.UNK

                        if arg_1 == InputType.Hold.value:
                                if enum_has_value(PaddedButton, arg_2):
                                    self.hold = True
                                    return PaddedButton(arg_2)
                        if arg_1 == InputType.DoubleTap.value:
                            if arg_2 == PaddedButton.dd.value:
                                return PaddedButton(arg_2)

                    #if (int(c[index + 3]) == 0x8a): #8b 00 05 8a 00 f0 for RE release
                        #if arg_1 == 0x0005: #release?
                            #return PaddedButton.RE

                #if b == 0x8a:  # 8a 01 00 8b 7f ff for RE hold
                    #if (int(c[index + 3]) == 0x8b):
                        #return PaddedButton.RE


                index += 3
        return None

    def parse_auto_cancel(self):
        if len(self.conditions) == 1:
            if len(self.conditions[0][1]) == 3: #this move auto cancels at a specific frame
                if int(self.conditions[0][1][0]) == 0x89:
                    return True
                if int(self.conditions[0][1][0]) == 0x8b:
                    if int(self.conditions[0][1][1]) == 0x74: #still in soul charge???
                        return True
                    return True #??? ?? 00 54 / 00 09
            if len(self.conditions[0][1]) == 6:
                if int(self.conditions[0][1][0]) == 0x89 and int(self.conditions[0][1][3]) == 0x8b:#this move auto cancels during soul charge??
                    return True
                if int(self.conditions[0][1][0]) == 0x89 and int(self.conditions[0][1][3]) == 0x89:#auto cancel window?????
                    return True
        elif len(self.conditions) == 0:
            return True
        return False

    def is_auto_cancel(self):
        return self.auto_cancel

    def is_button_press(self):
        if self.button_press == None:
            return False
        else:
            return True

class Movelist:
    HEADER_LENGTH = 0x30
    #STARTER_STRING = 'KH11'
    STARTER_INT = 0x3131484b

    THREE_BYTE_INSTRUCTIONS = [CC.START, CC.ARG_8A, CC.ARG_8B, CC.ARG_89, CC.EXE_19, CC.EXE_25, CC.EXE_A5, CC.EXE_13, CC.PEN_2A, CC.PEN_28, CC.PEN_29]

    def __init__(self, raw_bytes, name):
        self.bytes = raw_bytes
        self.name = name.split('/')[-1].split('_')[0].capitalize()

        header_index_1x = 0xC
        header_index_1y = 0xE
        header_index_2 = 0x10 # to attacks info
        header_index_3 = 0x14 # very short byte block
        header_index_4 = 0x18 # cinematics info
        header_unknown_1c = 0x1c
        header_unknown_1e = 0x1e
        header_unknown_20 = 0x20 #same as 0x1c in tira
        header_unknown_22 = 0x22
        header_unknown_24 = 0x24 #??
        header_unknown_26 = 0x26
        header_unknown_28 = 0x28
        header_unknown_2a = 0x2A
        header_unknown_2C = 0x2C

        move_block_start = 0x30
        self.length = b2i(raw_bytes, header_index_1x) - 1
        self.id = b2i(raw_bytes, header_index_1y)
        self.block_Q_start = b2i(raw_bytes, header_unknown_1c) #always zero???
        self.block_Q_length = b2i(raw_bytes, header_unknown_1e) #this offset is used to help determine the location for non attack moves such as stances and nuetral, they are marked as 3200+

        self.block_R_start = b2i(raw_bytes, header_unknown_20)  #always q length?
        self.block_R_length = b2i(raw_bytes, header_unknown_22)

        self.block_S_start = b2i(raw_bytes, header_unknown_24)
        self.block_S_length = b2i(raw_bytes, header_unknown_26)

        self.block_T_start = b2i(raw_bytes, header_unknown_28)
        self.block_T_length = b2i(raw_bytes, header_unknown_2a)

        #print('Q: {}+{} R: {}+{} S: {}+{} T: {}+{}'.format(self.block_Q_start, self.block_Q_length, self.block_R_start, self.block_R_length, self.block_S_start, self.block_S_length, self.block_T_start, self.block_T_length))

        attack_block_start = b4i(raw_bytes, header_index_2)
        short_block_start = b4i(raw_bytes, header_index_3)
        misc_block_start = b4i(raw_bytes, header_index_4)

        move_block_bytes = raw_bytes[move_block_start: attack_block_start]

        self.all_moves = []
        counter = 0
        for i in range(0, len(move_block_bytes), Move.LENGTH):
            move = Move(move_block_bytes[i: i + Move.LENGTH], self, counter)
            self.all_moves.append(move)
            counter += 1
        #print(hex(i))

        attack_block_bytes = raw_bytes[attack_block_start: short_block_start]
        self.all_attacks = []
        for i in range(0, len(attack_block_bytes), Attack.LENGTH):
            attack = Attack(attack_block_bytes[i: i + Attack.LENGTH])
            self.all_attacks.append(attack)

        for move in self.all_moves:
            attacks = []
            for index in move.attack_indexes:
                if index < len(self.all_attacks):
                    attacks.append(self.all_attacks[index])
            move.set_attacks(attacks)


        self.all_cancels = {}
        self.move_ids_to_cancels = {}
        for i in range(0, len(self.all_moves)):
            ca = self.all_moves[i].cancel_address
            try:
                end = self.all_moves[i + 1].cancel_address
            except:
                end = ca + self.parse_cancel_bytes_to_end(raw_bytes[ca:])
            cancel = Cancel(self, raw_bytes[ca: end], ca, i)
            self.all_cancels[ca] = cancel
            self.move_ids_to_cancels[i] = cancel
            self.all_moves[i].set_cancel(cancel)

        #chase stance shortcuts in links
        for cancel in self.all_cancels.values():
            cancel.condense_all_shortcuts()

        #self.move_ids_to_commands = self.alt_parse_neutral()
        self.move_ids_to_commands = self.parse_neutral()
        move_ids_to_check = list(self.move_ids_to_commands.keys())
        self.nodes = []

        while len(move_ids_to_check) > 0:
            move_id = move_ids_to_check.pop(0)
            original_command = self.move_ids_to_commands[move_id]
            ids_to_commands = {}
            if move_id < len(self.all_moves) and move_id >= 0:
                for link in self.move_ids_to_cancels[move_id].links:
                    com = link.get_command_string().replace('_', '+')
                    weight = link.get_graph_weight()
                    self.nodes.append((move_id, link.move_id, weight, com))
                    if link.is_button_press() or link.is_auto_cancel() or True:
                        ids_to_commands[link.move_id] = com

            for cancelable_move_id in ids_to_commands:
                if not cancelable_move_id in self.move_ids_to_commands.keys():
                    new_command = ids_to_commands[cancelable_move_id]
                    if '['  in new_command:
                        self.move_ids_to_commands[cancelable_move_id] = '{}'.format(original_command[:2 - len(new_command)] + new_command)
                    else:
                        self.move_ids_to_commands[cancelable_move_id] = '{}{}'.format(original_command, new_command)
                    move_ids_to_check.append(cancelable_move_id)

        self.short_bytes = self.bytes[short_block_start : misc_block_start]
        self.misc_bytes = self.bytes[misc_block_start : self.all_moves[0].cancel_address]
        #print('{:x} : {:x} : {:x}'.format(short_block_start, misc_block_start, misc_block_start - short_block_start))
        #self.generate_modified_movelist_bytes()

    def parse_cancel_bytes_to_end(self, bytes):
        i = 0
        while i < len(bytes):
            inst = bytes[i]
            try:
                inst = CC(inst)
            except:
                pass

            if inst == CC.END:
                return (i + 1)

            if inst in Movelist.THREE_BYTE_INSTRUCTIONS:
                i += 3
            else:
                i += 1

        return len(bytes)

    def print_all_frame_data(self):
        for move in self.all_moves:
            if 255 < move.move_id < self.block_Q_length:
                for data in move.get_frame_data():
                    print(data)



    def generate_modified_movelist_bytes(self):
        #header = b'\x99' + self.bytes[1:Movelist.HEADER_LENGTH]
        header = self.bytes[:Movelist.HEADER_LENGTH]

        do_replace_animation = False
        replace_bytes = b'\x85\x00\x00\x00'

        do_have_infinite_active_frames = False

        attacks = b''
        for attack in self.all_attacks:
            next_attack = attack.get_modified_bytes()
            if do_have_infinite_active_frames:
                next_attack = next_attack[:0x36] + b'\x01' + next_attack[0x37:] #0x36 start active
                next_attack = next_attack[:0x38] + b'\xFF' + next_attack[0x39:] #0x38 end active
            attacks += next_attack

        short = self.short_bytes

        misc = self.misc_bytes

        cancel_offsets = [0,]
        cancels = b''
        for key in range(0, len(self.all_moves)):
            cancel = self.move_ids_to_cancels[key]
            next_cancel = cancel.update_goto_instructions(cancel.get_modified_bytes(), cancel.bytes)
            cancels += next_cancel
            cancel_offsets.append(len(next_cancel))

        CANCEL_ADDRESS_OFFSET = 0x38

        starting_cancel_offset = self.all_moves[0].cancel_address
        moves = b''
        running_address = starting_cancel_offset
        for i, move in enumerate(self.all_moves):
            running_address += cancel_offsets[i]
            next_move = move.get_modified_bytes()
            cancel_address = (running_address).to_bytes(4, byteorder='little')
            next_move = next_move[:CANCEL_ADDRESS_OFFSET ] + cancel_address + next_move[CANCEL_ADDRESS_OFFSET + 4:]


            if do_replace_animation:
                next_move = replace_bytes + next_move[len(replace_bytes):]

            moves += next_move



        all_bytes =  header + moves + attacks + short + misc + cancels

        #with open('test.out', 'wb') as fw:
            #fw.write(all_bytes)
        return all_bytes





    def get_command_by_move_id(self, move_id):
        if move_id in self.move_ids_to_commands:
            return self.move_ids_to_commands[move_id]
        else:
            return '???'

    def search_for_cancel_arg(self, array, index, default):
        if index < len(array) and len(array) >= 2:
            return b2i(array[index], 0, big_endian=True)
        else:
            return default

    def print_bytes(byte_array):
        string = Movelist.bytes_as_string(byte_array)
        print(string)

    def bytes_as_string(byte_array):
        return ' '.join('{:02x}'.format(x) for x in byte_array)

    def from_file(filename):
        with open(filename, 'rb') as fr:
            raw_bytes = fr.read()
        return Movelist(raw_bytes, filename)

    def button_parse(type_code, input_code):
        if enum_has_value(InputType, type_code) and enum_has_value(PaddedButton, input_code):
            type = InputType(type_code)
            input = PaddedButton(input_code)
            if type == InputType.Press:
                return '{}'.format(input.name)
            elif type == InputType.Direction or type == InputType.Direction_ALT:
                codes_to_directions = {
                    PaddedButton.Forward : '6',
                    PaddedButton.Forward_ALT: '6',
                }
                if input in codes_to_directions.keys():
                    return'{}'.format(codes_to_directions[input])
                else:
                    return 'dir {:04x}'.format(input_code)

            elif type == InputType.Hold:
                return '[{}]'.format(input.name)
            else:
                return '{} {}'.format(type.name, input.name)
        else:
            try:
                return '{:04x}:{:04x}'.format(type_code, input_code)
            except Exception as e:
                import sys
                print ('{} {}'.format(type_code, input_code), file=sys.stderr)
                raise e


    def alt_parse_neutral(self):
        cancels = [x for x in self.all_cancels.values() if x.type >= 4]  # less hackish way to find neutral
        move_ids_to_commands = {}
        for cancel in cancels:
            mtc = cancel.parse_neutral_with_conditions()
            for key, value in mtc.items():
                if not key in move_ids_to_commands:
                    move_ids_to_commands[key] = value
        return move_ids_to_commands

    def parse_neutral(self):
        cancels = [x for x in self.all_cancels.values() if x.type >= 4] #less hackish way to find neutral

        move_ids_to_commands = {}
        replacements = []
        for cancel in cancels:
            #state machine variables
            args_expected = 0
            buf_89 = [-1, -1, -1, -1, -1]
            buf_8a = [-1, -1, -1, -1, -1]
            buf_8b = [-1, -1, -1, -1, -1]
            button_code = None
            next_8b_is_input = False
            next_19_is_normal_move = False
            next_19_is_8way_move = False
            next_19_is_backturned_move = False
            next_19_is_while_running = False
            next_19_is_azwel_replacement = False
            next_19_is_236 = False
            while_crouching_flag = False
            while_standing_signs = [-1]
            buffers = [buf_89, buf_8a, buf_8b]



            for i in range(len((cancel.bytes))):
                if args_expected != 0:
                    args_expected -= 1
                else:
                    inst = int(cancel.bytes[i])
                    try:
                        next_instruction = CC(inst)
                    except Exception as e:
                        #Either we've hit a new single (exciting!) or more likely we've overflowed into non-movelist bytes (sad)
                        #print('ERROR move_id:{} hex:{}'.format(cancel.move_id, hex(inst))) #don't call this during tkinter boot up sequence
                        break
                    #if it's an argument instruction, we store it for future use in an exe instruction
                    if next_instruction in Movelist.THREE_BYTE_INSTRUCTIONS:
                        args_expected = 2
                    else:
                        next_8b_is_input = False
                    if next_instruction in [CC.ARG_89, CC.ARG_8A, CC.ARG_8B]:
                        try:
                            buffers[abs(0x89 - inst)].append(b2i(cancel.bytes[i+1:], 0, big_endian = True))
                        except Exception as e:
                            print('error move_id: {} inst: {} counter: {}'.format(cancel.move_id, hex(inst), i))
                            raise e

                        if next_instruction == CC.ARG_8A:
                            if buf_8a[-1] == 0x0102 or buf_8a[-1] == 0x0101 or buf_8a[-1] == 0x0103: #input marker
                                next_8b_is_input = True
                            if buf_8a[-1] == 0x0103 or buf_8a[-1] == 0x0104: #0x0104 only for tira gloomy???
                                next_19_is_8way_move = True
                            if buf_8a[-1] == 0x105:
                                next_19_is_azwel_replacement = True
                            if buf_8a[-1] == 0x003D or buf_8a[-1] == 0x0102:
                                next_19_is_normal_move = True
                            if buf_8a[-1] == 0x0048:
                                #next_19_is_backturned_move = True
                                next_19_is_normal_move = True
                        if next_instruction in [CC.ARG_8B]:
                            if buf_8b[-1] == 0x001f:
                                next_19_is_while_running = True
                            if buf_8b[-1] == 0x0041 or buf_8b[-1] == 0x002b:
                                next_19_is_236 = True
                            if next_8b_is_input:
                                button_code = buf_8b[-1]
                                next_8b_is_input = False
                    #if it's an exe instruction, we 'execute' it, reading from the proper buffers to provide arguments
                    if next_instruction in [CC.EXE_19]:
                        move_id, dir = buf_8b[-1], buf_89[-1]
                        try:
                            button = PaddedButton(button_code).name
                            button = button.replace('_', '+')
                        except Exception as e:
                            button = button_code

                        if dir == 0x0096 or dir == 0x0097:
                            dir = 'bt'
                        if dir == 0xffff:
                            dir = ''

                        #if buf_89[-1] == 0xffff: #dunno what these are, but they aren't moves???
                            #next_19_is_8way_move = False
                            #next_19_is_normal_move = False

                        if next_19_is_normal_move or next_19_is_8way_move or next_19_is_while_running or next_19_is_236:
                            if not while_crouching_flag and next_19_is_normal_move: #hack way to guess when we've reached while crouching moves
                                if button_code in while_standing_signs:
                                    if button_code != while_standing_signs[-1]:
                                        while_crouching_flag = True
                                else:
                                    while_standing_signs.append(button_code)

                            command = '{}{}'.format(dir, button)

                            if next_19_is_while_running:
                                command = 'WR {}'.format(button)
                            elif next_19_is_236:
                                command = '236{}'.format(button)
                            elif next_19_is_8way_move and dir != 5:
                                command = '{}{}'.format(dir, command)
                            elif while_crouching_flag:
                                pass #TODO: better way to detect WC?
                                #command = 'WC {}'.format(command)


                            do_replace = True
                            if move_id in move_ids_to_commands.keys():
                                if '6' in move_ids_to_commands[move_id] or '4' in move_ids_to_commands[move_id]:
                                    do_replace = False

                            if do_replace:
                                move_ids_to_commands[move_id] = command

                            #cleanup
                            next_19_is_normal_move = False
                            next_19_is_8way_move = False
                            next_19_is_backturned_move = False
                            next_19_is_while_running = False
                            next_19_is_azwel_replacement = False
                            next_19_is_236 = False

                        elif next_19_is_azwel_replacement:
                            next_19_is_azwel_replacement = False
                            id = buf_8b[-1]
                            replace = buf_8b[-2]
                            replacements.append((id, replace))


        for id, replace in replacements:
            if replace in move_ids_to_commands and not id in move_ids_to_commands:
                #print('replacement {} -> {}'.format(id, replace))
                move_ids_to_commands[id] = '!{}'.format(move_ids_to_commands[replace])
        return move_ids_to_commands

    def condition_parse(self, move_id):
        if not move_id < len(self.move_ids_to_cancels) or move_id < 0:
            return []
        else:
            cancel = self.move_ids_to_cancels[move_id]
            return Movelist.links_from_bytes(cancel, self)


    def links_from_bytes(cancel, movelist):
            bytes = cancel.bytes
            buf_all = []

            links = []

            conditions = []
            index = 0
            buf_8b = []
            pos_to_conditions = {}
            last_call_index = Cancel.get_last_call_address_index(bytes)
            while index < len(bytes):
                try:
                    inst = CC(int(bytes[index]))
                except:
                    inst = CC.UNK
                is_last_call = index >= last_call_index
                if inst == CC.START:
                    index += 3
                elif inst in (CC.PEN_2A, CC.PEN_28, CC.PEN_29):
                    arg = b2i(bytes, index + 1, big_endian=True)
                    if inst == CC.PEN_28:
                        pos_to_conditions[arg] = list(conditions)

                    if inst == CC.PEN_2A:
                        if arg in pos_to_conditions.keys():
                            conditions += pos_to_conditions[arg]


                    index += 3
                elif inst in (CC.ARG_8B, CC.ARG_8A, CC.ARG_89):
                    if inst == CC.ARG_8B:
                        arg = b2i(bytes, index + 1, big_endian=True)
                        buf_8b.append(arg)

                    for _ in range(3):
                        try:
                            buf_all.append(int(bytes[index]))
                            index += 1
                        except Exception as e:
                            import sys
                            sys.stderr.write(str(last_call_index))
                            sys.stderr.write(inst.name)
                            sys.stderr.write(str(index))
                            raise e

                elif inst in (CC.EXE_25, CC.EXE_A5, CC.EXE_19, CC.EXE_13):
                    # print('{} {}: ({})'.format(inst, pos, Movelist.bytes_as_string((paper[max(pos - 29, 0):pos]))))
                    if inst == CC.EXE_A5: #add condition
                        condition_type = int(bytes[index + 1])
                        condition_arg_number = int(bytes[index + 2])
                        args = bytes[index - (3 * condition_arg_number): index]
                        conditions.append((condition_type, args))

                    if inst == CC.EXE_19: #if we figure this out we can unify with parse_neutral, until then we throw this away
                        conditions = []

                    if inst == CC.EXE_25: #add cancel
                        exe_type = int(bytes[index + 1])
                        exe_arg_number = int(bytes[index + 2])
                        args = bytes[index - (3 * exe_arg_number): index]
                        state = -1
                        ref_state = -1
                        sc_only = False
                        is_shortcut = False
                        for i, b in enumerate(args):
                            if b == 0x8b:
                                state = b2i(args, i + 1, big_endian=True)
                                ref_state = state
                                if state == 0x30CC or state == 0x30CE :  # soul charge marker, keep going 0x3218 may be tira gloomy only??
                                    sc_only = True
                                elif 0x3200 <= state <= 0x3300 : #stances exist in this range??
                                    state = decode_move_id(state, movelist)
                                    is_shortcut = True
                                    break
                                else:
                                    state = decode_move_id(state, movelist)
                                    break

                        links.append(Link(cancel, index - len(args), conditions, args, state, ref_state, exe_type, sc_only, is_last_call, is_shortcut))
                        #print('{} {} {}: ({})'.format(inst, int(bytes[index + 1]), int(bytes[index + 2]), state))

                        conditions = []
                    index += 3
                else:
                    #paper[pos] = int(bytes[index])
                    #print('{}'.format(inst))
                    #conditions = []
                    index += 1

            return links


    def alt_parse(self, move_id):
        cancel = self.move_ids_to_cancels[move_id]
        bytes = cancel.bytes

        sections = []
        last_slice = bytes.index(b'\x28') + 3
        print(last_slice)
        while True:
            slices = bytes[last_slice:].split(b'\x28')
            if len(slices) <= 1:
                break
            else:
                slice = slices[1]
            goto = b2i(slice, 0, big_endian=True)
            sections.append((last_slice, bytes[last_slice:goto]))
            last_slice = goto

        for goto, s in sections:
            print('{:04x}: {}'.format(goto, Movelist.bytes_as_string(s)))




    def write_graph(self):
        with open('graph.csv', 'w') as fw:
            fw.write('Source;Target;Weight;Label\n')
            for node in self.nodes:
                if not '?' in node[3]:
                    fw.write('{};{};{};{}\n'.format(node[0], node[1], node[2], node[3]))

    def reverse_spider_crawl(self):
        from collections import defaultdict
        neutral_ids = self.parse_neutral().keys()

        starting_nodes = []
        for i in range(0x101, self.block_Q_length): #these are the 'interesting' moves, minus a few like soul charge
            starting_nodes.append(i)

        edges = set()
        true_edges = set()
        old = set()
        to_check = set(starting_nodes)
        more_checks = set()
        for _ in range(1):
            for cancel in self.move_ids_to_cancels.values():
                    links = cancel.links
                    for link in links:
                        if (link.move_id in to_check):
                            if link.move_id in starting_nodes and cancel.move_id in starting_nodes:
                                true_edges.add((cancel.move_id, link.move_id))
                            else:
                                edges.add((cancel.move_id, link.move_id))
                                if (not cancel.move_id in to_check) and (not cancel.move_id in old):
                                    more_checks.add(cancel.move_id)
            old.update(to_check)
            to_check = set(more_checks)
            more_checks = set()
        print(len(edges))
        print(edges)

        #consolidate stances
        for cancel in self.move_ids_to_cancels.values():
            if cancel.move_id in starting_nodes:
                for x1, y1 in edges:
                    for link in cancel.links:
                        if link.move_id == x1:
                            true_edges.add((cancel.move_id, y1))

        print(len(true_edges))
        print(true_edges)

        #remove edges to anything in neutral (clears up 1 frame cancels):
        cleaned_edges = set()
        for x1, y1 in true_edges:
            if not y1 in neutral_ids:
                cleaned_edges.add((x1, y1))
        true_edges = cleaned_edges


        #add neutral
        for move_id in neutral_ids:
            true_edges.add((0, move_id))

        with open('graph2.csv', 'w') as fw:
            fw.write('Source;Target;Label\n')
            for start, stop in true_edges:
                try:
                    com = self.move_ids_to_commands[stop]
                except:
                    com = '?'
                fw.write('{};{};{}\n'.format(start, stop, com))


    def write_cancels(self):
        with open('cancels/c_{}'.format(self.name), 'w') as fw:
            print('making cancels for {}'.format(self.name))
            self.print_out_cancel_blocks(fw)

    def print_move_id_details(self, move_id):
        move = self.all_moves[move_id]
        print(Movelist.bytes_as_string(move.bytes))
        for index in move.attack_indexes:
            print(Movelist.bytes_as_string(self.all_attacks[index].bytes))

        move.get_frame_data()

        links = self.condition_parse(move_id)
        for link in links:
            print(link)

    def print_out_cancel_blocks(self, fw):
        for cancel in sorted(self.all_cancels.values(), key=lambda x: len(x.bytes)):
            running_index = 0
            check_for_end = False
            fw.write('#{}\n'.format(cancel.move_id))
            index = 0
            while index < len(cancel.bytes):
                # if cancel.bytes[index: index + 3] == b'\x25\x0d\05':
                # Movelist.print_bytes(cancel.bytes[index - 18: index + 2])
                bytes = cancel.bytes
                if check_for_end:
                    if bytes[index: index + 2] == b'\x02':
                        fw.write('02\n')
                        fw.write('-------------------------------\n')
                        break

                next_byte = int(bytes[index])

                if next_byte in [CC.EXE_13.value, CC.EXE_19.value, CC.EXE_25.value, CC.EXE_A5.value]:
                    fw.write(Movelist.bytes_as_string(bytes[running_index: index + 3]) + '\n')
                    running_index = index + 3
                    check_for_end = True
                    index += 2
                elif next_byte in [CC.START.value, CC.ARG_8B.value, CC.ARG_8A.value, CC.ARG_89.value, CC.PEN_29.value, CC.PEN_28.value, CC.PEN_2A.value]:
                    index += 2
                index += 1


if __name__ == "__main__":
    import os
    def load_all_movelists():

        directory = 'movelists/'

        movelists = []
        for filename in os.listdir(directory):
            if filename.endswith('.m0000') or filename.endswith('.sc6_movelist'):
                localpath = '{}/{}'.format(directory, filename)
                print('loading {}...'.format(localpath))
                movelist = Movelist.from_file(localpath)
                movelists.append(movelist)
        return movelists

    #input_file = 'tira_movelist.byte.m0000'

    #input_file = 'movelists/xianghua_movelist.byte.m0000' #these come from cheat engine, memory viewer -> memory regions -> (movelist address) . should be 0x150000 bytes

    #movelists = load_all_movelists()
    #movelists = [Movelist.from_file('movelists/tira.sc6_movelist')]
    #movelists = [Movelist.from_file('movelists/seong_mina_movelist.m0000')]
    #movelists = [Movelist.from_file('movelists/yoshimitsu_movelist.m0000')]
    #movelists = [Movelist.from_file('movelists/xianghua.sc6_movelist')]
    #movelists = [Movelist.from_file('movelists/mitsurugi_movelist.m0000')]
    #movelists = [Movelist.from_file('movelists/ivy_movelist.m0000')]
    #movelists = [Movelist.from_file('movelists/geralt_movelist.m0000')]
    #movelists = [Movelist.from_file('movelists/siegfried_movelist.m0000')]
    #movelists = [Movelist.from_file('movelists/voldo_movelist.m0000')]
    #movelists = [Movelist.from_file('movelists/azwel_movelist.m0000')]
    movelists = [Movelist.from_file('movelists/2B.sc6_movelist')]

    #for movelist in movelists:

    print('XXXXXXXXXXXXXXXXXXXX\n\n\n\n')
    #movelists[0].print_move_id_details(292)
    #movelists[0].print_move_id_details(285)
    #movelists[0].print_move_id_details(259)
    for link in movelists[0].move_ids_to_cancels[265].links:
        #if link.is_to_attack_or_stance(movelists[0]):
        print(link)

    for cancel in movelists[0].move_ids_to_cancels.values():
        if cancel.type >= 8:
            print(cancel.move_id)
        for link in cancel.links:
            if link.move_id == 364:
                print(cancel.move_id)
                print(link)


    cancel = movelists[0].all_moves[2433].cancel
    #for c in cancel.get_conditions():
        #print(c)
    print(cancel.parse_neutral_with_conditions())
    '''true_counter = 0
    total_counter = 0
    for move in movelists[0].all_moves:
        if move.cancel.move_id > 0xff and move.cancel.move_id < movelists[0].block_Q_length:
            total_counter += 1
            if b'\x8b\x00\x09\xa5\x01\x01\x96\x28' in move.cancel.bytes:
                true_counter += 1
            else:
                print(move.cancel.move_id)
    print('{}/{}'.format(true_counter, total_counter))

    for cancel in sorted(movelists[0].move_ids_to_cancels.values(), key=lambda x: x.type):
        if cancel.type > 1:
            print('{} : {} : 0x{:04x}'.format(cancel.type, cancel.move_id, encode_move_id(cancel.move_id, movelists[0])))'''

    #movelists[0].alt_parse(2345)
    #movelists[0].reverse_spider_crawl()
    movelists[0].print_all_frame_data()

    #cancel = movelists[0].all_moves[257].cancel
    #index = cancel.get_link_to_move_id(259).cancel_index
    #print(index)
    #print(cancel.get_basic_condition_by_index(index))

    for link in movelists[0].all_moves[424].cancel.links:
        print(link)