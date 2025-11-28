def chatLoop(page, use=1, sudo_password=None, max_com=20):
    def normalChat(page):
        import os
        from initMods.GetLastResponse import GetLastResponse
        from Mods.Message import SendMessage
        from colorama import init
        from termcolor import colored
        from art import art

        # def lineDrawer(char="-"):
        #     terminal_size = os.get_terminal_size()
        #     print(char * terminal_size.columns)

        print(art)
        while True:
            # indicate for the user that its going and needed to put a prompt and press enter
            print(colored("Prompt", "yellow", "on_black"))
            # get the prompt
            prompt = input()
            # user SendMessage function from the Mods folder
            SendMessage(page, prompt)

            # add a little space before getting deepseek's output
            print()
            # lineDrawer()
            print()

            # Get the response (function now waits for completion)
            # meaning that in the webpage, a animation happens, this function find out if its started, and also find out if its finished

            # capture the response in response varable
            response = GetLastResponse(page)
            # indicate that its deepseek speaking
            print(colored("DeepSeek", "blue", "on_black"))
            # print the response in bold:
            # if we put \33{1m before and After a string, it gets bold
            print(f"\033[1m{response}\033[0m")

            # i just thinked that if i add a random print, it would make me look like a pro coder XD
            print()

    def linuxChat(page, sudo_password=None):
        import os
        import subprocess
        import platform
        import re
        from initMods.GetLastResponse import GetLastResponse
        from Mods.Message import SendMessage
        from colorama import init
        from termcolor import colored
        from art import art

        # Initialize colorama
        init()

        print(art)
        print(colored("Linux Terminal Mode Activated", "green", "on_black"))

        # Detect OS and setup terminal environment
        # we detect the os using this, platform, inside system, find the lower(nae of the os)
        current_os = platform.system().lower()
        # do we have native linux temrina? None is just for declaring a empty varable
        terminal_cmd = None

        # if our os (platform.system().lower()) is linux,
        if current_os == "linux":
            # Running on actual Linux using bash(can be changed to zsh or oh my zsh but ai dosent care about these
            terminal_cmd = ["bash", "-c"]
            # tell the user that we detected its linux (lin kos XD)
            print(colored("Detected Linux OS - Using native terminal", "green"))
            # if the os in NOT linux, and is the nasty baddie windows
        elif current_os == "windows":
            # Check if WSL is available, kiddos linux (i use it myself, sadly)
            try:
                # Try to run wsl command to check if it's installed or not
                result = subprocess.run(
                    ["wsl", "--list", "--quiet"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                # code 0 means YES, the output is NOT an error, meaning wsl is there,
                if result.returncode == 0:
                    # so meaning that we have a bash, INSIDE out wsl
                    terminal_cmd = ["wsl", "bash", "-c"]
                    # and we will tell the user that we know your a idiot(windows user) and we'll use wsl for your little brain
                    print(colored("Detected Windows OS - Using WSL", "green"))
                else:
                    # if not wsl, pisho pisho the user out of the code, my golden beautiful code dosent whant a kid, using windows, touch it
                    print(
                        colored(
                            "WSL not found! Please install WSL to use Linux terminal mode.",
                            "red",
                        )
                    )
                    return
            # if it took a lot of time (subprocess.TimeExpired is always 30 sec's)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # pisho pisho the user out again, telling it that they dont have linux or wsl
                print(
                    colored(
                        "WSL not found! Please install WSL to use Linux terminal mode.",
                        "red",
                    )
                )
                return

        else:
            # else, show the user that were CONFUSED AS HELL, not using windows? also not user linux? dude im too lazy to go to shower, and your telling me to learn a new OS? which almost dosent exict?
            print(
                colored(
                    f"Unsupported OS: {current_os}. Linux terminal mode not available.",
                    "red",
                )
            )
            return

        # if after all those checkings, the dude passed, we ensure terminal is connected and his a LEGEND
        print(
            colored("Terminal ready! AI will systematically complete tasks.", "yellow")
        )
        print(colored("AI will check prerequisites and execute step-by-step.", "cyan"))
        print(
            colored(
                "AI will use cowsay for friendly communication and results!", "magenta"
            )
        )
        print()

        # Elevate to root using sudo su
        if sudo_password:
            # im too lazy to implement a way of getting the password when the user needs to enter the password, so i do this
            print(colored("Elevating to root privileges...", "yellow"))
            try:
                # if your os is linux
                if current_os == "linux":
                    # then run the process of turning into super user
                    process = subprocess.Popen(
                        # process command is sudo su
                        "sudo su",
                        # its in shell mode, meaning its running IN A SHELL
                        shell=True,
                        # pipe meaning AS A PIPE
                        # we connect OUR input to the python file to fill the password for the su command
                        # and also, when we sudo su, we are INSIDE the su environment, meaning that were going to sent and get messages to the su env, this is a way to sent the input
                        stdin=subprocess.PIPE,
                        # we connect ITS output to the python file to see if the command worked or not
                        # and also, when we sudo su, we are INSIDE the su environment, meaning that were going to sent and get messages to the su env, this is a way to capture the output
                        stdout=subprocess.PIPE,
                        # we connect out python file to the error handler of su
                        # in the su env we might get errors, we need to detect them so the ai see's them and fixes them (if it was able to, which mostly likely will not be able to
                        stderr=subprocess.PIPE,
                        # turns you input into bytes for the system to work || automatically turns the output of the system to text so YOU, as a lazy coder can read it
                        text=True,
                    )

                    stdout, stderr = process.communicate(
                        input=sudo_password
                        + "\n",  # we use the stdin, which is the input to sent our password to the code, and \n is basically pressing enter
                        timeout=10,  # we make sure to stop the process if it took more that 10 seconds,
                    )

                    if (
                        process.returncode == 0
                    ):  # return code 0 means good, and return codes OTHER THAN 0 (mostly 1) are bad
                        print(
                            colored(
                                "✓ Successfully elevated to root privileges", "green"
                            )
                        )  # if its 0, then its good
                    else:  # if its a return code other than 0, which is 1 i think, MOSTLY, not always
                        print(
                            colored("✗ Failed to elevate to root privileges", "red")
                        )  # tell it that something went wrong
                        print(
                            colored(f"Error: {stderr}", "red")
                        )  # use the pipe that we made with the stderr name, to SHOW the actually error,
                        # reminder:
                        # when timeout happens, python ITSELF finds out if timeout happened in 9 lines before this one,
                        # BUT it the actually linux failed to get su, then we need to use the bridge(pipe) we made to the su env to find this out, this is a basic error handler
                        # that handles nothing, but ot cry in front of you about the linux bro hitting him too hard in the belly
                        return

                # linux part finished

                else:  # Windows with WSL,

                    # its almost just as same as the one we use in linux to get su, but this time we add a wsl before it, let me explain

                    # in a terminal:
                    # when we do this:
                    # app1 app2
                    # we are actually telling app1, to do something with app2 and app3
                    # so when we do wsl bash -c sudo su

                    # we are telling wsl to run bash:
                    # and telling bash to run with -c tag which means that we whant the characters after -c to be passed into bash as commands, AND:
                    # to run sudo su in bash
                    # overhally something like this wsl --> bash --> -c (as for command) --> sudo su <-- there are commands because we said -c

                    process = subprocess.Popen(
                        ["wsl", "bash", "-c", "sudo su"],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    # same, just lazy to ctrl+c, ctrl+v
                    stdout, stderr = process.communicate(
                        input=sudo_password + "\n", timeout=10
                    )
                    if process.returncode == 0:
                        print(
                            colored(
                                "✓ Successfully elevated to root privileges", "green"
                            )
                        )
                    else:
                        print(colored("✗ Failed to elevate to root privileges", "red"))
                        print(colored(f"Error: {stderr}", "red"))
                        return
                # we call this error catching, we catch the error as e (put the error in a varable called e)
            except Exception as e:
                # print the e, but the problem is, that e is not a string, we have to type convert, so it changes to a string, using str(var), :
                # overhally in python type conversion is like this type(var) e.g int(2.1) == 2

                print(colored(f"Error elevating privileges: {str(e)}", "red"))
                return
        else:  # when making the main function of linux automator(i just type names, not remember them) we declared a varable:
            # declaring a varable means MAKING A CONTAINER, but not putting anything in it,
            # python dosent have a official method, but we have None, which is.... well.... none, nothing,
            # so. a = None means that a is THERE, but its empty
            # so we can leave the sudo su part and skip it if user dident specified its room password,
            print(
                colored(
                    "⚠ No sudo password provided - running without root privileges",
                    "yellow",
                )
            )

        # we cant make a automated linux ai thingy without running commands,
        def execute_command(
            command,
        ):  # make a function named execute_command that takes a argument named command
            # OR -->
            """Execute a command and return the result with captured output"""
            try:
                # tell the user what command are we runnig with a cyan color, which is AS UGLY AS A BANANA
                print(colored(f"Executing: {command}", "cyan"))
                # at first, the code showed the os EVERYTIME it whanted to print something, which, we dont need at all,
                # print(colored(f"Current OS: {current_os}", "blue"))
                # me, as the user, KNOW what oprating system i am using

                # for making it look pretty we make a seperator,
                print(colored("=" * 60, "blue"))

                # Execute the command (no sudo password handling needed since we're already root(IF.... were already root))
                # everything already explained in the previus examples,
                if current_os == "linux":
                    print(colored("Linux ", "blue"))
                    result = subprocess.run(
                        command.strip(),
                        shell=True,
                        text=True,
                        capture_output=True,
                        timeout=120,
                    )
                else:  # Windows with WSL
                    print(colored("WSL", "blue"))
                    result = subprocess.run(
                        ["wsl", "bash", "-c", command.strip()],
                        text=True,
                        capture_output=True,
                        timeout=120,
                    )

                # Display the actual output to user
                if (
                    result.stdout
                ):  # if resault is good, and its not a error, print it with green color (not the resault, just the title like text above it)
                    print(colored("STDOUT:", "green"))
                    # print the output of our command (that we piped it, i just whant to remind you that i KNOW WHAT A PIPE IS, mr,rahimi)
                    print(result.stdout)
                if (
                    result.stderr
                ):  # if resaykt us bad, show the title red, and print the resaults
                    print(colored("STDERR:", "red"))
                    # print the resaults
                    print(result.stderr)

                print(colored("=" * 60, "blue"))  # add the second seperator
                print(
                    colored(
                        f"Command completed with exit code: {result.returncode}", "blue"
                    )
                )

                # Return result with captured output for AI
                return result

            except subprocess.TimeoutExpired:

                print(colored("Command timed out after 30 seconds", "red"))
                return None  # return nothing, because it timed out and after 30 seconds(timeout) we had NOTHING TO DO THINGS ONTO IT
            except (
                Exception
            ) as e:  # again, get the error, string it, and show it to the dude looking at the terminal like its a formula of solving the meaning of life
                print(colored(f"Error executing command: {str(e)}", "red"))
                return None

        def send_systematic_prompt(
            task,
        ):  # send a long prompt, to make sure the ai does linux, and the ai's linux linux's
            """Send a systematic prompt for thorough task completion"""
            systematic_prompt = f"""
            SYSTEMATIC TASK EXECUTION MODE:
            Task: {task}

            You must systematically complete this task by:
            1. Analyzing ALL prerequisites needed
            2. Checking each prerequisite step by step
            3. Installing/configuring missing dependencies
            4. Executing the main task
            5. Verifying completion
            but remember, these can change, based on user task, and the way user speaks, you can skip parts, in the process if you found out that the skpped part is important?
            you can always do it again

            For each step, you must:
            - Check if prerequisite exists (use appropriate commands)
            - If missing, install/configure it
            - Verify installation success
            - Move to next step
            - Continue until main task is complete

            CRITICAL RULES:
            - ONLY output Linux commands, NO explanations or text
            - ONE command per response
            - Use commands: ALL commands that are:
                                    - single line commands, meaning they dont OPEN a terminal-gui environment
                                    - needed, to do your stuuf, and acomplish your goal
            - Use appropriate package managers: 
                                    - officials: any official that matches the os, apt pacman etc...
                                    - officials: any official that matches the app or action needed, pip, npm, python -m etc...
            - Always verify success before proceeding
            - When task is COMPLETELY DONE, output exactly: "--PK--PK--PK--" because if the text is smaller that 3 characters, the temrinal wont run it

            ROOT PRIVILEGES:
            - You are running with root privileges (elevated via sudo su)
            - All commands will execute with full system access
            - No need to prefix commands with "sudo" - you already have root access
            - Examples: apt install, snap install, systemctl, etc.

            IMPORTANT: Commands will execute in real-time terminal. You can see the output directly.
            Use the terminal output to make informed decisions about the next step. also messages that are smaller than 5 characters wont get runned in the terminal, IF your command is small, like pwd, ls, or ANY OTHER COMMAND THAT IS SMALLER THAN 5 CHARACTERS, if a command is smaller than 5 characters, add a comment in front of it, a comment is a string, that we put in our commands to help the hummand/non machines find out that what this code does, meaning they wont actually DO anything, so, if a command is smaller than 5 characters, we can put a command in front of them, like this ```pwd #this is a comment to make the command bigger than 5 characters``` but if the command is ok, and more than 5 characters, like this ```sudo apt install cowsay``` theres no need to any comments, because our bridge to the terminal automatically finds it out and puts it in the terminal

            COWSAY INTERACTION RULES:
            - Use cowsay to connect with the user and make interactions more friendly
            - When user asks for BOTH action AND results (like "show me what's in this folder" or "tell me about this file"), use cowsay to present the results
            - Use cowsay for status updates, confirmations, and friendly communication
            - Examples of when to use cowsay:
              * After completing a step: cowsay "Step completed successfully!"
              * When showing results: cowsay "Here's what I found in the folder"
              * For confirmations: cowsay "Ready to proceed with next step"
              * When user asks questions: cowsay "Let me check that for you"
            - Don't overuse cowsay - use it strategically for meaningful interactions
            - Available cowsay options: -f (different animals), -e (eyes), -T (tongue)

            EXAMPLE for "create games folder and cd into it":
            1. mkdir -p ~/games
            2. cd ~/games
            3. pwd # a command to ensure that commands that are less that 3 cahracters OR equal to 3 characters run
            4. cowsay "Games folder created and ready!"
            5. --PK--PK--PK--

            EXAMPLE for "show me what's in my home directory":
            1. ls -la ~
            2. cowsay "Here's what's in your home directory!"
            3. --PK--PK--PK--

            BUT REMEMBER:
                this linux terminal is in your hands, DO NOT LIMIT YOURSELF TO THE THINGS I TOLD YOU IN THIS PROMP, be creative, to accomplish the task

            AND:
                if the user is not asking you to DO anything, you can directly speak to user using cowsay, which will be always installed

            Start with the FIRST command for: {task}
            """
            SendMessage(
                page, systematic_prompt
            )  # send the long systematical prompt to the deepseek

        # Test command execution -- if you dont understand this code snipped, then i whant to ask you, WHY ARE YOU READING 332 LINES OF MY CODE? oh sorry, HOW?
        print(colored("Testing command execution...", "yellow"))
        test_result = execute_command("echo 'Terminal test successful'")
        if test_result and test_result.returncode == 0:
            print(colored("✓ Terminal execution working!", "green"))
        else:
            print(colored("✗ Terminal execution failed!", "red"))

        # Test cowsay functionality -- ?
        print(colored("Testing cowsay functionality...", "yellow"))
        cowsay_result = execute_command("cowsay 'Hello! I'm ready to help you!'")
        if cowsay_result and cowsay_result.returncode == 0:
            print(
                colored(
                    "✓ Cowsay working! AI will use it for friendly communication!",
                    "green",
                )
            )
        else:
            print(
                colored(
                    "⚠ Cowsay not available, but AI will still work normally", "yellow"
                )
            )
        print()

        # Main task loop -- here's the main game XD
        while (
            True
        ):  # this happens until we stop it from happening (ctrl+c or ctrl+d for python(it might work or might not work))
            # we indicate to the user that we whant a task from it
            print(colored("Enter your task:", "yellow", "on_black"))
            # we get the task, simply in task varable
            task = input()

            #
            if (
                not task.strip()
            ):  # .strip() is a function from strings that cleans the string, i have NO ways to expalin it, but to show you:
                # "     hello" --> "hello"
                # "\nhello" --> "hello"
                # \thello\n    " --> "hello,
                # this is needed because we need our prompt for the ai to be clean, this ai is not MEANT to do these linux automations, so its sensetive
                continue  # if the task is not stripped, strip it, if its stripped, go on to the next lines

            #
            print(colored(f"Starting executing", "green"))
            print()

            # Send initial systematic prompt WITH the task with it
            send_systematic_prompt(task)

            # Execute commands until task is complete
            task_complete = False  # this makes the loop break if its true, so:
            # when its false:
            # task continues to run:
            # and linux commands get into shell over and over again UNTIL were done
            # when its true:
            # task is done, and stops working:
            # and linux commands stop continuing to run over and over again,

            command_count = (
                0  # we use this to keep count of how meany commands we putted there,
            )
            max_commands = max_com  # Safety limit to prevent infinite loops, and stop the ai from doing something that takes 10 hours,
            # buts its also a optional argument of the function, so we can change it, BY DEFAULT its 20 commands,

            while (
                not task_complete and command_count < max_commands
            ):  # continue this loop until, task is complete OR commands are finished (more that 20 commands)
                print()

                print(colored("Waiting for AI response...", "yellow"))

                # Get the response using this funcion,
                response = GetLastResponse(page)
                print(colored("DeepSeek", "blue", "on_black"))
                print(f"\033[1m{response}\033[0m")

                # Check for completion signal:
                # i told the ai to say --PK--PK--PK-- when its task is completed, in here we are LITTERALLY SEEING ENGLISH
                # if THIS is in THAT, do THIS
                if "--PK--PK--PK--" in response.strip():
                    print(
                        colored("✓ TASK COMPLETED SUCCESSFULLY!", "green", "on_black")
                    )
                    task_complete = True  # as i said, it will break the loop
                    break  # but i like to make 2 times more sure that loop will break

                # Execute the command if it's not the completion signal
                if response.strip() and "--PK--PK--PK--" not in response.strip():
                    print(colored(f"About to execute: '{response.strip()}'", "magenta"))
                    result = execute_command(response.strip())
                    command_count = (
                        command_count + 1
                    )  # same as command_count += 1, but i like to make the code so simple, that the user dosen even have to know the oprators:
                    # and when i say simple, im talking about only the 1% that i KNOW how to simplize, other than that? reader have to be a code knower

                    # Send follow-up prompt for next step
                    if not task_complete:
                        # Prepare command output for AI
                        output_info = ""
                        if (
                            result
                            and hasattr(result, "stdout")
                            and hasattr(result, "stderr")
                        ):
                            output_info = f"""
Command executed: {response.strip()}
Exit code: {result.returncode}
"""
                            if result.stdout:
                                output_info += f"STDOUT:\n{result.stdout}\n"
                            if result.stderr:
                                output_info += f"STDERR:\n{result.stderr}\n"
                        else:
                            output_info = f"Command executed: {response.strip()}\n(No output captured)"

                        follow_up = f"""
                {output_info}

                Continue with the next step for: {task}
                Remember: When completely done, output exactly: "--PK--PK--PK--"

                COWSAY REMINDER:
                - Use cowsay for friendly communication and status updates
                - When showing results or confirming completion, use cowsay
                - Examples: cowsay "Step completed!" or cowsay "Here are the results!"
                - Use cowsay strategically to connect with the user
                """
                        SendMessage(page, follow_up)

            if command_count >= max_commands:
                print(
                    colored(
                        "⚠ Maximum command limit reached. Task may be incomplete.",
                        "yellow",
                    )
                )

            print()
            print(colored("=" * 50, "blue"))
            print()

    # # Route to appropriate chat function
    # if lin:
    #     linuxChat(page, sudo_password)
    # # if AcsiiArter:
    # #   arterChat(page)
    # else:
    #     normalChat(page)


    match use:
        case 1:
            chatLoop()
        case 2:
            linuxChat(page)
            