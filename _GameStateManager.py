import SoulCaliburGameState
import time
import GameplayEnums
import MovelistParser
from typing import List

class GameStateManager:
    def __init__(self):
        self.game_reader = SoulCaliburGameState.SC6GameReader()
        self.p1_move_id = 0
        #self.p1_backfiller = FrameBackCounter(True)
        #self.p2_backfiller = FrameBackCounter(False)
        self.move_ids_record = [[], []]
        self.bhc_stuns_record = [[], []]
        self.entry_times = [[], []]
        self.time_spent_in_move_id_count = [[], []]

    def Update(self, do_print_debug_vars, show_all_hitboxes):
        successful_update = self.game_reader.UpdateCurrentSnapshot()
        if successful_update:
            try:
                snapshots = self.game_reader.snapshots
                #self.p1_backfiller.update(snapshots)
                #self.p2_backfiller.update(snapshots)
                if len(snapshots) > 4:
                    self.p1_move_id = snapshots[-1].p1.movement_block.movelist_id
                    did_p1_attack_change = snapshots[-2].p1.movement_block.movelist_id != snapshots[-3].p1.movement_block.movelist_id
                    if did_p1_attack_change:
                        old_id = snapshots[-3].p1.movement_block.movelist_id
                        self.count_time_in_move_id(self.time_spent_in_move_id_count[0], old_id, snapshots, True)

                        s = self.create_frame_entry('p1', snapshots[-1].p1, self.move_ids_record[0], self.bhc_stuns_record[0], self.entry_times[0], self.game_reader.p1_movelist)

                        if s != None:
                            for entry in s:
                                print(entry)
                                if not show_all_hitboxes:
                                    break


                    #did_p2_attack_change = snapshots[-1].p2.global_block.last_attack_address != snapshots[-2].p2.global_block.last_attack_address
                    did_p2_attack_change = snapshots[-2].p2.movement_block.movelist_id != snapshots[-3].p2.movement_block.movelist_id
                    if did_p2_attack_change:
                        old_id = snapshots[-3].p2.movement_block.movelist_id
                        self.count_time_in_move_id(self.time_spent_in_move_id_count[1], old_id, snapshots, False)
                        s = self.create_frame_entry('p2', snapshots[-1].p2, self.move_ids_record[1],self.bhc_stuns_record[1], self.entry_times[1], self.game_reader.p2_movelist)

                        if s != None:
                            for entry in s:
                                print(entry)
                                if not show_all_hitboxes:
                                    break


                if do_print_debug_vars:
                    print(self.game_reader.snapshots[-1])
            except Exception as e:
                print(e)
                raise e

    def count_time_in_move_id(self, count_list, move_id, snapshots, is_p1 = True):
        found_move_id = False
        move_id_changed = False

        start_time = 0
        stop_time = 0
        i = 0
        while i < len(snapshots) and not move_id_changed:
            if is_p1:
                next_move_id = snapshots[-i].p1.movement_block.movelist_id
            else:
                next_move_id = snapshots[-i].p2.movement_block.movelist_id
            if not found_move_id and move_id == next_move_id:
                start_time = snapshots[-i].timer
                found_move_id = True

            if found_move_id and move_id != next_move_id:
                stop_time = snapshots[-i].timer
                move_id_changed = True
            i += 1

        if start_time == 0 or stop_time == 0:
            count = 0
        else:
            count = start_time - stop_time

        count_list.append((move_id, count))
        #print(count_list[-1])
        while len(count_list) > 10:
            count_list.pop(0)


    def create_frame_entry(self, name, p, record, bhc_stuns, times, movelist):
        id = p.movement_block.movelist_id
        if len(record) == 0 or record[-1] != id:
            record.append(id)
        #bhc_stuns.append((0, 0, 0))
        #if id != 0x59 and id <= movelist.block_Q_length:  # 0x59 is the 'coming to a stop' move_id from 8 way run and above q_length are 'imaginary' moves
        if (id >= 0x0100 and id <= movelist.block_Q_length) or id == 212 or id == 214: #212 is soul charge, the only interesting move below 0x0100
                if len(bhc_stuns) > 1:
                    stun = bhc_stuns[-1] #declare here in case we add a new one in FrameStringFromMovelist
                s = GameStateManager.FrameStringFromMovelist(name, p, record, bhc_stuns, self.game_reader.snapshots[-1].timer)
                #times.append(self.game_reader.timer - p.movement_block.short_timer)
                times.append(self.game_reader.timer)
                if len(times) > 1 and len(bhc_stuns) > 2:
                    #delta = times[-1] - times[-2]
                    delta = times[-1] - stun[4]
                    delta -= stun[3]
                    #print(stun)
                    #print('d{}({}) | {} | {} | {}'.format(delta, delta + stun[3], delta - stun[0], delta - stun[1], delta - stun[2]))

                return s
        while len(record) > 10:
            record.pop(0)

        while len(times) > 10:
            times.pop(0)

        while len(bhc_stuns) > 10:
            bhc_stuns.pop(0)

        return None

    def FrameStringFromMovelist(p_str, p : SoulCaliburGameState.PlayerSnapshot, move_ids, stuns, timer):

        def pretty_frame_data_entry(fd : MovelistParser.FrameData):
            guard_damage = p.startup_block.guard_damage
            frame_string = 'FDO:{}:{}'.format(p_str, fd).replace('[gd]', '{:^2}'.format(guard_damage))
            strings.append(frame_string)

        def no_hitbox_data():
            com = p.movelist.get_command_by_move_id(id)
            fd = MovelistParser.FrameData(id, com, 0, 0, 0, ' ', 0, ' ', 0, ' ', ' ', ' ', 0, 0, [''])

            if move_ids[-1] >= 0 and move_ids[-1] < len(p.movelist.all_moves):
                move = p.movelist.all_moves[move_ids[-1]]
                fd.notes = move.cancel.get_technical_frames()
                cf = move.cancel.get_cancelable_frames()
                total = move.total_frames
                shortcut_links = []
                for link in move.cancel.links:
                    if link.is_shortcut:
                        shortcut_links.append(link)
                #if len(shortcut_links) > 0:
                    #fd.notes += ['x{}'.format('/'.join(['{}'.format(x.leave_on) for x in shortcut_links]))]
                #else:
                fd.whiff = '{}'.format(total - cf)

            fd.delta = delta

            pretty_frame_data_entry(fd)
            return strings



        id = p.movement_block.movelist_id
        move = p.movelist.all_moves[id]

        delta = 0
        if len(move_ids) > 1 and move_ids[-2] < len(p.movelist.all_moves):
            try:
                old_move = p.movelist.all_moves[move_ids[-2]]
                old_link = old_move.cancel.get_link_to_move_id(move_ids[-1])
                leave = old_link.leave_on
                enter = old_link.enter_in
                diff = leave - enter
                if len(old_move.attacks) > 0:
                    old_startup = old_move.attacks[0].startup
                    old_block_stun = old_move.attacks[0].block_stun
                else:
                    old_block_stun = 0
                    old_startup = 0
                    if len(move_ids) > 2 and move_ids[-3] < len(p.movelist.all_moves):
                        older_move = p.movelist.all_moves[move_ids[-3]]
                        older_link = older_move.cancel.get_link_to_move_id(move_ids[-2])
                        if len(older_move.attacks) > 0:
                            old_startup = older_move.attacks[0].startup
                            old_block_stun = older_move.attacks[0].block_stun
                            #leave += older_link.leave_on
                            #enter += older_link.enter_in
                            older_diff = older_link.leave_on - older_link.enter_in
                            print('2:{} 1:{} s:{} b:{}'.format(diff, older_diff, old_startup, old_block_stun))
                            diff += (older_diff)



                delta = diff - old_startup - old_block_stun
                #if not old_link.is_shortcut:
                #delta -= enter
            except Exception as e:
                pass
                #print(e)
                print("Couldn't find route from {} to {}".format(move_ids[-2], move_ids[-1]))



        strings = []

        if id >= len(p.movelist.all_moves):
            return no_hitbox_data()

        else:
            frame_datas = move.get_frame_data(delta=delta)
            if len(frame_datas) == 0:
                return no_hitbox_data()
            else:
                added_stun = False
                counter = 1
                for frame_data in frame_datas:
                    fd = frame_data
                    if not added_stun:
                        stuns.append((fd.bstun, fd.hstun, fd.cstun, fd.imp, timer))
                        added_stun = True
                    if len(frame_datas) > 1:
                        #fractions = {(1, 2) : '⅓', (1, 2) : '⅓',}
                        fd.notes.append('½')#.format(counter, len(frame_datas)))
                    pretty_frame_data_entry(fd)
                    counter += 1
                return strings



    def FormatFrameString(p_str, p : SoulCaliburGameState.PlayerSnapshot):
        b, h, c, t = FrameAnalyzer.CalculateFrameAdvantage(p)
        str = "FDO:{}:{:^4}|{:^7}|{:^4}|{:^2}|{:^7}|{:^7}|{:^7}|{:^4}|{:^4}|{:^1}|{:^4}|".format(
                                                        p_str,
                                                        p.movement_block.movelist_id,
                                                        p.movelist.get_command_by_move_id(p.movement_block.movelist_id)[-7:],
                                                        p.startup_block.startup_frames + 1,
                                                        p.startup_block.attack_type,
                                                        b,
                                                        h,
                                                        c,
                                                        p.startup_block.damage,
                                                        p.startup_block.guard_damage,
                                                        p.startup_block.end_of_active_frames - p.startup_block.startup_frames,
                                                        t,
                                                      )

        return p.movement_block.movelist_id, b, h, c, t, [str]

class FrameAnalyzer:
    def CalculateFrameAdvantage(p : SoulCaliburGameState.PlayerSnapshot):
        uncanceled_frames = p.global_block.total_animation_frames
        cancelable = p.global_block.end_of_move_cancelable_frames
        startup = p.startup_block.startup_frames
        block_stun = p.startup_block.block_stun
        hit_stun = p.startup_block.hit_stun
        counter_stun = p.startup_block.counterhit_stun
        total_frames = uncanceled_frames - cancelable

        on_block = total_frames - (startup + block_stun)
        on_hit = total_frames - (startup + hit_stun)
        on_counter = total_frames - (startup + counter_stun)

        b, h, c = FrameAnalyzer.StringifyAdvantage(on_block), FrameAnalyzer.StringifyAdvantage(on_hit), FrameAnalyzer.StringifyAdvantage(on_counter)
        if p.startup_block.hit_launch != GameplayEnums.LaunchType.none.name:
            if p.startup_block.hit_launch != GameplayEnums.LaunchType.THROW.name:
                h = '{} {}'.format(p.startup_block.hit_launch, h)
            else:
                h = '{}'.format(p.startup_block.hit_launch)
        if p.startup_block.counter_launch!= GameplayEnums.LaunchType.none.name:
            if p.startup_block.counter_launch != GameplayEnums.LaunchType.THROW.name:
                c = '{} {}'.format(p.startup_block.counter_launch, c)
            else:
                c = '{}'.format(p.startup_block.counter_launch)
        if not p.startup_block.has_counterhit_properties:
            c = ''

        return b, h, c, total_frames
        #return b, h, c, cancelable

    def StringifyAdvantage(f : int):
        flipped = f * -1
        if flipped >= 0:
            return '+{}'.format(flipped)
        else:
            return '{}'.format(flipped)

    def CalculateCarriedAdvantage(movelist, move_ids, stuns):
        weights = []
        apply_blockstuns = []
        for i, move_id in enumerate(move_ids):
            if move_id < len(movelist.all_moves) and move_id >= 0:
                if i < len(move_ids) - 1:
                    weight, is_block_stun_applied = movelist.all_moves[move_id].get_weight_to_move_id(move_ids[i + 1])
                    weights.append(weight)
                    apply_blockstuns.append(is_block_stun_applied)
                else:
                    weight = movelist.all_moves[move_id].get_no_hitbox_startup()
                    weights.append(weight)
                    apply_blockstuns.append(False)
                    #weights.append(weight)
            else:
                weights.append(None)
                apply_blockstuns.append(False)

        current_balance = 0
        current_stun = ((0, 0, 0))

        for i in range(1, len(weights)):
            weight = weights[-i]
            stun = stuns[-i]
            if weight != None:
                #print(weight)
                current_balance += weight
            else:
                break
            if apply_blockstuns[-i] and stun != (0, 0, 0):
                #print(stun)
                current_stun = stun
                break

        #print(current_balance)
        #print(current_stun)
        #print(weights)
        tuple =(current_balance, ) + current_stun
        #print(tuple)
        return tuple





class FrameBackCounter:
    def __init__(self, is_p1):
        self.is_p1 = is_p1
        self.total_frames = 0
        self.current_frame = 9999

    def reset(self, total, current_frame, snapshots : List[SoulCaliburGameState.GameSnapshot]):
        if self.current_frame < self.total_frames: #if we haven't printed any frames, we print them now
            self.retrospective(snapshots)
        self.total_frames = total
        self.current_frame = current_frame


    def update(self, snapshots : List[SoulCaliburGameState.GameSnapshot]):
        self.current_frame += 1
        if self.current_frame == self.total_frames:
            self.retrospective(snapshots)

    def retrospective(self, snapshots : List[SoulCaliburGameState.GameSnapshot]):
        if self.current_frame < len(snapshots):
            crouching = lambda s: s.global_block.is_currently_crouching
            TC = self.backfill_for_func('TC', crouching, snapshots)
            jumping = lambda s: s.global_block.is_currently_jumping
            TJ = self.backfill_for_func('TJ', jumping, snapshots)
            guard_impacting = lambda s: s.global_block.is_currently_guard_impacting
            GI = self.backfill_for_func('GI', guard_impacting, snapshots)
            armoring = lambda s: s.global_block.is_currently_armoring
            ARM = self.backfill_for_func('REV', armoring, snapshots)
            if self.is_p1:
                p = 'p1:'
            else:
                p = 'p2:'
            format_string = 'NOTE:{} {} {} {} {}'
            note_string = format_string.format(p, ARM, GI, TC, TJ)
            if len(note_string) > len(format_string.replace('{', '').replace('}', '')):
                print(note_string)

    def backfill_for_func(self, string, func, snapshots):
        old_string = string
        toggle = False

        for i in reversed(range(1, self.current_frame)):
            if self.is_p1:
                s = snapshots[-i].p1
            else:
                s = snapshots[-i].p2
            c = func(s)
            if not toggle and c:
                toggle = True
                string += '[{}-'.format(s.movement_block.move_counter)
            if toggle and not c:
                toggle = False
                string += '{}]'.format(s.movement_block.move_counter)
        if string != old_string:
            return string
        else:
            return ""


if __name__ == "__main__":
    launcher = GameStateManager()
    while(True):
        launcher.Update(False, False)
        time.sleep(.05)
