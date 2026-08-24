<instructions>
Treat each command as an exact string.
</instructions>

<constants>
</constants>

<schemas>
</schemas>

<state>
MODE: "open"
COMMAND: "pwd"
OUTPUT: ""
</state>

<triggers>
- The shell mode is open. -> oak:process/route
</triggers>

<processes>
<process id="oak:process/route" name="Route the current command">
STEPS:
1. IF state oak:state/command equals "pwd":
   THEN:
      1. CALL process oak:process/pwd.
   ELSE:
      1. IF state oak:state/command equals "exit":
         THEN:
            1. CALL process oak:process/exit.
         ELSE:
            1. FAIL "Unknown shell command.".
</process>
<process id="oak:process/pwd" name="Run pwd">
STEPS:
1. SET state oak:state/output = "/oak".
2. SET state oak:state/command = "exit".
</process>
<process id="oak:process/exit" name="Run exit">
STEPS:
1. SET state oak:state/output = "logout".
2. SET state oak:state/mode = "closed".
</process>
</processes>

<interfaces>
</interfaces>
