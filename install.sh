#!/bin/bash

#set -x

CHECK_FOR_DEBIANLIKE=1
export CHECK_FOR_DEBIANLIKE
VALID_PATH=
export VALID_PATH

function green_text {
	echo -e "\e[92m$1\e[0m"
}

function red_text {
	echo -e "\e[101m$1\e[0m"
}

function die {
	red_text "$1" >&2
	exit
}

function install_if_not_exists {
	PROGNAME=$1
	INSTALL=$2

	if [[ -z $INSTALL ]]; then
		INSTALL=$PROGNAME
	fi

	if ! which $PROGNAME >/dev/null; then
		red_text "$PROGNAME could not be found. Please enter your user password to run apt-get install $INSTALL"
		sudo apt-get -y install $INSTALL
	fi
}

function die_unless_debianlike {
	if [[ "$CHECK_FOR_DEBIANLIKE" -eq "1" ]]; then
		if ! cat /etc/issue | egrep -i "debian|ubuntu|mint" > /dev/null; then
			red_text "You seem to not be on Debian, Ubuntu or Mint, but this installer only works on these."
			red_text "If you want to run it anyways, run it with --no-os-check"
		fi
	fi
}

function get_path_from_list_that_is_in_PATH {
	DONE=0
	CHOSENPATH=
	for CHECKPATH in "$@"; do
		if [[ "$DONE" -eq "0" ]]; then
			if echo $PATH | egrep "(^|:)$CHECKPATH/*($|:)" > /dev/null; then
				DONE=1
				CHOSENPATH=$CHECKPATH
			fi
		fi
	done

	if [[ -z $CHOSENPATH ]]; then
		die "No valid PATH found. Try adding --force-path=/path/to/binaries/"
	else
		echo $CHOSENPATH
	fi
}

for i in "$@"; do
    case $i in
        --no-os-check)
		CHECK_FOR_DEBIANLIKE=0
        ;;

        --force-path=*)
		VALID_PATH="${i#*=}"
        ;;

	--help|-h)
		green_text "kdecsms installer"
echo '-h, --help		This help
--no-os-check		Do not check if is Debian, Ubuntu or Mint
'
	;;

        *)
                # unknown option
        ;;
    esac
done

die_unless_debianlike
install_if_not_exists "kdeconnect-cli" "kdeconnect"
install_if_not_exists "python3"
install_if_not_exists "qtchooser" "python3-pyqt5"

if [[ -z $VALID_PATH ]]; then
	VALID_PATH=$(get_path_from_list_that_is_in_PATH "/usr/local/bin" "/usr/bin")
fi

FINAL_PATH=$VALID_PATH/kdecsms 
green_text "The file kdecsms.py will be copied to $FINAL_PATH. You will be asked to provide your password."
sudo cp kdecsms.py $FINAL_PATH && green_text "The file kdecsms was copied successfully to $FINAL_PATH" || red_text "Copying the file kdecsms.py to $FINAL_PATH failed"
sudo chmod +x $FINAL_PATH && green_text "The execute-permission for $FINAL_PATH was set successfully" || red_text "Setting the execute-permission for $FINAL_PATH failed"
sudo cp kdecsms.gif /usr/local/src && green_text "Copying to logo to /usr/local/src/kdecsms.gif worked" || red_text "Copying the logo to /usr/local/src/kdecsms.gif failed"
sudo cp kdecsms.desktop /usr/share/applications && green_text "Copying to desktop file to /usr/share/applications/kdecsms.desktop worked" || red_text "Copying the desktop file to /usr/share/applications/kdecsms.desktop failed"
