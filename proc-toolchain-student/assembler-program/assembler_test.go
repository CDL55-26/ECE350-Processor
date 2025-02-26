package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

const testDirectory = "test"

var testISA ISA

var testFiles []string

func TestAssembler(t *testing.T) {

	for testIndex := 0; testIndex < len(testFiles); testIndex++ {
		assembledFile := readFile(testFiles[testIndex] + ".mem")

		fmt.Printf("Testing: %s\n", testFiles[testIndex])
		got := assemble(readFile(testFiles[testIndex]+".s"), testISA, "2", 4096)

		for i := range assembledFile {

			if i >= len(got) && assembledFile[i] != NOP && assembledFile[i] != "" {
				t.Errorf("Assembly of %s.s failed on line %d: Expected %s, got %s.", testFiles[testIndex], i, assembledFile[i], NOP)
			} else if i < len(got) && assembledFile[i] != got[i] {
				t.Errorf("Assembly of %s.s failed on line %d: Expected %s, got %s.", testFiles[testIndex], i, assembledFile[i], got[i])
			}
		}
	}

}

func TestMain(m *testing.M) {

	// load embedded isa
	isaInstructions := unmarshalInstructions(readEmbeddedCSV(instructionsFile))

	// load defualt register aliases from embedded file
	registerAliases := unmarshalRegisters(readEmbeddedCSV(registersFile))

	testISA = ISA{isaInstructions, registerAliases}

	err := filepath.WalkDir(testDirectory, func(path string, d os.DirEntry, err error) error {
		if strings.HasSuffix(d.Name(), ".s") {
			testFiles = append(testFiles, testDirectory+"/"+strings.TrimSuffix(d.Name(), ".s"))
		}
		return nil
	})
	if err != nil {
		log.Fatalf("Failed to load files in test directory %s", testDirectory)
	}

	os.Exit(m.Run())
}
