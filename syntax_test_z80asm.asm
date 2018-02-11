; SYNTAX TEST "Packages/z80asm/z80asm.sublime-syntax"

; This is a comment
; <- comment

romstart:    jp       start                ; $0000 c3 00 10        ; called from: $22bd
; <- entity.name.label
;            ^ keyword.control
;                                          ^ comment

             defb     $cd,$31,$2e,$31,$00                          ; .1.1.      ; 
;                     ^constant.numeric
;                        ^ punctuation.separator
;                         ^constant.numeric
;                            ^ punctuation.separator
;                             ^constant.numeric
;                                 ^constant.numeric
;                                                                  ^ comment

             defb     $c3,$0f,$2a,$c3,$52,$25,$c3,$a5,$2a,$c3      ; ..*.R%..*. ; 
;                                                                  ^ comment

             ld       a,(hl)               ; $0008 7e              ; called from: $0c7c, $0d43, $0d45, $0e17, $0e2b, $0e61,
;            ^ keyword.control
;                     ^ variable.parameter
;                        ^ variable.parameter
;                                                                  ^ comment

             jr       nz,loop00e0          ; $00ec 20 f2           ; 
;                     ^ keyword.operator.logical

             defc     basexec=$4889
