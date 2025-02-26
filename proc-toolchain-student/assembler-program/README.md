## ECE350 MIPS Assembler

This program can assemble ECE350 limited-ISA MIPS assembly into machine code. The list of supported instructions can be found in the [instructions.csv](instructions.csv) file. The assembler also supports custom instructions which can be specified at runtime.

### Building the program
To build the program from source you will need to have golang installed. Alternatively you can download a prebuilt binary from the project's [package registry](https://gitlab.oit.duke.edu/ece350-ta/assembler-program/-/packages/529).

```
$ go build -o asm
```

### Using the program

```
$ ./asm [flags] <filename>
```

| Argument | Description |
| ------ | ------ |
| filename | name of the assembly file to assemble |

| Optional Flags | Description |
| ----- | ----------- |
| -o | name of the output file |
| -i | csv file containing custom instruction definitions |
| -r | csv file containing custom register aliases |
|-b | output base of instructions (only 2 or 16 supported). Defaults to binary. |
| -l | number of 32-bit words in output file |

*Note:* The flags must come before the name of the assembly file.

### Custom Instructions

Custom instructions should be defined in a .csv file. Each row specifies a single instruction 
and should match the following format: instruction, type, opcode.

For example:

```
print,J,11000
draw,R,11001
```

### Custom Register Aliases

You can define additional register aliases in another .csv file. The first column of the row
defines which register to assign aliases and following columns are all assigned as aliases.

For example:
```
2,sprite
3,reg3,register3,registerthree
```

This will set "sprite" to be an alias for register 2 and "reg3", "register3", and "registerthree"
to be aliases for register 3. Then these aliases can be used in the assembly files in place of the
register number.

```
add $three, $sprite, $reg3  # same as add $3, $2, $3
```

### Testing

The assembler can be run against a set of test files contained in the [test](/test) directory using the ```go test``` command.

### Creating releases

Since the assembler was written using Golang it needs to first be compiled. Rather than having students install golang just to compile the assembler we build the assembler for common OS/arch pairs and release the prebuilt binaries to the students. 

This process is simplified using the [release.sh](release.sh) script. Currently this script creates releases for Mac(Intel), Mac(M1), Windows 64-bit, and Linux 64-bit. There are additional combinations that can be added if necessary.

These releases should not be commited to the repository, however they are automatically uploaded to the project's [package registry](https://gitlab.oit.duke.edu/ece350-ta/assembler-program/-/packages) if you have an API key set when running the script.

Before running the release script you should increase the release number to keep the package registry organized.

```
$ export API_KEY=<your api key>
$ ./release.sh
```

These packages can then be added as Release Assets to a Gitlab release located at Deployments->Releases in the sidebar of the project.

Written by Jack Proudfoot