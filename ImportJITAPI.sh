#! /bin/bash

# A simple script to import JITAPI GitHub project onto your working station


# Just some checks and notes before the script runs

echo "NOTE: The script is going to import project here!"

read -p "Does current working directory suit you? (y/n) " ANSWER

if [[ $ANSWER != "y" ]] && [[ $ANSWER != "Y" ]]
then
    exit 1
fi


# And off we go!

echo -e "\e[5mPreparing your virtual environment...\e[0m"

python3 -m venv JITENV # Prepare the environment
source JITENV/bin/activate

EXPECTED_ENV=$(pwd)
EXPECTED_ENV+="/JITENV"

if [[ $VIRTUAL_ENV == $EXPECTED_ENV ]]
then
    echo -ne "\e[1A\e[K\r\e[1;92mEnvironment prepared successfully!\e[0m\n"
else
    echo -ne "\e[1;31mThere was an error while entering the virtual environment.\e[0m\n"
    deactivate
    rm -Rf JITENV
    exit 1
fi

cd JITENV
git clone https://github.com/MojiRiAnt/JITAPI.git # Prepare the project
cd JITAPI

mkdir var

#pip3 install -r requirements.txt # Install requirements

echo ""
echo -e "\e[1;92mScript finished successfully!\e[0m"
#echo -e "\e[1mNOTE: Use $ invoke --list to see available commands.\e[0m"
echo -e "\e[1mNOTE: To remove the project, simply remove the JITENV directory.\e[0m"
