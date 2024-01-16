# FRC Game Tools

FIRST Robotics Competition has a set of tools: 
1. driver station software
2. tools to configure the hardware, and 
3. software libraries to use with your chosen programming language.  

The first two items come in the "game tools" installation, and the third comes in a language-specific installation.  Not every computer **needs** to have the game tools, but practically speaking it will be more convenient if most or all computers have the driver station software, so that we aren't searching/borrowing the driver station just to run a test.  

To install the FRC game tools, follow the directions at https://docs.wpilib.org/en/stable/docs/zero-to-robot/step-2/frc-game-tools.html.

You will see links on that page to the Python Installation Guide.  Read it for information, but **don't execute** the steps.  Rather, use the modified steps that we have documented below.


# Developer Configuration

Sharkbots uses Python for programming. Because Python has a very large community and because it's very easy to add new libraries to a python environment, it's very easy for developers to end up with a lot of complex dependencies that end up causing trouble on the actual RoboRio or outboard processor. To (help) fight that, please use the **conda** package manager to create a "virtual environment." Everyone will share the same libraries and be able to to recreate the virtual environment quickly.

**NOTE**: If you want to develop in a Linux environment under Windows (using the Windows Subsystem for Linux aka WSL), you may. However, you **must** use Ubuntu 22 to do so. Ubuntu 18 requires a lot of upgrades to work with wpilib. If you're using a Windows machine and don't want to use Linux, use the **Command prompt** or **Windows Powershell** terminals to work. 

## Clone this repo 

Using your git client, create a local copy of this Github repository on your development machine. If you have a graphical user interface, use it. If you have a command-line version of **git** installed, go to the directory in which you want to do your programming, and run:

    git clone https://github.com/WHEARobotics/FRC2024

This will create a subdirectory called **FRC2024** containing the latest contents of this repository.

## Installing miniconda

Follow the instructions at the [miniconda installation page](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) to install the **conda** program on your system.

1. Open a terminal. 
1. Change directories (`cd`) to the **FRC2024/** directory created by the git cloning process from the previous step
1. Confirm that this directory has a file called **requirements.txt** in it. 

The **requirements.txt** file defines the Python libraries used in the common development environment.


## Create the **frc** conda environment 

Run:

    conda create -n frc python=3.10

You are asking the **conda** program to create an environment. The name of the environment is "frc" (`-n frc`). The version of Python we will use is Python 3.10 (`python=3.10`).

### IMPORTANT! Activate the **frc** environment before work!

When you open a terminal, the **conda** program puts you in the **base** environment, which does not contain any shared libraries and may not even have a Python interpreter installed. You **MUST** activate the **frc** environment, every session, by running:

    conda activate frc 

To confirm that you've switched to the proper environment, run:

    conda info --envs

This will tell you about all the environments you have installed. The output will look something like:

```bash
# conda environments:
#
base                     /home/lobrien/mambaforge
frc                   *  /home/lobrien/mambaforge/envs/frc
```

The currently activated environment will be marked with an asterisk. In this case, you can see that the **frc** environment is activated. 

## Install libraries using **pip**

Install the libraries used by our team with:

    pip install -r requirements.txt

This program will take a minute or two to run. It will download and install the appropriate Python runtime and tools and all the listed packages. We will undoubtedly decide to include some other packages. When we do so, we'll update **requirements.txt** and save it so we don't struggle with "works on my machine!" errors. (There are _always_ WOMM errors! It's just part of the process.)

**Note**: This involves a lot of very complex behind-the-scenes stuff. Often, "recreating the dev environment" is one of the biggest challenges to getting started in a programming project. Don't be surprised if you need help from a mentor at this stage. Just ask!

**Note**: On Windows Subsystem for Linux (WSL), installing **wpilib-util** fails trying to find **std::span**. Larry reckons this indicates that WSL is using an older **gcc**. See https://github.com/WHEARobotics/FRC2023/issues/2

## Verify the most critical tools

Once you have activated the **frc** environment, you should be able to program our robot! First, though, let's verify the installation went well. In a terminal, switch to the **src/helloworld/** subdirectory (`cd ./src/helloworld/`), activate the **frc** conda environment, and:

### Verify you are running Python 3.10

Run `python --version`. Expected result: `Python 3.10.0`

### Verify that you can run a simple wpilib robot

Switch to the **robot/** subdirectory of **src/helloworld/** and run:

    robotpy --main hello_robot.py sim

You're asking the robotpy program to run the program **hello_robot.py** in simulator mode. 

You should see a command-line output similar to:

```bash
(frc) c:\gh\wh\FRC2024\src\helloworld\robot>robotpy --main hello_robot.py sim
23:02:51:625 INFO    : halsim_gui          : WPILib HAL Simulation 2024.1.1.0
HAL Extensions: Attempting to load: halsim_gui
Simulator GUI Initializing.
Simulator GUI Initialized!
HAL Extensions: Successfully loaded extension
23:02:52:532 INFO    : pyfrc.physics       : Physics support successfully enabled
23:02:52:533 INFO    : wpilib              : RobotPy version 2024.1.1
23:02:52:533 INFO    : wpilib              : WPILib version 2024.1.1.0
23:02:52:533 INFO    : wpilib              : Running with simulated HAL.
23:02:52:547 INFO    : nt                  : Listening on NT3 port 1735, NT4 port 5810
Not loading CameraServerShared
23:02:52:565 INFO    : pyfrc.physics       : Motor config: 2 CIM motors @ 10.71 gearing with 6.0 diameter wheels
23:02:52:566 INFO    : pyfrc.physics       : - Theoretical: vmax=12.980 ft/s, amax=44.731 ft/s^2, kv=0.925, ka=0.268
23:02:52:567 INFO    : pyfrc.physics       : Robot base: 29.5x38.5 frame, 22.0 wheelbase, 110.0 mass

********** Robot program startup complete **********
Default frc::IterativeRobotBase::DisabledPeriodic() method... Override me!
Default frc::IterativeRobotBase::RobotPeriodic() method... Override me!

```

And a "Robot Simulation" Window to appear. Close the simulation window to end the program.

### Verify that you have OpenCV ("Computer Vision") installed

Switch to the **src/helloworld/apriltags** directory and run:

    python hello_apriltag.py 

Expected output: `Yeah, that worked.`

### Verify that you can capture an attached Webcam 

**Note**: You must have a Webcam attached or this will fail! lol

Switch to the **src/helloworld/opencv** directory and run:

    python hello_opencv.py

**Note**: You may be asked for permission to access your Webcam and the program may fail until you grant this. 

Expected output: A window should open with the view from your Webcam. It should contain a crude "targeting overlay" made of some crossed lines and a circle. To exit the program, press 'q' on your keyboard. 

## You should be set

If you've:

1. Installed **conda**
1. Created an **frc** environment based on **requirements.txt** 
1. Activated the **frc** environment
1. Verified:
   1. **wpilib**
   1. OpenCV 
   1. Webcam capture

You should have all the tools ready to begin programming! 

# Updating the RobotPy installation on our PCs

## Update the first computer

A designated person will:

* Create a git branch for updates.

* Update robotpy by running (in the Anaconda prompt with the frc environment activated):

    pip install --upgrade robotpy

* Find the new robotpy version number by executing 
 
    pip list

and looking for a line like `robotpy 2024.1.1`

* Edit the **pyproject.toml** file in the **hello2024** project.  This file tells robotpy which version of robotpy should be on the robot, along with other libraries.  Change the line that looks like `robotpy_version = "2024.1.1"` to use the same version that you see in pip list output.

* Now we need to get the latest versions of the robotpy files that go onto the robot loaded onto the PC.  With your Anaconda prompt in the folder of the code project you edited, run

    robotpy sync


* Test deploying the code to a robot.  
* Ideally, copy the **pyproject.toml** file to another project with more complex code than **hello2024**, and test to verify that deployed code works, too.
* Then update the requirements file for the whole repository. With your Anaconda prompt at the root level of the repository (where the **requirements.txt** file is), execute: 

    pip freeze > requirements.txt

this puts the output of the `pip freeze` command into the **requirements.txt** file, replacing the old contents.

* Ideally, update the **pyproject.toml** files in all other projects within the repository so that they are all using the same version.

* Document your changes in the **RELEASE_NOTES.md** file in the repository.

* Make a commit, push the updated files to GitHub, and merge your branch into the **main** branch.  

## Updating the rest of the computers

Once the changes have been pushed to GitHub, The rest of computers (and the developers using them) can pull from it and then run these two commands (in an Anaconda prompt with the `frc` environment activated):

* Updating the python environment:

    pip install -r requirements.txt

* In the folder with one of projects to download stuff needed for the robot:

    robotpy sync

