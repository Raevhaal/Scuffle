import AddressMap

from ByteTools import *
import ModuleEnumerator
import PIDSearcher
import GameplayEnums
import MovelistParser

class SC6GameReader:
        def __init__(self):
            self.pid = -1
            self.snapshots = []
            self.p1_movelist = None
            self.p2_movelist = None
            self.timer = 0
            self.do_write_movelist = False
            self.is_movelist_new = False
            self.consecutive_frames_of_zero_timer = 0
            
            #self.module_address = 0x140000000 #hard coding this until it breaks, then use ModuleEnumerator again
            #self.module_address = 0x7FF60AC30000 #new hardcoded
            
            self.module_address = 0

        def IsForegroundPID(self):
            pid = c.wintypes.DWORD()
            active = c.windll.user32.GetForegroundWindow()
            active_window = c.windll.user32.GetWindowThreadProcessId(active, c.byref(pid))
            return pid.value == self.pid

        def GetWindowRect(self):
            # see https://stackoverflow.com/questions/21175922/enumerating-windows-trough-ctypes-in-python for clues for doing this without needing focus using WindowsEnum
            if self.IsForegroundPID():
                rect = c.wintypes.RECT()
                c.windll.user32.GetWindowRect(c.windll.user32.GetForegroundWindow(), c.byref(rect))
                return rect
            else:
                return None

        def HasWorkingPID(self):
            return self.pid > -1

        def VoidPID(self):
            self.pid = -1

        def VoidMovelists(self):
            self.p1_movelist = None
            self.p2_movelist = None

        def MarkMovelistAsOld(self):
            self.is_movelist_new = False

        def HasNewMovelist(self):
            return self.is_movelist_new


        def UpdateCurrentSnapshot(self):
            if not self.HasWorkingPID():
                self.pid = PIDSearcher.GetPIDByName(b'SoulcaliburVI.exe')
                if self.HasWorkingPID():
                    print("Soul Calibur VI process id acquired: {}".format(self.pid))
                else:
                    print("Failed to find processid. Trying to acquire...")

            if self.HasWorkingPID():
                process_handle = OpenProcess(0x10 | 0x20 | 0x08, False, self.pid) #0x10 = ReadProcess Privleges 0x20 = WriteProcess Privleges 0x08 = Operation Privleges

                self.module_address = ModuleEnumerator.GetModuleAddressByPIDandName(pid = self.pid, name = "SoulcaliburVI.exe")
                
                test_block = GetValueFromAddress(process_handle, self.module_address + AddressMap.global_timer_address)

                if test_block == 0: #not in a fight yet or application closed
                    self.consecutive_frames_of_zero_timer += 1
                    if self.consecutive_frames_of_zero_timer > 10:
                        self.VoidPID()
                        self.VoidMovelists()
                    return False
                else:
                    self.consecutive_frames_of_zero_timer = 0
                    if self.p1_movelist == None:
                        #movelist_sample = GetValueFromAddress(process_handle, AddressMap.p1_movelist_address, isString=True)
                        movelist_sample = GetDataBlockAtEndOfPointerOffsetList(process_handle, self.module_address, [AddressMap.p1_movelist_address], 0x4)
                        movelist_sample = GetValueFromDataBlock(movelist_sample, 0)

                        if  movelist_sample == MovelistParser.Movelist.STARTER_INT:
                            p1_movelist_data = GetDataBlockAtEndOfPointerOffsetList(process_handle, self.module_address, [AddressMap.p1_movelist_address], AddressMap.MOVELIST_BYTES)
                            p2_movelist_data = GetDataBlockAtEndOfPointerOffsetList(process_handle, self.module_address, [AddressMap.p2_movelist_address], AddressMap.MOVELIST_BYTES)
                            self.p1_movelist = MovelistParser.Movelist(p1_movelist_data, 'p1')
                            self.p2_movelist = MovelistParser.Movelist(p2_movelist_data, 'p2')
                            self.is_movelist_new = True
                        else:
                            return False

                    new_timer = GetValueFromAddress(process_handle, self.module_address + AddressMap.global_timer_address)

                    if self.timer == new_timer:
                        return False
                    else:
                        self.timer = new_timer


                    #p1_startup_block = GetDataBlockAtEndOfPointerOffsetList(process_handle, self.module_address, AddressMap.p1_startup_block_breadcrumb, 0x100)
                    #p2_startup_block = GetDataBlockAtEndOfPointerOffsetList(process_handle, self.module_address, AddressMap.p2_startup_block_breadcrumb, 0x100)

                    #p1_movement_block = GetDataBlockAtEndOfPointerOffsetList(process_handle, self.module_address, AddressMap.p1_movement_block_breadcrumb, 0x100)
                    #p2_movement_block = GetDataBlockAtEndOfPointerOffsetList(process_handle, self.module_address, AddressMap.p2_movement_block_breadcrumb, 0x100)

                    p1_move_id = GetValueFromAddress(process_handle, self.module_address + AddressMap.p1_move_id_address, is_short =True)
                    p2_move_id = GetValueFromAddress(process_handle, self.module_address + AddressMap.p2_move_id_address, is_short=True)

                    p1_gdam = GetValueFromAddress(process_handle, self.module_address + AddressMap.p1_guard_damage_address, is_short=True)
                    p2_gdam = GetValueFromAddress(process_handle, self.module_address + AddressMap.p2_guard_damage_address, is_short=True)

                    p1_input = GetValueFromAddress(process_handle, self.module_address + AddressMap.p1_input_address, is_short =True)
                    p1_global = SC6GlobalBlock(p1_input)

                    p2_input = GetValueFromAddress(process_handle, self.module_address + AddressMap.p2_input_address, is_short=True)
                    p2_global = SC6GlobalBlock(p2_input)

                    value_p1 = PlayerSnapshot(self.p1_movelist, p1_gdam, p1_move_id, p1_global)
                    value_p2 = PlayerSnapshot(self.p2_movelist, p2_gdam, p2_move_id, p2_global)

                    if self.do_write_movelist:
                        p1_movelist_address = GetValueFromAddress(process_handle, self.module_address + AddressMap.p1_movelist_address, is64bit=True)
                        WriteBlockOfData(process_handle, p1_movelist_address, self.p1_movelist.generate_modified_movelist_bytes())
                        self.do_write_movelist = False
                        self.VoidPID()
                        self.VoidMovelists()

                    self.snapshots.append(GameSnapshot(value_p1, value_p2, self.timer))
                    MAX_FRAMES_TO_KEEP = 1000
                    if len(self.snapshots) > MAX_FRAMES_TO_KEEP:
                        self.snapshots = self.snapshots[MAX_FRAMES_TO_KEEP // 2: -1]
                    return True



class SC6MovementBlock:
    def __init__(self, move_id):
        self.movelist_id = move_id

class SC6StartupBlock:
    def __init__(self, gdam):
        self.guard_damage = gdam

class SC6GlobalBlock:
    def __init__(self, input_short):
        left_bytes = (input_short & 0xFF00) >> 8
        right_bytes = input_short & 0x00FF

        self.input_code_button = right_bytes
        self.input_code_direction = left_bytes

    def __repr__(self):
        repr = "{} | {} |".format(
            self.input_code_button, self.input_code_direction)
        return repr

class PlayerSnapshot:
    def __init__(self, movelist, gdam, move_id, global_block : SC6GlobalBlock):
        self.movelist = movelist
        self.movement_block = SC6MovementBlock(move_id)
        self.startup_block = SC6StartupBlock(gdam)
        self.global_block = global_block

class GameSnapshot:
    def __init__(self, p1_snapshot : PlayerSnapshot, p2_snapshot : PlayerSnapshot, timer):
        self.timer = timer
        self.p1 = p1_snapshot
        self.p2 = p2_snapshot

    def __repr__(self):
        return "{} ||| {}".format(self.p1, self.p2)


if __name__ == "__main__":
    import time
    import GameplayEnums
    myReader = SC6GameReader()
    old_state = None
    while True:
        successful_update = myReader.UpdateCurrentSnapshot()

        if successful_update:
            new_state = myReader.snapshots[-1]
            print("you're open {}".format(new_state.timer))

        time.sleep(.005)

