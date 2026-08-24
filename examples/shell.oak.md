<instructions>
Treat each command as an exact string.
</instructions>

<constants>
</constants>

<schemas>
<schema id="oak:schema/command-line" name="Command Line" purpose="Carry one command the user types.">
<COMMAND>

WHERE:
- <COMMAND> is string; is non-empty (e.g. `pwd`, `exit`); the exact command string.
</schema>

<schema id="oak:schema/terminal-output" name="Terminal Output" purpose="Carry one line the shell prints.">
<OUTPUT>

WHERE:
- <OUTPUT> is string; is non-empty (e.g. `/oak`, `logout`); the printed line.
</schema>
</schemas>

<state>
MODE: "open"
</state>

<triggers>
<trigger id="oak:trigger/command" when="A command line arrives while the shell mode is open." process="oak:process/route" />
</triggers>

<processes>
<process id="oak:process/route" name="Route the current command">
IF interface oak:interface/stdin <COMMAND> equals "pwd":
  CALL process oak:process/pwd
ELSE:
  IF interface oak:interface/stdin <COMMAND> equals "exit":
    CALL process oak:process/exit
  ELSE:
    FAIL "Unknown shell command."
</process>

<process id="oak:process/pwd" name="Run pwd">
EMIT interface oak:interface/stdout:
  <OUTPUT> = "/oak"
</process>

<process id="oak:process/exit" name="Run exit">
EMIT interface oak:interface/stdout:
  <OUTPUT> = "logout"
SET state oak:state/mode = "closed"
</process>
</processes>

<interfaces>
<interface id="oak:interface/stdin" direction="in" schema="oak:schema/command-line">
The command line the user types.
</interface>

<interface id="oak:interface/stdout" direction="out" schema="oak:schema/terminal-output">
The line the shell prints.
</interface>
</interfaces>
