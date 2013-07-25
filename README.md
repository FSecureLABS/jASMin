An interactive command assembler for ARM and THUMB. Quite useful when creating exploits for Android.

$ ./jASMin.py 

    _   _   ___ __  __ _      
   (_) /_\ / __|  \/  (_)_ _  
   | |/ _ \\__ \ |\/| | | ' \ 
  _/ /_/ \_\___/_|  |_|_|_||_|
 |__/                                                                                                                                                          
     twist your droid's ARM    

Type 'help' or '?' to list commands
Separate instructions by ;

[mode]      ARM
[format]    ARRAY
[direction] ASM->HEX

> nop
0x00, 0x00, 0xa0, 0xe1
> mode
[mode]      THUMB
> nop
0xc0, 0x46
> load /home/user/Desktop/test.asm
0xc0, 0x46
