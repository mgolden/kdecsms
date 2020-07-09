#!/usr/bin/python3

# KDE Complete SMS

# -------- CONFIG -------

# Path to kdeconnect_cli
kdeconnect_cli = "/usr/bin/kdeconnect-cli"

# Dimensions of window at startup
initial_width = 310
initial_height = 350

# All the strings on the application interface, to be used for localization
allStrings = {
    "en": {
        "To:": "To:",
        "Available Phones": "Available Phones",
        "Refresh": "Refresh",
        "Sent": "Sent",
        "Failed to send": "Failed to send",
        "Message": "Message",
        "Send": "Send",
        "No Phones": "No Phones"
    }
}

# (See end of the class for the icon data)

# ----- END CONFIG-------

#############################################################################
##
## Copyright (C) 2019 Mitchell Golden
##
## This file implements the KDE Complete SMS program.
##
## You may use this file under the terms of the GNU GPL v2 or v3.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
#############################################################################


import sys
import os
import re
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QDialog, QWidget, QSizePolicy,
        QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
        QPushButton, QRadioButton, QPlainTextEdit)
from PyQt5.QtGui import QIcon, QPixmap

class WidgetGallery(QDialog):
    
    # The current device we're using
    device = None
    
    # Qt objects
    mainLayout = None
    toBox = None
    toEdit = None
    phonesBox = None
    messageBox = None
    messageEdit = None
    statusWidget = None
    
    # Used for localized strings
    strings = None
    
    def __init__(self, argv, toNumber, language=None, parent=None):
        super(WidgetGallery, self).__init__(parent)

        if language is None or language not in allStrings.keys():
            language = "en"
        self.strings = allStrings[language]

        if not toNumber:
            toNumber = ""

        self.mainLayout = QVBoxLayout()
        self.toBox = self.createToBox(toNumber)
        self.messageBox = self.createMessageBox()
        self.mainLayout.addWidget(self.messageBox)
        self.reset()
        self.setLayout(self.mainLayout)

        self.setWindowTitle("kdecsms")
        # Remove the help button - it's not implemented (and probably not necessary)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint);
        q = QPixmap()
        q.loadFromData(self.iconData)
        self.setWindowIcon(QIcon(q))


    # There is intermittent bad behavior when the show method() is called from inside the constructor
    def showAndSet(self):
        self.show()
        self.resize(initial_width, initial_height)
        # The focus goes in messageEdit only if it's enabled.  toEdit is always enabled.
        if self.messageEdit.isEnabled():
            self.messageEdit.setFocus()
        else:
            self.toEdit.setFocus()


    def runcmd(self, command):
        # https://stackoverflow.com/questions/3503879/assign-output-of-os-system-to-a-variable-and-prevent-it-from-being-displayed-on
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        return (result.stdout, result.stderr)


    zero_devices = "0 devices found"
    def getPhones(self):
        # print("getPhones")
        # 2020-07-08 - At some point it seems that the message "0 devices found" moved from out to err
        command = " ".join([kdeconnect_cli, "-a", "--id-name-only"])
        (out,err) = self.runcmd(command)
        if err:
            if err[0:self.zero_devices.__len__()] == self.zero_devices:
                res = []
            else:
                print(err)
                sys.exit(1)
        else:
            res = out.split("\n")
            res = [x for x in res if x] # remove blank lines; there is one on end
            if res and res[0] == "0 devices found":
                res = []
        phones = []
        for line in res:
            i = line.find(" ")
            phone = {}
            if i>-1:
                phone["device"] = line[0:i]
                phone["name"] = line[i+1:].strip()
            else:
                phone["device"] = line.strip()
                phone["name"] = "?"
            phones.append(phone)
        return phones


    def setDevice(self, device):
        self.device = device
        # print("device is %s" % device)


    def unlinkBox(self, box):
        if box:
            self.mainLayout.removeWidget(box)

    def deleteBox(self, box):
        if box:
            self.unlinkBox(box)
            box.setParent(None)
            box.deleteLater()

    def getToNumber(self):
        return self.toEdit.text().strip().replace("'", "") # remove any single quotes (prevent injections)

    
    def reset(self):
        # Kill old widget if it's present
        self.unlinkBox(self.toBox)
        self.deleteBox(self.phonesBox)
        self.unlinkBox(self.messageBox)
        self.phonesBox = self.createPhonesBox()
        self.mainLayout.addWidget(self.toBox)
        self.mainLayout.addWidget(self.phonesBox)
        self.mainLayout.addWidget(self.messageBox)
        if not (self.device and self.getToNumber()):
            # If we didn't set a device, then disable sending
            self.messageBox.setDisabled(True)
            self.toEdit.setFocus()
        else:
            self.messageBox.setDisabled(False)
            self.messageEdit.setFocus()

    def createToBox(self, toNumber):
        toBox = QGroupBox()
        layout = QHBoxLayout()
        
        layout.addWidget(QLabel(self.strings["To:"]))
        self.toEdit = toEdit = QLineEdit(toNumber)
        toEdit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        layout.addWidget(toEdit)
        toBox.setLayout(layout)
        return toBox
        
                         
    # Function factory for phone button slots
    # https://stackoverflow.com/questions/3431676/creating-functions-in-a-loop
    def make_f(self, d):
        def f():
            self.setDevice(d)
        return f
        
    
    def createPhonesBox(self):
        phonesBox = QGroupBox(self.strings["Available Phones"])
        layout = QVBoxLayout()

        phones = self.getPhones()

        checked = False
        index = 0
        for phone in phones:
            device = phone["device"]
            rb = QRadioButton(phone["name"])
            if not checked:
                rb.setChecked(True)
                self.setDevice(device)
                checked = True
            layout.addWidget(rb)
            # https://www.tutorialspoint.com/pyqt/pyqt_signals_and_slots.htm
            rb.clicked.connect(self.make_f(device))
            index += 1
        if not checked:
            self.setDevice(None)
            layout.addWidget(QLabel(self.strings["No Phones"]), alignment=Qt.AlignCenter)


        button = QPushButton(self.strings["Refresh"])
        button.setDefault(True)
        layout.addWidget(button, alignment=Qt.AlignRight)
        button.clicked.connect(self.reset)
        
        phonesBox.setLayout(layout)
        return phonesBox


    def send_message(self):
        # Note: use single quotes around the arguments to prevent injection-type attacks.
        message = self.messageEdit.toPlainText().rstrip().replace("'", "'\"'\"'") # Note - single quotes go in double quote
        toNumber = self.getToNumber()
        command = "%s --device '%s' --destination '%s' --send-sms '%s'" % (kdeconnect_cli, self.device, toNumber, message)
        # print(command)
        (out, err) = self.runcmd(command)
        # print(out)
        # print(err)
        if not out and not err:
            msg = self.strings["Sent"]
            # print(msg)
            self.statusWidget.setText(msg)
            self.messageEdit.setPlainText("")
        else:
            msg = self.strings["Failed to send"]
            # print(msg)
            self.statusWidget.setText(msg)
            # Don't clear the text, but do rescen for phones
            self.reset()
        self.messageEdit.setFocus()


    def createMessageBox(self):
        messageBox = QGroupBox(self.strings["Message"])
        layout = QVBoxLayout()

        self.messageEdit = messageEdit = QPlainTextEdit()

        messageEdit.setPlainText("")

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(messageEdit)

        bottomLayout = QHBoxLayout()

        self.statusWidget = statusWidget = QLabel("")
        bottomLayout.addWidget(statusWidget, alignment=Qt.AlignCenter)

        button = QPushButton(self.strings["Send"])
        button.setDefault(True)
        button.clicked.connect(self.send_message)
        bottomLayout.addWidget(button, alignment=Qt.AlignRight)
        
        layout.addLayout(bottomLayout)
        messageBox.setLayout(layout)
        
        return messageBox


    # It's a bit clunky to code the icon here, but it keeps everything contained in a single file.
    iconData = (
        b'GIF89a0\x000\x00\xf6\x00\x00\x1f\x97\xef\x1e\x99\xee\x1e\x97\xf2\x17\x9a\xf7\x1d\x99\xf3\x1d\x96\xf8\x14\x9b\xfb\x19\x99\xf8%\x96\xe7'
        b'*\x96\xe6-\x99\xe6"\x97\xed*\x97\xea#\x99\xec,\x9a\xea1\x97\xe13\x9b\xe5:\x9f\xe72\x9e\xec9\x9e\xe8!\x96\xf2#\x9c\xf3*'
        b'\x9e\xf37\xa2\xec;\xa1\xeb-\xa0\xf32\xa2\xf4;\xa6\xf4A\x9f\xdcM\xa0\xdaa\xac\xdeF\xa4\xe6J\xa5\xe5O\xa8\xe5A\xa5\xecC\xab'
        b'\xeaK\xab\xedT\xab\xe5X\xae\xe5R\xae\xeb[\xaf\xeaW\xb1\xeb[\xb2\xebD\xaa\xf5K\xae\xf5S\xb1\xf5\\\xb5\xf6e\xb4\xe6d\xb5\xe9'
        b'l\xbb\xecq\xb9\xe7|\xbe\xe7s\xbb\xeb{\xbe\xec`\xb7\xf6e\xb9\xf6n\xbd\xf7r\xbf\xf7v\xc0\xed~\xc2\xedv\xc1\xf7y\xc4\xf5}'
        b'\xc4\xf8\x80\xc1\xe6\x83\xc4\xeb\x8c\xc7\xea\x8e\xcc\xef\x96\xcd\xee\x9b\xce\xed\x9c\xd2\xee\x84\xcb\xf4\x83\xc7\xf8\x87\xc9\xf8\x8c\xcb\xf9\x94\xcf\xf5\x93\xce'
        b'\xf9\x9c\xd6\xf5\x9b\xd2\xf9\xa3\xd3\xed\xab\xd7\xef\xbb\xdc\xef\xa0\xd6\xf2\xa8\xd7\xf2\xad\xda\xf2\xa5\xd6\xfa\xac\xd9\xfa\xb4\xdd\xf3\xba\xde\xf3\xb3\xdd\xfa'
        b'\xb9\xdf\xfb\xb3\xe2\xf7\xbc\xe1\xf5\xbd\xe1\xfb\xc3\xe3\xf4\xcc\xe7\xf6\xc3\xe9\xf7\xcc\xea\xf6\xc1\xe2\xfb\xc9\xe6\xfc\xcd\xea\xfb\xd2\xec\xf6\xdb\xee\xf5\xd5'
        b'\xec\xfb\xdc\xef\xfd\xd7\xf0\xf7\xdd\xf2\xf7\xdd\xf2\xfc\xe4\xed\xf4\xee\xf8\xf7\xe3\xf4\xfd\xea\xf5\xfd\xe7\xf9\xfc\xeb\xf9\xfb\xf1\xf7\xf7\xf3\xfa\xf7\xfb\xfb'
        b'\xf6\xf4\xfb\xfc\xfb\xfc\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04'
        b'\x00\x00\x00\x00\x00,\x00\x00\x00\x000\x000\x00\x00\x07\xfe\x80\x04\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x8d\x02'
        b'\x95\x91\x02\x97\x02\x01\x97\x04\x9e\x98\x8e\x0b\x08\x10\x12\x0b\x83\x14\x9f\xa1\x87\x9a\x84\rZfmV\x14\x01\x04\x08QWF*\x0e\x02\x07\xab'
        b'\x9b\x85\njsu]\xa9\x04;tsso$\x0b\xc0\x89\x15\x8c\x97\x9d\x83\x0emuu[\xa7%osrt5\x01\x06\xa0\xa1\x01'
        b'\x0c+\x08\x82\n\xd8s]\x0b\x10ds\xcaL\xb5\xc7\xa1\x9a\x0bJrR\x18\x01\xc2u\xe8\\a eY\x1d/\x0eV\x15\xaa \xe2'
        b'M\xc04S`\xb4!\x06\xe5\xc7\xb29j>($d\x80V\x91et\xd2\x98h\xb7\xc6\x1b\x1d:06\x12\xe2D`\x02\x9a9a'
        b'0\xb0\xabsQ\x19\x14N\xe50I#P\x0b\xc1\x962\x17(\\\xcb\xd6\x06\xdc\x1c7!\n\xd4B\xb4\xd3Q\x80\x01\xb5*xxC'
        b'#\xd55b]\x9c\xd0\x9cC\x06\x82JA*\xac\xa4\x81\xf3\xe6\x02\xcfkt\xea\\\xb1@F\x0e1&\xfe\xf7\x14*\x01I&A\xad'
        b'\xabj\x17\xa0pCLN\x8cZ9)\x19Q6\xc7\x0c\x82^C\x05\x12X0\x84\x8e\xdb7\x1aU\x99\xfb@\x03JY\x9e\x0c\xd4d'
        b'\xbb\xf2\xc9\x81\x17\x90]\xbc\x06\x96Tk\x00\x877@\x16\x04\xb8*g\n\x85\x05\x16P\xb8\xa5\xf3\x85\xc5hJ\xaa\xbb\xbc\x11\xe1\xabG'
        b'\x0c\x12\t)\x10qR\x03\xc8\x87\x06*\x97\xa6\x80S\x87L\x89\xc3\xaa\x1c\x0899\x83B\x81\xaf\x03\x16H \xb3\xf5\r\x13\x18#L'
        b"\xec\x00\xf3\xed\xdb\x8eD\xd7'\t \xc1\x86N\x1c)A\xd0\x9ct\xace\x07\x19eZ\xd4\xa9\x140@\x80\x0c.*\x10\xd0@\x07\xde"
        b'\xcc1\x84j\x0e\x14\xf1\x85Y_y\x02@\x02\r\x0c  \x18u\xc8\xf1\x02O\x82< a\x83\x87,\xf0\x84\x1cl@\xb0!\x86_'
        b"\xf1\xb4\x94 \xbe\x10p\x81\n'x\x12\x00`)\x1e\xd2T&\x9ftr@'\xad\x9cHb\x89<2\xe5\x02\x12G\xb80\xa3 \x15"
        b'l\xd0\xc2\n3f\xfe\xa0\xc1\x90\x15h`\x01!\x15\xac\xd0\xc2\x06C\x12\xe0\x82\x1at\x98aF\x96\x1b\x10r\x83fD\xdd0\x08\x17'
        b'u`QH\x0bt\xb4\xb1\x13\x0fndS\x87\x19-\x10\xc2\x02\x1dXh \xc8\nm\x98q\xcc\x06tT\xb1\x82\x06+`A\x07\x0b'
        b'\x82\x84\x11\xd0\x93\x83PQ\x87\x1b\xd2\xb4PG\x13\x1bh\xc0B\x18tt)\x08\x17jd@\x88\x0bt\xc4)\x80\x0fthJ\xa4\x1b'
        b'M\x14J)\x0e\x83T\xe0F\x18\x8c\x12\xd0D\x1b\x84h@\xc7\x11\x82dP\xc7\x12\x864\x85C\x1d6\x10\xb2\x81\xa8ad\x81E\x16'
        b'\x83\xb8\xd0\xc6\x12\x8c\x1e\x80\xc4\xa0\xbe"\xcaB\x1db.\x94\xaa\x18o.!$!apq\x03\x1d\x88V\xd1D\x12nP @\x06'
        b'g\xd4!F\x12-\xcc\xe8h\xaf\x8aT\xe0\x83\xa1\x01-\xb1S\xb6\x15\xd0\x91\x83\x00\x16\xb8\xc1\x02\xb8;ep\xc4\x18\xd9\xb8q\xc4N'
        b'\x1b\xd4\xc1C\xae2\xbaP\xc5\xa3\x85rA\x00\x15\xc4\xdepF\x05\xfc\xad\x16\x92\x81\rd\xd2J@\x05m\x98IH\x06m\x1cL\x00'
        b'\x12\xd1&\xdaj\xb0\x04\xd8\x10*\x16\xb8Vlm!\\\x98!\x88\x00ItJ\xc8\x12u\x10J@\x18f\xcc\xf8\xaa4(\xab\xea\x83'
        b'\x1b+\x10P\xb1\x1a\x0e\x13\x02\xcb \x16\x88\x01\xc7\x12-(|k\xb1up\xd1\x82\x06\x1b\x80\x8a\xeb\xceYHC\x05\x1c2\x1b\xdd\xaa'
        b'\x0fuT\xd1B\x06\x1b$a0!\x16,q\xc6If\xe4P\x08\x0e\xd8\xa4EG\x13\xf3&\xedB\x1dI\x08\x92\x84\x9a\x82\x0c\xed\xa6'
        b'\x1b}\xe7\x9a\x81\xa8\xb9\xae\xe0\xc2\xd5l\xdb)\xc8\x92\x82X\xe0x\xe4,,\x8e("\xbeT\xd9\xe3\xe6\x9co\x1e\x08\x00;'
    )


# Find the phone number in argv.  Everything else is passed to QApplication
def getArgvToNumber(argv):
    toNumber = None
    newArgv = [argv[0]]
    # Possible first characters of a phone number
    r1 = re.compile("[()+0-9]")
    # Characters not allowed in phones number (i.e. only ( ) space + - . 0-9 are allowed)
    r2 = re.compile("[^() +-.0-9]")
    for arg in argv[1:]:
        # A phone number as an argument will be treated as the recipient
        if r1.match(arg):
            toNumber = arg
        # Thunderbird calls this with callto:THENUMBER (with no spaces or dashes)
        elif arg[0:7]=="callto:":
            toNumber = arg[7:]
        # If it's not recognized, just send it in to Qt.
        else:
            # clean possibly problematic characters out
            newArgv.append(arg)
    if toNumber:
        toNumber = r2.sub("", toNumber)
    return (newArgv, toNumber)


def main():
    (argv, toNumber) = getArgvToNumber(sys.argv)
    app = QApplication(argv)
    # Try to determine the language from the Unix environment
    language = os.environ.get("LANG")
    if language:
        language = re.sub("_.*", "", language)
    widgetGallery = WidgetGallery(argv, toNumber, language=language)
    widgetGallery.showAndSet()
    sys.exit(app.exec_()) 



if __name__ == '__main__':
    # spawn a child so calling process doesn't wait
    pid = os.fork()
    # if fork is successful, just exit
    if pid>0:
        sys.exit(0)
    main()
    
