# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.29

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /opt/homebrew/Cellar/cmake/3.29.1/bin/cmake

# The command to remove a file.
RM = /opt/homebrew/Cellar/cmake/3.29.1/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /Users/harker/Desktop/CS461/tiny_vm

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug

# Include any dependencies generated for this target.
include CMakeFiles/tiny_vm.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include CMakeFiles/tiny_vm.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/tiny_vm.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/tiny_vm.dir/flags.make

/Users/harker/Desktop/CS461/tiny_vm/vm_code_table.c: /Users/harker/Desktop/CS461/tiny_vm/opdefs.txt
/Users/harker/Desktop/CS461/tiny_vm/vm_code_table.c: /Users/harker/Desktop/CS461/tiny_vm/build_bytecode_table.py
/Users/harker/Desktop/CS461/tiny_vm/vm_code_table.c: /Users/harker/Desktop/CS461/tiny_vm/vm_code_table.h
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --blue --bold --progress-dir=/Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Generating /Users/harker/Desktop/CS461/tiny_vm/vm_code_table.c"
	python3 /Users/harker/Desktop/CS461/tiny_vm/build_bytecode_table.py /Users/harker/Desktop/CS461/tiny_vm/opdefs.txt /Users/harker/Desktop/CS461/tiny_vm/vm_code_table.c

CMakeFiles/tiny_vm.dir/cjson/cJSON.c.o: CMakeFiles/tiny_vm.dir/flags.make
CMakeFiles/tiny_vm.dir/cjson/cJSON.c.o: /Users/harker/Desktop/CS461/tiny_vm/cjson/cJSON.c
CMakeFiles/tiny_vm.dir/cjson/cJSON.c.o: CMakeFiles/tiny_vm.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building C object CMakeFiles/tiny_vm.dir/cjson/cJSON.c.o"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/tiny_vm.dir/cjson/cJSON.c.o -MF CMakeFiles/tiny_vm.dir/cjson/cJSON.c.o.d -o CMakeFiles/tiny_vm.dir/cjson/cJSON.c.o -c /Users/harker/Desktop/CS461/tiny_vm/cjson/cJSON.c

CMakeFiles/tiny_vm.dir/cjson/cJSON.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/tiny_vm.dir/cjson/cJSON.c.i"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /Users/harker/Desktop/CS461/tiny_vm/cjson/cJSON.c > CMakeFiles/tiny_vm.dir/cjson/cJSON.c.i

CMakeFiles/tiny_vm.dir/cjson/cJSON.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/tiny_vm.dir/cjson/cJSON.c.s"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /Users/harker/Desktop/CS461/tiny_vm/cjson/cJSON.c -o CMakeFiles/tiny_vm.dir/cjson/cJSON.c.s

CMakeFiles/tiny_vm.dir/main.c.o: CMakeFiles/tiny_vm.dir/flags.make
CMakeFiles/tiny_vm.dir/main.c.o: /Users/harker/Desktop/CS461/tiny_vm/main.c
CMakeFiles/tiny_vm.dir/main.c.o: CMakeFiles/tiny_vm.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Building C object CMakeFiles/tiny_vm.dir/main.c.o"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/tiny_vm.dir/main.c.o -MF CMakeFiles/tiny_vm.dir/main.c.o.d -o CMakeFiles/tiny_vm.dir/main.c.o -c /Users/harker/Desktop/CS461/tiny_vm/main.c

CMakeFiles/tiny_vm.dir/main.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/tiny_vm.dir/main.c.i"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /Users/harker/Desktop/CS461/tiny_vm/main.c > CMakeFiles/tiny_vm.dir/main.c.i

CMakeFiles/tiny_vm.dir/main.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/tiny_vm.dir/main.c.s"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /Users/harker/Desktop/CS461/tiny_vm/main.c -o CMakeFiles/tiny_vm.dir/main.c.s

CMakeFiles/tiny_vm.dir/vm_state.c.o: CMakeFiles/tiny_vm.dir/flags.make
CMakeFiles/tiny_vm.dir/vm_state.c.o: /Users/harker/Desktop/CS461/tiny_vm/vm_state.c
CMakeFiles/tiny_vm.dir/vm_state.c.o: CMakeFiles/tiny_vm.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_4) "Building C object CMakeFiles/tiny_vm.dir/vm_state.c.o"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/tiny_vm.dir/vm_state.c.o -MF CMakeFiles/tiny_vm.dir/vm_state.c.o.d -o CMakeFiles/tiny_vm.dir/vm_state.c.o -c /Users/harker/Desktop/CS461/tiny_vm/vm_state.c

CMakeFiles/tiny_vm.dir/vm_state.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/tiny_vm.dir/vm_state.c.i"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /Users/harker/Desktop/CS461/tiny_vm/vm_state.c > CMakeFiles/tiny_vm.dir/vm_state.c.i

CMakeFiles/tiny_vm.dir/vm_state.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/tiny_vm.dir/vm_state.c.s"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /Users/harker/Desktop/CS461/tiny_vm/vm_state.c -o CMakeFiles/tiny_vm.dir/vm_state.c.s

CMakeFiles/tiny_vm.dir/vm_ops.c.o: CMakeFiles/tiny_vm.dir/flags.make
CMakeFiles/tiny_vm.dir/vm_ops.c.o: /Users/harker/Desktop/CS461/tiny_vm/vm_ops.c
CMakeFiles/tiny_vm.dir/vm_ops.c.o: CMakeFiles/tiny_vm.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_5) "Building C object CMakeFiles/tiny_vm.dir/vm_ops.c.o"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/tiny_vm.dir/vm_ops.c.o -MF CMakeFiles/tiny_vm.dir/vm_ops.c.o.d -o CMakeFiles/tiny_vm.dir/vm_ops.c.o -c /Users/harker/Desktop/CS461/tiny_vm/vm_ops.c

CMakeFiles/tiny_vm.dir/vm_ops.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/tiny_vm.dir/vm_ops.c.i"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /Users/harker/Desktop/CS461/tiny_vm/vm_ops.c > CMakeFiles/tiny_vm.dir/vm_ops.c.i

CMakeFiles/tiny_vm.dir/vm_ops.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/tiny_vm.dir/vm_ops.c.s"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /Users/harker/Desktop/CS461/tiny_vm/vm_ops.c -o CMakeFiles/tiny_vm.dir/vm_ops.c.s

CMakeFiles/tiny_vm.dir/vm_code_table.c.o: CMakeFiles/tiny_vm.dir/flags.make
CMakeFiles/tiny_vm.dir/vm_code_table.c.o: /Users/harker/Desktop/CS461/tiny_vm/vm_code_table.c
CMakeFiles/tiny_vm.dir/vm_code_table.c.o: CMakeFiles/tiny_vm.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_6) "Building C object CMakeFiles/tiny_vm.dir/vm_code_table.c.o"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/tiny_vm.dir/vm_code_table.c.o -MF CMakeFiles/tiny_vm.dir/vm_code_table.c.o.d -o CMakeFiles/tiny_vm.dir/vm_code_table.c.o -c /Users/harker/Desktop/CS461/tiny_vm/vm_code_table.c

CMakeFiles/tiny_vm.dir/vm_code_table.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/tiny_vm.dir/vm_code_table.c.i"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /Users/harker/Desktop/CS461/tiny_vm/vm_code_table.c > CMakeFiles/tiny_vm.dir/vm_code_table.c.i

CMakeFiles/tiny_vm.dir/vm_code_table.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/tiny_vm.dir/vm_code_table.c.s"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /Users/harker/Desktop/CS461/tiny_vm/vm_code_table.c -o CMakeFiles/tiny_vm.dir/vm_code_table.c.s

CMakeFiles/tiny_vm.dir/builtins.c.o: CMakeFiles/tiny_vm.dir/flags.make
CMakeFiles/tiny_vm.dir/builtins.c.o: /Users/harker/Desktop/CS461/tiny_vm/builtins.c
CMakeFiles/tiny_vm.dir/builtins.c.o: CMakeFiles/tiny_vm.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_7) "Building C object CMakeFiles/tiny_vm.dir/builtins.c.o"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/tiny_vm.dir/builtins.c.o -MF CMakeFiles/tiny_vm.dir/builtins.c.o.d -o CMakeFiles/tiny_vm.dir/builtins.c.o -c /Users/harker/Desktop/CS461/tiny_vm/builtins.c

CMakeFiles/tiny_vm.dir/builtins.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/tiny_vm.dir/builtins.c.i"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /Users/harker/Desktop/CS461/tiny_vm/builtins.c > CMakeFiles/tiny_vm.dir/builtins.c.i

CMakeFiles/tiny_vm.dir/builtins.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/tiny_vm.dir/builtins.c.s"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /Users/harker/Desktop/CS461/tiny_vm/builtins.c -o CMakeFiles/tiny_vm.dir/builtins.c.s

CMakeFiles/tiny_vm.dir/vm_core.c.o: CMakeFiles/tiny_vm.dir/flags.make
CMakeFiles/tiny_vm.dir/vm_core.c.o: /Users/harker/Desktop/CS461/tiny_vm/vm_core.c
CMakeFiles/tiny_vm.dir/vm_core.c.o: CMakeFiles/tiny_vm.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_8) "Building C object CMakeFiles/tiny_vm.dir/vm_core.c.o"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/tiny_vm.dir/vm_core.c.o -MF CMakeFiles/tiny_vm.dir/vm_core.c.o.d -o CMakeFiles/tiny_vm.dir/vm_core.c.o -c /Users/harker/Desktop/CS461/tiny_vm/vm_core.c

CMakeFiles/tiny_vm.dir/vm_core.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/tiny_vm.dir/vm_core.c.i"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /Users/harker/Desktop/CS461/tiny_vm/vm_core.c > CMakeFiles/tiny_vm.dir/vm_core.c.i

CMakeFiles/tiny_vm.dir/vm_core.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/tiny_vm.dir/vm_core.c.s"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /Users/harker/Desktop/CS461/tiny_vm/vm_core.c -o CMakeFiles/tiny_vm.dir/vm_core.c.s

CMakeFiles/tiny_vm.dir/vm_loader.c.o: CMakeFiles/tiny_vm.dir/flags.make
CMakeFiles/tiny_vm.dir/vm_loader.c.o: /Users/harker/Desktop/CS461/tiny_vm/vm_loader.c
CMakeFiles/tiny_vm.dir/vm_loader.c.o: CMakeFiles/tiny_vm.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_9) "Building C object CMakeFiles/tiny_vm.dir/vm_loader.c.o"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/tiny_vm.dir/vm_loader.c.o -MF CMakeFiles/tiny_vm.dir/vm_loader.c.o.d -o CMakeFiles/tiny_vm.dir/vm_loader.c.o -c /Users/harker/Desktop/CS461/tiny_vm/vm_loader.c

CMakeFiles/tiny_vm.dir/vm_loader.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/tiny_vm.dir/vm_loader.c.i"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /Users/harker/Desktop/CS461/tiny_vm/vm_loader.c > CMakeFiles/tiny_vm.dir/vm_loader.c.i

CMakeFiles/tiny_vm.dir/vm_loader.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/tiny_vm.dir/vm_loader.c.s"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /Users/harker/Desktop/CS461/tiny_vm/vm_loader.c -o CMakeFiles/tiny_vm.dir/vm_loader.c.s

CMakeFiles/tiny_vm.dir/logger.c.o: CMakeFiles/tiny_vm.dir/flags.make
CMakeFiles/tiny_vm.dir/logger.c.o: /Users/harker/Desktop/CS461/tiny_vm/logger.c
CMakeFiles/tiny_vm.dir/logger.c.o: CMakeFiles/tiny_vm.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_10) "Building C object CMakeFiles/tiny_vm.dir/logger.c.o"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/tiny_vm.dir/logger.c.o -MF CMakeFiles/tiny_vm.dir/logger.c.o.d -o CMakeFiles/tiny_vm.dir/logger.c.o -c /Users/harker/Desktop/CS461/tiny_vm/logger.c

CMakeFiles/tiny_vm.dir/logger.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/tiny_vm.dir/logger.c.i"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /Users/harker/Desktop/CS461/tiny_vm/logger.c > CMakeFiles/tiny_vm.dir/logger.c.i

CMakeFiles/tiny_vm.dir/logger.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/tiny_vm.dir/logger.c.s"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /Users/harker/Desktop/CS461/tiny_vm/logger.c -o CMakeFiles/tiny_vm.dir/logger.c.s

# Object files for target tiny_vm
tiny_vm_OBJECTS = \
"CMakeFiles/tiny_vm.dir/cjson/cJSON.c.o" \
"CMakeFiles/tiny_vm.dir/main.c.o" \
"CMakeFiles/tiny_vm.dir/vm_state.c.o" \
"CMakeFiles/tiny_vm.dir/vm_ops.c.o" \
"CMakeFiles/tiny_vm.dir/vm_code_table.c.o" \
"CMakeFiles/tiny_vm.dir/builtins.c.o" \
"CMakeFiles/tiny_vm.dir/vm_core.c.o" \
"CMakeFiles/tiny_vm.dir/vm_loader.c.o" \
"CMakeFiles/tiny_vm.dir/logger.c.o"

# External object files for target tiny_vm
tiny_vm_EXTERNAL_OBJECTS =

/Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm: CMakeFiles/tiny_vm.dir/cjson/cJSON.c.o
/Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm: CMakeFiles/tiny_vm.dir/main.c.o
/Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm: CMakeFiles/tiny_vm.dir/vm_state.c.o
/Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm: CMakeFiles/tiny_vm.dir/vm_ops.c.o
/Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm: CMakeFiles/tiny_vm.dir/vm_code_table.c.o
/Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm: CMakeFiles/tiny_vm.dir/builtins.c.o
/Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm: CMakeFiles/tiny_vm.dir/vm_core.c.o
/Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm: CMakeFiles/tiny_vm.dir/vm_loader.c.o
/Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm: CMakeFiles/tiny_vm.dir/logger.c.o
/Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm: CMakeFiles/tiny_vm.dir/build.make
/Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm: CMakeFiles/tiny_vm.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --bold --progress-dir=/Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_11) "Linking C executable /Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/tiny_vm.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/tiny_vm.dir/build: /Users/harker/Desktop/CS461/tiny_vm/bin/tiny_vm
.PHONY : CMakeFiles/tiny_vm.dir/build

CMakeFiles/tiny_vm.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/tiny_vm.dir/cmake_clean.cmake
.PHONY : CMakeFiles/tiny_vm.dir/clean

CMakeFiles/tiny_vm.dir/depend: /Users/harker/Desktop/CS461/tiny_vm/vm_code_table.c
	cd /Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /Users/harker/Desktop/CS461/tiny_vm /Users/harker/Desktop/CS461/tiny_vm /Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug /Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug /Users/harker/Desktop/CS461/tiny_vm/cmake-build-debug/CMakeFiles/tiny_vm.dir/DependInfo.cmake "--color=$(COLOR)"
.PHONY : CMakeFiles/tiny_vm.dir/depend

