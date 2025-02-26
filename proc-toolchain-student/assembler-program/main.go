package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
)

func main() {
	if len(os.Args) < 2 {
		log.Fatal("Input program not specified. Please specify the name of one (or more) assembly programs.")
	}

	customInstructions := flag.String("i", "", "a custom instructions file")
	customRegisterMap := flag.String("r", "", "a custom registermap file")
	outputLength := flag.Int("l", 4096, "number of 32-bit words in output file")
	outputBase := flag.String("b", "2", "output base of instructions (2 or 16)")
	outputFileFlag := flag.String("o", "", "name of file to output")
	flag.Parse()

	if *outputLength <= 0 {
		log.Fatal("Length of output file must be greater than 0")
	}

	if *outputBase != "2" && *outputBase != "16" {
		fmt.Printf("Output base %s not supported. Defaulting to base 2\n", *outputBase)
		*outputBase = "2"
	}

	// load embedded isa
	isaInstructions := unmarshalInstructions(readEmbeddedCSV(instructionsFile))

	// load any additional custom instructions from file and replace any existing isa instructions
	if *customInstructions != "" {
		customInstructions := unmarshalInstructions(readCSV(*customInstructions))

		for k, v := range customInstructions {
			isaInstructions[k] = v
		}
	}

	// load defualt register aliases from embedded file
	registerAliases := unmarshalRegisters(readEmbeddedCSV(registersFile))

	// set any additional register aliases specified
	if *customRegisterMap != "" {
		customRegisterAliases := unmarshalRegisters(readCSV(*customRegisterMap))

		for k, v := range customRegisterAliases {
			registerAliases[k] = v
		}
	}

	// create ISA struct
	isa := ISA{isaInstructions, registerAliases}

	// load assembly file from arguments
	assemblyFile := flag.Args()[0]

	assembledFile := assemble(readFile(assemblyFile), isa, *outputBase, *outputLength)

	// write assembled program to file
	var outputFilename string
	if *outputFileFlag != "" {
		outputFilename = *outputFileFlag
	} else {
		outputFilename = fmt.Sprintf("%s.mem", strings.TrimSuffix(assemblyFile, ".s"))
	}

	writeFile(outputFilename, assembledFile)

}
