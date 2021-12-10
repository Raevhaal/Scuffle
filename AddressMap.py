import ConfigReader

offset_module = 0x03EC14D0 #The first value on the cheat engine pointers
offset_players_pointer_A = 0x08
offset_players_pointer_B = 0x520
offset_player_1_object = 0x390
offset_player_2_object = 0x3A0
offset_movement_type_block = 0x160
offset_timer_block = 0x110

#The following addresses are all global (green adresses in cheat engine)
global_timer_address = 0x45846AC #there's a bunch of these, 4 bytes ; should go up until training mode is reset (goes to 0).

p1_input_address = 0x45865A0
p2_input_address = 0x461D5D0

p1_movelist_address = 0x45C96A0 #p1/p2 movelist address: xianghua movelist starting bytes: 4B 48 31 31 00 00 00 00 00 00 00 00 99 0B 2D 00 38 43 03 00 48 D2 03 00 90 D2 03 00 00 00 3B 02 = (alternate bytes for 0th move indes: 3B 02 22 00 5D 02 09 07 66 09 33 02 86 1A 40 00 67 00 00 00 00 00 00 00 00 00 C8 42 00 00 C8 42 FF FF 00 00 00 00 00 00)
p2_movelist_address = 0x46606D0 #other starting bytes available in /movelists although they may have changed slightly if the patch touches the movelist

p1_move_id_address = 0x45C8A52 #xianghua aab is 257/259/262 #there's a lot, pick the third one (or the one with immediate response time and that goes to '89' while transitioning from 8 way run to standing still)
p2_move_id_address = 0x465FA82

p1_guard_damage_address = 0x457BFE8 #xianghua aab is 4/4/16
p2_guard_damage_address = 0x457C1C8



MOVELIST_BYTES = 0x150000 #memory allocated for movelist,


#For address.ini testing
#global_timer_address = 0
#p1_input_address = 0
#p2_input_address = 0
#p1_move_id_address = 0
#p2_movelist_address = 0
#p1_guard_damage_address = 0
#p2_guard_damage_address = 0
#p1_move_id_address = 0
#p2_move_id_address = 0

#Read/Write the config file
address_config = ConfigReader.ConfigReader('address_map')
#section_players = 'Trail To Players Data'
#offset_players_pointer_A = address_config.get_hex_property(section_players, 'players_data_block_offset_A', offset_players_pointer_A)
#offset_players_pointer_B = address_config.get_hex_property(section_players, 'players_data_block_offset_B', offset_players_pointer_B)
#offset_player_1_object = address_config.get_hex_property(section_players, 'player_1_offset', offset_player_1_object)
#offset_player_2_object = address_config.get_hex_property(section_players, 'player_2_offset', offset_player_2_object)

#section_block = 'Player Data Block Constants'
#offset_movement_type_block = address_config.get_hex_property(section_block, 'movement_block', offset_movement_type_block)
#offset_timer_block = address_config.get_hex_property(section_block, 'timer_block', offset_timer_block)

section_global = 'Global Addresses'
address_config.add_comment('SCUFFLE relies on these values to find its data.')
address_config.add_comment('After an update or patch, the values may change.')
address_config.add_comment('However they can be found again with cheat engine.')
address_config.add_comment('')
address_config.add_comment('All these addresses are global which means they are *green* in cheat engine and will be located at the bottom of the list of matching addresses.')
address_config.add_comment('')
address_config.add_comment('Global Timer (4 bytes): The timer ticks up by 1 every frame and resets to 0 when training mode is reset. There seem to be multiple of these, perhaps all equally good?')
global_timer_address = address_config.get_hex_property(section_global, 'global_timer', global_timer_address)

address_config.add_comment("p1/p2 Input Address (2 bytes): Input address can be found by holding buttons down. 0 for no button, 1 for A, 2 for B, 4 for K, and 8 for G. Combinations are added together. The second part of the input buffer is direction held, so don't hold any directions. Don't use the first global address, it picks up inputs for both p1 and p2 in training mode.")
p1_input_address = address_config.get_hex_property(section_global, 'p1_input_buffer', p1_input_address)
p2_input_address = address_config.get_hex_property(section_global, 'p2_input_buffer', p2_input_address)


address_config.add_comment("p1/p2 Movelist Address (8 bytes): p1/p2 movelist address: xianghua movelist starting bytes: 4B 48 31 31 00 00 00 00 00 00 00 00")
address_config.add_comment("p1/p2 Movelist Address: 1. Pick Xianghua for p1 and p2 2. Search for that byte array 3. Search for a global address that points to the address of that array. 4.There should be four addresses, use the 1st for p1 and 3rd for p2")
p1_movelist_address = address_config.get_hex_property(section_global, 'p1_movelist_address', p1_movelist_address)
p2_movelist_address = address_config.get_hex_property(section_global, 'p2_movelist_address', p2_movelist_address)


address_config.add_comment("p1/p2 Move Id (2 bytes): Xianghua's a/a/b string has move ids 257/259/262.")
address_config.add_comment("p1/p2 Move Id: There will be multiple matches, pick the third green address.")
address_config.add_comment("p1/p2 Move Id: Alternately you are looking for a match that responds without delay and briefly shows '89' while transitioning from 8-way run to standing.")
p1_move_id_address = address_config.get_hex_property(section_global, 'p1_move_id_address', p1_move_id_address)
p2_move_id_address = address_config.get_hex_property(section_global, 'p2_move_id_address', p2_move_id_address)

address_config.add_comment("p1/p2 Guard Damage (2 bytes): Xianghua's a/a/b string has gdam 4/4/16. A+B has guard damage 38.")
p1_guard_damage_address = address_config.get_hex_property(section_global, 'p1_guard_damage_address', p1_guard_damage_address)
p2_guard_damage_address = address_config.get_hex_property(section_global, 'p2_guard_damage_address', p2_guard_damage_address)




address_config.write()

#Assemble all the relative addresses together
test_breadcrumb = [offset_module, offset_players_pointer_A, offset_players_pointer_B]

p1_movement_block_breadcrumb = [offset_module, offset_players_pointer_A, offset_players_pointer_B, offset_player_1_object, offset_movement_type_block]#xianghua's aab is 257/259/262
p2_movement_block_breadcrumb = [offset_module, offset_players_pointer_A, offset_players_pointer_B, offset_player_2_object, offset_movement_type_block]

p1_startup_block_breadcrumb = [offset_module, offset_players_pointer_A, offset_players_pointer_B, offset_player_1_object] #xianghua's AAB is 10/16/25
p2_startup_block_breadcrumb = [offset_module, offset_players_pointer_A, offset_players_pointer_B, offset_player_2_object]

p1_timer_block_breadcrumb = [offset_module, offset_players_pointer_A, offset_players_pointer_B, offset_player_1_object, offset_timer_block]#xianghua's AAB is 123/65/433
p2_timer_block_breadcrumb = [offset_module, offset_players_pointer_A, offset_players_pointer_B, offset_player_2_object, offset_timer_block]

#No longer used but possible to recover if needed:
'''
#p1_last_attack_address = 0x1445A7460 #for Tira A is 0x3730, K is 0x5aa0 and A+B is 0x62f0, search for the increase/decrease from one to the next #xianghua's AAB is 0x42b8/0x4408/0x45c8
#p2_last_attack_address = 0x14463E170

#p1_last_move_address = 0x1445A7460 #xianghua's 5k : 40 50 11 00 00 00 00 00 64 00 00 00 00 00 64 00 00 00 00 00 64 00 00 00 00 00 64 00 00 00 00 00 50 00 00 00 B0 FF 6E 00
#p2_last_move_address = 0x14463E170

#p1_is_currently_jumping_address = 0x1445F8B84 # 4 bytes 01 00 00 00 when jumping, 00 when not
#p2_is_currently_jumping_address = 0x14468F894

#p1_is_currently_crouching_address = 0x1445F8B88 # same as above but for crouching, can probably search for both together with 8 byte array
#p2_is_currently_crouching_address = 0x14468F898

#p1_is_currently_guard_impacting = 0x144563E40 # 8 byte boolean, 1 when guard impacting, 0 the rest of the time; use ivy's super or xianghua's b+k spinny one for enough frames to pause reliably
#p2_is_currently_guard_impacting = 0x1445FAB50

#p1_is_currently_armoring = 0x1445652DC #8 byte boole, 1 when armoring, else 0; use nightmare super or 6A or 6K
#p2_is_currently_armoring = 0x1445FBFEC

p1_end_of_move_cancelable_frames = 0x14455B3D0 #for tira AA is 11/12, this is 0 when no move is active #for xianghua's AAB it's 5/6/4
p2_end_of_move_cancelable_frames = 0x14455B5B0

p1_total_animation_frames = 0x1445A7D80 #for Tira AA is 52/56, remember this is a FLOAT #for xianghua's aab 46/55/62
p2_total_animation_frames = 0x14463EA90
'''





