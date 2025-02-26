package main

import (
	_ "embed"
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"strings"
)

//go:embed instructions.csv
var instructionsFile string

//go:embed registers.csv
var registersFile string

type Instruction struct {
	name      string
	instrType string
	opcode    string
}

/*
 * Reads a csv file from disk
 */
func readCSV(filepath string) [][]string {
	f, err := os.Open(filepath)
	if err != nil {
		log.Fatal("Unable to load the input file "+filepath, err)
	}
	defer f.Close()

	reader := csv.NewReader(f)
	records, err := reader.ReadAll()
	if err != nil {
		log.Fatal("Unable to parse file for "+filepath, err)
	}

	return records
}

/*
 * Reads a csv file that has been embedded in the binary
 */
func readEmbeddedCSV(embeddedFile string) [][]string {
	reader := csv.NewReader(strings.NewReader(embeddedFile))
	records, err := reader.ReadAll()
	if err != nil {
		log.Fatal("Unable to embedded file ", err)
	}

	return records
}

/*
 * Reads a file and returns a slice with each line
 */
func readFile(filepath string) []string {
	f, err := os.Open(filepath)
	if err != nil {
		log.Fatalf("Unable to load the input file %s %s", filepath, err)
	}
	defer f.Close()

	filebytes, err := io.ReadAll(f)
	if err != nil {
		log.Fatal("Error reading assembly file ", err)
	}

	filestring := string(filebytes)

	file := strings.Split(filestring, "\n")

	return file
}

/*
 * Writes data to the file
 */
func writeFile(filepath string, data []string) {
	f, err := os.OpenFile(filepath, os.O_RDWR|os.O_CREATE, 0755)
	if err != nil {
		log.Fatalf("Unable to load the output file %s: %s", filepath, err)
	}
	defer f.Close()

	for _, line := range data {
		f.WriteString(fmt.Sprintf("%s\n", line))
	}
}

/*
 * Unmarshals the ISA instructions from csv format strings
 */
func unmarshalInstructions(records [][]string) map[string]Instruction {
	instructions := make(map[string]Instruction)

	for _, rawInstr := range records {
		instructions[rawInstr[0]] = Instruction{rawInstr[0], rawInstr[1], rawInstr[2]}
	}

	return instructions
}

/*
 * Unmarshals the register aliases into a map
 */
func unmarshalRegisters(records [][]string) map[string]int {
	registerMap := make(map[string]int)

	for register := range records {
		for _, alias := range records[register] {
			registerMap[alias] = register
		}
	}

	return registerMap
}

/*
 * Determines the maximum of (a,b)
 */
func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}
