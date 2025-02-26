# MultDiv Unit

For the multdiv checkpoint, I implemented an unmodified Booths algorithm and a non-restoring binary division algorithm.

## Multiplier

For the multiplier, I implemented Booth's unmodified algorithm using a 65 bit register to hold the accumulator values, product values, and shift out bit. 

I used an arithmetic right shifter to shift the register output and I used a 6-bit TFF counter to assert the dataRDY flag. I used a 6 bit and not 5 bit counter because I was having issues with timing, stopping one cycle early. As such, I added one more TFF and used the 6th TFF to assert when the operation was ready.

## Divider

For the divider, I implemented the non-restoring algorithm, utilizing a very similar setup to that of the multiplier. I used a 64 bit register to hold the accumulator and quotient values and the same TFF clock to assert when the data was ready. Because we were not outputting the remainder of the division, I didn't restore the value on the last cycle and just outputed the lower 32 bits of the register.

## MultDiv

When I combined the two operators, I used a DFF to hold the state of whether a mult or div operation was currently be executed. I then used this value as the select bit for several muxes to output either the multiplication or division results.