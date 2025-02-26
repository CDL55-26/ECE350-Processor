package main

import (
	"errors"
	"fmt"
	"log"
	"strconv"
	"strings"
)

const NOP string = "00000000000000000000000000000000"

type ISA struct {
	instructions    map[string]Instruction
	registerAliases map[string]int
}

var isa ISA

var routines map[string]int

var lineNum int = 0

func assemble(assemblyFile []string, assemblerISA ISA, outputBase string, outputLength int) []string {
	isa = assemblerISA
	routines = make(map[string]int)

	var cleanedFile []string

	lineNum = 0

	// clean the assembly file and parse routines
	for i := 0; i < len(assemblyFile); i++ {

		instr := assemblyFile[i]

		fields := strings.Fields(strings.ReplaceAll(instr, ",", ""))

		if len(fields) == 0 || strings.HasPrefix(fields[0], ".") {
			continue
		}

		// check if instruction defines a routine
		if strings.HasSuffix(fields[0], ":") {
			routines[strings.TrimSuffix(fields[0], ":")] = lineNum

			if len(fields) > 1 {
				fields = append(make([]string, 0), fields[1:]...)
			} else {
				continue
			}

		}

		// clean comments
		for j := 0; j < len(fields); j++ {
			if strings.HasPrefix(fields[j], "#") {
				fields = append(make([]string, 0), fields[:j]...)
				break
			}
		}

		if fields != nil && len(fields) > 0 {
			cleanedFile = append(cleanedFile, strings.Join(fields, " "))
			lineNum++
		}
	}

	// assemble the instructions
	var assembledInstrs []string
	lineNum = 0

	for _, instr := range cleanedFile {

		fields := strings.Fields(strings.ReplaceAll(instr, ",", ""))

		// fmt.Println(fields)

		assembledInstr := assembleInstruction(fields)

		if outputBase == "16" {
			var err error
			parsed_val, err := strconv.ParseInt(assembledInstr, 2, 64)
			if err != nil {
				log.Fatalf("Could not parse assembled binary %s instruction %s into decimal\n", assembledInstr, instr)
			}

			assembledInstr = fmt.Sprintf("%x", parsed_val)
		}

		assembledInstrs = append(assembledInstrs, assembledInstr)
		lineNum++
	}

	for len(assembledInstrs) < outputLength {
		assembledInstrs = append(assembledInstrs, NOP)
	}

	return assembledInstrs
}

func assembleInstruction(instruction []string) string {

	instrType := isa.instructions[instruction[0]].instrType

	switch instrType {
	case "R":
		return assembleRType(instruction)
	case "I":
		return assembleIType(instruction)
	case "JI":
		return assembleJIType(instruction)
	case "JII":
		return assembleJIIType(instruction)
	case "nop":
		return NOP
	default:
		log.Fatalf("Assembler does not support instruction %s with type %s.\n", strings.Join(instruction, " "), instrType)
	}

	return NOP
}

func assembleRType(instruction []string) string {

	// if len(instruction) != 4 {
	// 	log.Fatalf("Invalid arguments for instruction %s", strings.Join(instruction, " "))
	// }

	regs := make([]int, 3)

	for i := range regs {
		if i == 2 && (instruction[0] == "sll" || instruction[0] == "sra") {
			regs[i] = 0
			break
		}

		reg, err := loadRegister(instruction[i+1])
		if err != nil {
			log.Fatalf("Invalid register alias %s for instruction: %s\n", instruction[i+1], strings.Join(instruction, " "))
		}
		regs[i] = reg
	}

	shamt, err := strconv.Atoi(instruction[3])
	if err != nil && (instruction[0] == "sll" || instruction[0] == "sra") {
		log.Fatalf("Invalid shamt for instruction: %s\n", instruction)
	}

	alu_opcode := isa.instructions[instruction[0]].opcode

	assembledInstr := fmt.Sprintf("00000%05b%05b%05b%05b%s00", regs[0], regs[1], regs[2], shamt, alu_opcode)

	return assembledInstr
}

func assembleIType(instruction []string) string {

	var standardizedInstr []string
	if instruction[0] == "sw" || instruction[0] == "lw" {
		pieces := strings.Split(instruction[2], "(")

		standardizedInstr = []string{instruction[0], instruction[1], strings.TrimSuffix(pieces[1], ")"), pieces[0]}
	} else {
		standardizedInstr = instruction
	}

	regs := make([]int, 2)

	for i := range regs {
		reg, err := loadRegister(standardizedInstr[i+1])
		if err != nil && standardizedInstr[0] != "sll" && standardizedInstr[0] != "sra" {
			log.Fatalf("Invalid register alias %s for instruction: %s\n", standardizedInstr[i+1], strings.Join(instruction, " "))
		}
		regs[i] = reg
	}

	var immed int

	if routineLineNum, ok := routines[standardizedInstr[3]]; ok {
		immed = routineLineNum - lineNum - 1
	} else {
		var err error
		immed, err = strconv.Atoi(standardizedInstr[3])
		if err != nil {
			log.Fatalf("Invalid immediate for instruction: %s\n", standardizedInstr)
		}
	}

	signed_immed := fmt.Sprintf("%017b", uint(immed))

	opcode := isa.instructions[standardizedInstr[0]].opcode

	assembledInstr := fmt.Sprintf("%s%05b%05b%s", opcode, regs[0], regs[1], signed_immed[len(signed_immed)-17:])

	return assembledInstr
}

func assembleJIType(instruction []string) string {
	opcode := isa.instructions[instruction[0]].opcode

	var immed int

	if routineLineNum, ok := routines[instruction[1]]; ok {
		immed = routineLineNum
	} else {
		var err error
		immed, err = strconv.Atoi(instruction[1])
		if err != nil {
			log.Fatalf("Invalid immediate for instruction: %s\n", strings.Join(instruction, " "))
		}
	}

	signed_immed := fmt.Sprintf("%027b", uint(immed))

	assembledInstr := fmt.Sprintf("%s%s", opcode, signed_immed[len(signed_immed)-27:])

	return assembledInstr
}

func assembleJIIType(instruction []string) string {
	opcode := isa.instructions[instruction[0]].opcode

	reg, err := loadRegister(instruction[1])
	if err != nil {
		log.Fatalf("Invalid register alias %s for instruction: %s\n", instruction[1], strings.Join(instruction, " "))
	}

	assembledInstr := fmt.Sprintf("%s%05b%022d", opcode, reg, 0)

	return assembledInstr
}

/*
 * Attempts to load register address based on alias
 */
func loadRegister(alias string) (int, error) {
	if regnum, ok := isa.registerAliases[strings.ReplaceAll(alias, "$", "")]; ok {
		return regnum, nil
	} else {
		return 0, errors.New("Invalid register alias")
	}
}
