<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and THEN omit $.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
State holds values that persist and can change while processes run.
Each trigger contains GIVEN, WHEN, and THEN; WHEN matches first, GIVEN guards it, and THEN selects a process.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
Each interface is one document-boundary crossing: in arrives, out is emitted, and inout does both.
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
<trigger id="command">
GIVEN: $state.mode equals "open"
WHEN: "A command line arrives."
THEN: process.route
</trigger>
</triggers>

<processes>
<process id="route" name="Route command">
IF $interface.stdin.COMMAND equals "pwd":
  THEN:
    CALL process.pwd
  ELSE:
    IF $interface.stdin.COMMAND equals "exit":
      THEN:
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
<interface id="stdin" direction="in" schema="schema.command-line">
The command line the user types.
</interface>

<interface id="stdout" direction="out" schema="schema.terminal-output">
The line the shell prints.
</interface>
</interfaces>
