<instructions>
$ reads a value; a dotted path starts with its part; a bare $NAME is local to the running process; SET, CALL, and EMIT omit $.
Each schema is one information shape: a template with <PLACEHOLDER> slots, and WHERE lines that constrain each slot.
State holds values that persist and can change while processes run.
Each trigger names one arrival reason, an optional state guard, and the process that runs when both match.
Each process is the exact way to do one task; follow its steps in order, top to bottom.
Each interface is one information crossing: in arrives, out is emitted, and inout does both.
Treat each command as an exact string.
</instructions>

<constants>
</constants>

<schemas>
<schema id="command-line" name="Command Line" purpose="Carry one command the user types.">
<COMMAND>

WHERE:
- <COMMAND> is string; is non-empty (e.g. `pwd`, `exit`); the exact command string.
</schema>

<schema id="terminal-output" name="Terminal Output" purpose="Carry one line the shell prints.">
<OUTPUT>

WHERE:
- <OUTPUT> is string; is non-empty (e.g. `/oak`, `logout`); the printed line.
</schema>
</schemas>

<state>
mode: "open"
</state>

<triggers>
<trigger id="command" given='$state.mode equals "open"' when="A command line arrives." process="route" />
</triggers>

<processes>
<process id="route" name="Route command">
IF $interface.stdin.COMMAND equals "pwd":
  CALL process.pwd
ELSE:
  IF $interface.stdin.COMMAND equals "exit":
    CALL process.exit
  ELSE:
    FAIL "Unknown shell command."
</process>

<process id="pwd" name="Run pwd">
EMIT interface.stdout:
  OUTPUT = "/oak"
</process>

<process id="exit" name="Run exit">
EMIT interface.stdout:
  OUTPUT = "logout"
SET state.mode = "closed"
</process>
</processes>

<interfaces>
<interface id="stdin" direction="in" schema="command-line">
The command line the user types.
</interface>

<interface id="stdout" direction="out" schema="terminal-output">
The line the shell prints.
</interface>
</interfaces>
