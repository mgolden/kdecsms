# kdecsms

KDE Complete SMS

KDE Command-line SMS


## Description

This is a standalone interface program to send SMS messages from a KDE desktop.
It fills a need in the KDE space at the moment, because there is no good way to initiate and continue an SMS conversation using kdeconnect.

I am a huge fan of kdeconnect.
It is a great tool, and the integration between my desktop and my phone is something I use constantly.
And while the plasma widget does a great job informing of inbound SMS messages, and making a single response to them, it doesn't allow multiple responses, since the widget closes after the message is sent.
It also doesn't have a way of initiating an SMS thread to someone who hasn't texted you first.

There are a few ways to do this that I am aware of.

* The base way to do it is to use the kdeconnect-cli --send-sms flag at the command line.
One has to first find out the device ID, before typing the message in quotes on the command line.
Sending the second message requires either retyping or editing the previous command line.

* There's a plasma widget called KDEConnect SMS, https://github.com/comexpertise/plasma-kdeconnect-sms
It works fine for me, but it has a few issues:
    * Since it's a plasmoid, you don't have a link to it on the taskbar to fish it up.
    * You have to type the number in the box directly, it doesn't accept a paste action.
    * You only have one of it open, so going from one number to another means retyping.
    * It doesn't properly tell you when the message has not been sent.

* There's an application called ksms, https://github.com/estradanic/ksms , which solves some of these problems.
    * However, it maintains its own addressbook - but I already have an application for that: Thunderbird's Cardbook.
    * It displays the device's ID rather than its name.
Perhaps I should have tried to fix this, but there were no instructions about how to build it (and besides, I wanted to learn pyqt5).

What I wanted was a way to open the contact in Cardbook, click on the number, and have the application open with the phone number present.

I couldn't decide whether to call this KDE Complete SMS or KDE Command-line SMS.
It's complete because it plugs the hole in the KDE SMS facility.
It's command-line so it can be invoked from the commandline, which is key to the Cardbook integration that I wanted.

Thus: kdecsms

This is my first Qt application, so comments or improvements will be welcome.
I doubtless did some things in a clucky way.


## Installation

Though it is called kdecsms, it actually should be able to run on any desktop so long as the prerequisites are installed.

On Debian, Ubuntu and Mint, running

```console
bash install.sh
```

should be sufficient. Otherwise, to install it manually, follow these steps:

* kdeconnect
    * `sudo apt-get install kdeconnect`
* python3
    * Already installed I believe on every KDE desktop, but if not, then `sudo apt-get install python3`.
* pyqt5
    * Also already installed on KDE desktop, but if not: `sudo apt-get install python3-pyqt5`.

Of course you'll need Qt itself, but the pyqt5 installation should bring it in if it's not present.
I don't know how to do these things on Windows, but there should be instructions somewhere.

To get it to run, just put `kdecsms.py` somewhere in your path - /usr/local/bin should do nicely.
You should be able to remove the `.py` from the filename if you want, so long as it has x permission.


## Setup for Thunderbird/Cardbook

* First, make sure you have the plugin CardBook installed.
* Then, check if you already have a `callto` action configured.
* Go to Edit > Preferences > Attachments, and see if there is an action defined for `callto`.
* If there is, you will need to delete it.
(You probably don't have one configured unless you use a SIP autodialer on your computer.
If you do, you will have to choose what you want to happen when you click a phone number.)
* Go to the Cardbook tab, open a contact.
* In the right panel, the contact's phone number(s) will be displayed as hyperlinks.
* Click one of them. You should see a "Launch Application" window asking you to choose something to run.
Click `Choose`, start from `Filesystem` and navigate to `/usr/local/bin/kdecsms.py`, and click `Open`.
* Be sure to click the "Remember my choice for callto links" checkbox.
* Click `Open link`.

You should see a window ready to send your SMS.

I should add that the explanation of the use of callto links is sort of sparse in the Thunderbird/Cardbook documentation.


## Adding to KDE menu

* Put the icon somewhere: `sudo cp kdecsms.gif /usr/local/src`
* Right click on the K button, select `Edit Applications...`
* Right click on `Utilities`, select `Add Item..`, type in kdecsms.
* Flll in Name: "kdecsms", Description: "KDE Complete SMS", Command: "/usr/local/bin/kdecsms.py"
* Click the icon and select `/usr/local/src/kdecsms.png`
* Click `Save`


## Use

It's all pretty self explanatory, but one subtle point: The message box is greyed out if there is no selected phone, or if there is no
To: number in the input box.
If you add a phone to the To: box, you will need to hit the `Refresh` button under the phones to get the message box back.
However, if you change the To: number, you don't have to refresh (though it won't hurt, of course).


## TODO

* There should be a package for this.
* The package should include an install that puts it in the command menu
* It shouldn't really invoke kdeconnect-cli via a shell when a direct fork-exec would do.
* The logo sucks.
* It seems that pyqt doesn't use the system theme.

## Author

* **Mitch Golden** - *Initial work* - [mgolden](https://github.com/mgolden)
* Norman Koch - Writing the Installer [NormanTUD](https://github.com/NormanTUD)

## License

This may be redistributed under the GPL v2 or GPL v3.  (Which are the licenses of kdeconnect itself.)
See the LICENSE file for details.
