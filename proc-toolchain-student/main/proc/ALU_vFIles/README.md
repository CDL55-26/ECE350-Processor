# ALU
## Carter Levine (CDL55)

## Description of Design
There are four major operations done by the ALU with three attached flag bits.

The flag bits are:
* Oveflow
* isLessThan
* notEqualTo.

Overflow was calculated by Xor'ing the carry-in and carry-out bits of the most significant full adder. If bits didn't matach, Overlow was set high

isLessThan was calculated after subtraction. If the leading bit of the output was a 1 and there was no overflow, A < B. Else if the MSB of A was 1 and Overflow was high, then A must have been less than B (not reflected by just looking at the MSB of the output)

notEqualTo was calculated using cascading Or gates. After subtraction, the output would be zero if A and B were equal, so I Or'd all of the bits of the output and if any of them were 1 (indicating not zero) then notEqualTo was set high.

The adder used was a 2-level Carry Look Ahead adder. Like a ripple carry, the main unit was the full adder. However, the carrybits were all calculated before hand, rather than rippled into each adder. 

I built 4, 8-bit CLA's and then connected them together using another CLA framework, making it two level. As such, there were nor rippled carry bits and the carry out of each CLA 8-bit unit were calculated in parallel. 

For subtraction, used a unit that would act as a buffer if the opcode signified Add or would Xor all of the bits with 1 if Subtract was signified, flipping the bits for two's compliment.

I used a 32 barrel shifter for the left and right shifts. The shifter was comprised of smaller,1-bit, 2-bit, 4-bit, 8-bit, and 16-bit shifters, which either shifted or acted as buffers depending on the shift amount.

I implemented the arithmetic shift by assigning the MSB of the input to a wire and then used that wire for the incoming bits.

The bitwise AND and bitwise OR were straightforward and consisted of 32 and gates and 32 or gates that ran in parallel.

The final ALU output was controlled by a 4 input mux, who's select bits came from the opcode. 

## Bugs
I have not found any bugs and the ALU is passing all of the gradescope test cases. However, I spent a while making sure the logic for the isLessThan flag bit was correct.