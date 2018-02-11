-- Script for MAME that launches the vg5k emulator, waits for boot, injects
-- a binary program and launches it.
--
-- Copyright 2018 Sylvain Glaize
-- 
-- Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
-- documentation files (the "Software"), to deal in the Software without restriction, including without
-- limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
-- Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
--
-- The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
-- 
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
-- TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
-- THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
-- CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
-- DEALINGS IN THE SOFTWARE.

local machine = manager:machine()
local machine_debugger = machine:debugger()
local log = machine_debugger.consolelog
local log_count = 1

-- First verity if the debugger was launched with the emulator
if not machine_debugger then
	print("No debugger found.")
	return
end

-- Pause the emulator while setuping the system
emu.pause()

-- Get control objects from the emulator
local cpu = manager:machine().devices[":maincpu"]
local debugger = cpu:debug()

-- The steps
local boot = {
	name = "BOOT",
	action = function()
		debugger:go(0x2adf)
		emu.unpause()
	end
}

local load_after_boot = {
	name = "LOAD",
	condition = "Stopped at temporary breakpoint 2ADF on CPU ':maincpu'",
	action = function()
		machine_debugger:command("load input.bin,0x7000")
		emu.keypost('CALL &"7000"\n')
	end
}

local final_step = {
	name = "STOP",
	action = function()
	end
}

local steps = {
	boot,
	load_after_boot,
	final_step,
}

-- The Step Machine
local current_step = 0
local next_step

function do_action()
	next_step.action()
end

function go_to_next_step()
	current_step = current_step + 1

	if current_step <= #steps then
		next_step = steps[current_step]
		print("Running step: " .. next_step.name)
	else
		next_step = nil
		print("No more step")
	end

end

-- Bootstraping
go_to_next_step()

-- Running the Step Machine
emu.register_periodic(function()
	local condition_found = false

	if log_count <= #log then
		for i = log_count, #log do
			msg = log[i]

			print("DEBUG: " .. msg)
			if next_step and msg == next_step.condition then
				condition_found = true
			end
		end

		log_count = #log + 1
	end

	if condition_found or (next_step and not next_step.condition) then
		do_action()
		go_to_next_step()
	end

end)
