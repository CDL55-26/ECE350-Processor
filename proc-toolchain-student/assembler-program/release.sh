#!/bin/bash

# This script builds release binaries for common platforms

projectid="22311"
version="1.0.0"

mkdir -p releases

# 64-bit Mac (intel)
env GOOS=darwin GOARCH=amd64 go build -o releases/mac_intel/asm
cp release_instructions.txt releases/mac_intel/instructions.txt
cp test/sample.s releases/mac_intel/sample.s
zip -jvr releases/mac_intel.zip releases/mac_intel/ -x "*.DS_Store"

curl --header "PRIVATE-TOKEN: ${API_TOKEN}" \
     --upload-file releases/mac_intel.zip \
     "https://gitlab.oit.duke.edu/api/v4/projects/${projectid}/packages/generic/asm/${version}/mac_intel.zip?status=default"


# 64-bit Mac (m1)
env GOOS=darwin GOARCH=arm64 go build -o releases/mac_m1/asm
cp release_instructions.txt releases/mac_m1/instructions.txt
cp test/sample.s releases/mac_m1/sample.s
zip -jvr releases/mac_m1.zip releases/mac_m1/ -x "*.DS_Store"

curl --header "PRIVATE-TOKEN: ${API_TOKEN}" \
     --upload-file releases/mac_m1.zip \
     "https://gitlab.oit.duke.edu/api/v4/projects/${projectid}/packages/generic/asm/${version}/mac_m1.zip?status=default"


# 64-bit Windows
env GOOS=windows GOARCH=amd64 go build -o releases/windows/asm.exe
cp release_instructions.txt releases/windows/instructions.txt
cp test/sample.s releases/windows/sample.s
zip -jvr releases/windows.zip releases/windows/ -x "*.DS_Store"

curl --header "PRIVATE-TOKEN: ${API_TOKEN}" \
     --upload-file releases/windows.zip \
     "https://gitlab.oit.duke.edu/api/v4/projects/${projectid}/packages/generic/asm/${version}/windows.zip?status=default"


# 64-bit Linux
env GOOS=linux GOARCH=amd64 go build -o releases/linux/asm
cp release_instructions.txt releases/linux/instructions.txt
cp test/sample.s releases/linux/sample.s
zip -jvr releases/linux.zip releases/linux/ -x "*.DS_Store"

curl --header "PRIVATE-TOKEN: ${API_TOKEN}" \
     --upload-file releases/linux.zip \
     "https://gitlab.oit.duke.edu/api/v4/projects/${projectid}/packages/generic/asm/${version}/linux.zip?status=default"


#  As of 10/12/21 these are the supported GOOS/GOARCH combos
#    GOOS - Target Operating System| GOARCH - Target Platform
#    -------------------------------|--------------------------
#    |           android            |           arm           |  
#    |           darwin             |           386           |  
#    |           darwin             |           amd64         |    
#    |           darwin             |           arm           |  
#    |           darwin             |           arm64         |    
#    |           dragonfly          |           amd64         |    
#    |           freebsd            |           386           |  
#    |           freebsd            |           amd64         |    
#    |           freebsd            |           arm           |  
#    |           linux              |           386           |  
#    |           linux              |           amd64         |    
#    |           linux              |           arm           |  
#    |           linux              |           arm64         |    
#    |           linux              |           ppc64         |    
#    |           linux              |           ppc64le       |      
#    |           linux              |           mips          |   
#    |           linux              |           mipsle        |     
#    |           linux              |           mips64        |     
#    |           linux              |           mips64le      |       
#    |           netbsd             |           386           |  
#    |           netbsd             |           amd64         |    
#    |           netbsd             |           arm           |  
#    |           openbsd            |           386           |  
#    |           openbsd            |           amd64         |    
#    |           openbsd            |           arm           |  
#    |           plan9              |           386           |  
#    |           plan9              |           amd64         |    
#    |           solaris            |           amd64         |    
#    |           windows            |           386           |   
#    |           windows            |           amd64         |
#    ----------------------------------------------------------