from enum import Enum


def enum_has_value(cls, value):
    return any(value == item.value for item in cls)

class Button(Enum):
    A = 0x01
    B = 0x02
    K = 0x04
    G = 0x08

    B_K = 0x06
    A_B = 0x03
    A_G = 0x09
    K_G = 0x0C

    A_B_K = 0x07


class PaddedButton(Enum):
    U = 0xAAAA
    RE = 0xAAAB

    A = 0x0001
    B = 0x0002
    K = 0x0004
    G = 0x0008

    B_K = 0x0600
    A_B = 0x0300
    A_G = 0x0900
    B_G = 0x0a00
    K_G = 0x0C00

    A_B_K = 0x0700

    Forward = 0x1008
    Forward_ALT = 0x3008

    d = 0x9999

    b = 0x002e
    h = 0x001b
    #c =
    dd = 0x0054

class InputType(Enum):
    Press = 0x06
    Hold = 0x20

    Direction_PRESS = 0x13AF
    Direction_HOLD = 0x13AE
    Direction_ALT = 0x0002
    No_SC_Press =0x8f #for when you're not in soul charge???


    OnContact = 0x0B #counter hit uses the same code signature but are about 3x as long so the counterhit part must be in there somewhere

    DoubleTap = 0x2C

    #PressDown = 0x13af /0x13ae ??
    #PressBack =  0x0002 /0x1002 ??
    #0x0120 #geralt, super?? + hold button




class CC(Enum): #Cancel codes for the cancel block, mostly we expect (CC XX XX CC XX XX ...) where CC is the cancel codes and XX is the variable provided to them
    UNK = 0x9999

    START = 0x01 #begins every block(?)
    END = 0x02  # this byte ends the block

    EXE_25 = 0x25 #all EXE blocks have the seecond argument as the number of instructions since the last non 8b/89 block (mostly true)
    EXE_19 = 0x19 #very common in neutral blocks
    EXE_A5 = 0xA5
    EXE_13 = 0x13 #very rare, yoshimitsu only???

    ARG_89 = 0x89 #the ARG blocks provide arguments to the EXE blocks
    ARG_8B = 0x8b
    ARG_8A = 0x8a #may not be an arg field???

    PEN_2A = 0x2A #the variables for these blocks stay the same or increase (although they may start in the middle of the block and 'wrap' around to the top)
    PEN_28 = 0x28
    PEN_29 = 0x29

    RETURN_00 = 0x00
    RETURN_03 = 0x03
    RETURN_04 = 0x04
    RETURN_05 = 0x05
    RETURN_07 = 0x07
    RETURN_08 = 0x08
    RETURN_0b = 0x0b
    RETURN_0d = 0x0d
    RETURN_0e = 0x0e
    RETURN_0f = 0x0f
    RETURN_10 = 0x10
    RETURN_12 = 0x12
    RETURN_13 = 0x13
    RETURN_14 = 0x14
    RETURN_1a = 0x1a
    RETURN_1b = 0x1b
    RETURN_1c = 0x1c
    RETURN_1e = 0x1e
    RETURN_23 = 0x23
    RETURN_32 = 0x32
    RETURN_42 = 0x42
    RETURN_4c = 0x4c
    RETURN_4d = 0x4d
    RETURN_5c = 0x5c
    RETURN_5d = 0x5d
    RETURN_61 = 0x61
    RETURN_68 = 0x68
    RETURN_6b = 0x6b
    RETURN_74 = 0x74
    RETURN_77 = 0x77
    RETURN_78 = 0x78
    RETURN_7a = 0x7a
    RETURN_7e = 0x7e
    RETURN_88 = 0x88
    RETURN_8c = 0x8c
    RETURN_8d = 0x8d
    RETURN_8e = 0x8e
    RETURN_8f = 0x8f
    RETURN_91 = 0x91
    RETURN_92 = 0x92
    RETURN_94 = 0x94
    RETURN_95 = 0x95
    RETURN_96 = 0x96
    RETURN_98 = 0x98
    RETURN_99 = 0x99
    RETURN_9e = 0x9e
    RETURN_9f = 0x9f
    RETURN_a0 = 0xa0
    RETURN_a1 = 0xa1
    RETURN_a2 = 0xa2
    RETURN_a3 = 0xa3
    RETURN_a4 = 0xa4
    RETURN_ab = 0xab
    RETURN_ac = 0xac
    RETURN_ad = 0xad
    RETURN_ae = 0xae
    RETURN_af = 0xaf
    RETURN_b1 = 0xb1
    RETURN_b3 = 0xb3
    RETURN_f0 = 0xf0
    RETURN_fb = 0xfb



