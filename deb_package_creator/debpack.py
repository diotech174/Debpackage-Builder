import sys
import os
import shutil
from ui_program import Ui_Program
from pathlib import Path
from threading import Thread
import subprocess
from time import sleep
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QDialog, QLabel, QDialogButtonBox, QVBoxLayout, QLineEdit, QFileDialog


# exec shell commands
def execShellCommand(self, sudoPass, cmdBash):
    returnCode = os.system('echo %s|sudo -S %s' % (sudoPass, cmdBash))
    if returnCode == 256:
        try:
            shutil.rmtree(self.folder)
            dlg = QDialog(self)
            dlg.setWindowTitle("Warning")
            QBtn = QDialogButtonBox.Ok
            dlg.buttonBox = QDialogButtonBox(QBtn)
            dlg.buttonBox.accepted.connect(dlg.accept)
            dlg.label = QLabel()
            dlg.label.setText("Erro: root password is invalid!")
            dlg.layout = QVBoxLayout()
            dlg.layout.addWidget(dlg.label)
            dlg.layout.addWidget(dlg.buttonBox)
            dlg.setLayout(dlg.layout)
            dlg.exec()
            self.txtResult.clear()
            self.btnCompile.setEnabled(False)
            self.btnBuildProject.setEnabled(True)
        except Exception as e:
            print(str(e))


# build a deb file
def buildDebFile(self, cmdBash):
    self.btnBuildProject.setEnabled(False)
    self.btnCompile.setEnabled(False)
    self.txtResult.insertPlainText("Wait for build the package........\n")
    p = subprocess.Popen(cmdBash, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while p.poll() is None:
        sleep(0.5)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        th = Thread(target=showResult, args=(
            self,
            current_time + " .................................................."
        ))
        th.daemon = True
        th.start()

    exitCode = p.returncode

    if (exitCode == 0):
        self.MessageBox("Success!", "Build .deb package is successfully!")
        os.system(
            'open "%s"' % str(
                Path.home()
            )+"/debcreator/build/"
        )
        self.btnBuildProject.setEnabled(True)
        self.btnCompile.setEnabled(True)
        th = Thread(target=showResult, args=(
            self,
            "\nPackage build successfully!"
        ))
        th.daemon = True
        th.start()


# show result to processes
def showResult(self, s):
    self.txtResult.insertPlainText(s+"\n")


# copy files
def copyFile(self, file, output):
    cmdBash = "cp " + file + " " + output
    p = subprocess.Popen(cmdBash, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while p.poll() is None:
        sleep(0.5)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(current_time + " ..................................................")
    exitCode = p.returncode

    if (exitCode == 0):
        th = Thread(target=showResult, args=(
            self,
            "Copy file: "+file+" to "+output
        ))
        th.daemon = True
        th.start()
        self.filesCopied += 1
        if self.filesCopied == self.totalFiles:
            self.btnCompile.setEnabled(True)
            # set permition for build package
            cmdBash = " chmod -R 0755 " + self.folder + " *"
            th1 = Thread(target=execShellCommand, args=(self, self.sudoPass, cmdBash))
            th1.daemon = True
            th1.start()
            # set permition for build package
            cmdBash = " chmod +x " + self.folder
            th2 = Thread(target=execShellCommand, args=(self, self.sudoPass, cmdBash))
            th2.daemon = True
            th2.start()
            # build .deb file
            self.btnBuildProject.setEnabled(True)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Program()
        self.ui.setupUi(self)
        self.lbl = self.ui.label
        self.txtPackageName = self.ui.txtPackagename
        self.txtDesc = self.ui.txtDesc
        self.txtMaintainer = self.ui.txtMaintainer
        self.txtVersion = self.ui.txtVersion
        self.txtDepends = self.ui.txtDepends
        self.txtIconFile = self.ui.txtIconFile
        self.txtResult = self.ui.txtResult
        self.txtResult.textChanged.connect(self.scrollToBottom)
        self.txtProjectFiles = self.ui.txtProjectFiles
        self.txtRootFolder = self.ui.txtRootFolder
        self.txtExecutable = self.ui.txtExecutable
        self.cbOpenInTerminal = self.ui.cbOpenInTerminal
        self.cbShowNotify = self.ui.cbShowNotify
        # buttons and actions
        self.btnSearchIcon = self.ui.btnSearchIcon
        self.btnSearchIcon.clicked.connect(self.openIconFile)
        self.btnBuildProject = self.ui.btnBuildProject
        self.btnBuildProject.clicked.connect(self.buildPackage)
        self.btnCompile = self.ui.btnCompile
        self.btnCompile.clicked.connect(self.createDebFile)
        self.btnSearchRootFolder = self.ui.btnSearchRootFolder
        self.btnSearchRootFolder.clicked.connect(self.openRootFolder)
        self.btnSearchExecutable = self.ui.btnSearchExecutable
        self.btnSearchExecutable.clicked.connect(self.openExecutableFile)
        # global vars
        self.folder = ""
        self.sudoPass = ""
        self.filesCopied = 0  # total files copy finished
        self.totalFiles = 2  # total project files
        # combobox values
        self.cbxCategory = self.ui.cbxCategory
        self.cbxArchitecture = self.ui.cbxArchitecture
        # add categories of application
        self.categories = [
            self.tr('Other'),
            self.tr('Internet'),
            self.tr('Development'),
            self.tr('Education'),
            self.tr('Science'),
            self.tr('Office'),
            self.tr('Graphics'),
            self.tr('Network'),
            self.tr('Game'),
            self.tr('Video'),
            self.tr('System'),
            self.tr('Utility')
        ]
        self.cbxCategory.addItems(self.categories)
        # add architectures
        self.architectures = [
            self.tr('amd64'),
            self.tr('i686'),
            self.tr('any')
        ]
        self.cbxArchitecture.addItems(self.architectures)

    # Move txtResult scroll to bottom
    def scrollToBottom(self):
        scroller = self.txtResult.verticalScrollBar()
        scroller.setValue(scroller.maximum())

    # Validate form
    def validForm(self):
        valid = True
        if self.txtPackageName.text().strip() == "":
            self.MessageBox("Warning", "Enter the package name!")
            self.txtPackageName.setFocus()
            valid = False
        if self.txtDesc.text().strip() == "" and valid:
            self.MessageBox("Warning", "Enter the project description!")
            self.txtDesc.setFocus()
            valid = False
        if self.txtMaintainer.text().strip() == "" and valid:
            self.MessageBox("Warning", "Enter the project maintainer name!")
            self.txtMaintainer.setFocus()
            valid = False
        if self.txtVersion.text().strip() == "" and valid:
            self.MessageBox("Warning", "Enter the project version!")
            self.txtVersion.setFocus()
            valid = False
        if self.txtRootFolder.text().strip() == "" and valid:
            self.MessageBox("Warning", "Enter the project root path!")
            self.txtRootFolder.setFocus()
            valid = False
        if self.txtIconFile.text().strip() == "" and valid:
            self.MessageBox("Warning", "Enter the project icon file!")
            self.txtIconFile.setFocus()
            valid = False
        if self.txtExecutable.text().strip() == "" and valid:
            self.MessageBox("Warning", "Enter the project executable file!")
            self.txtExecutable.setFocus()
            valid = False
        return valid

    def buildPackage(self):
        if self.validForm():
            if self.getRootPassword():
                self.createProjectFile()

    # Show messagebox
    def MessageBox(self, title, msg):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        QBtn = QDialogButtonBox.Ok
        dlg.buttonBox = QDialogButtonBox(QBtn)
        dlg.buttonBox.accepted.connect(dlg.accept)
        dlg.label = QLabel()
        dlg.label.setText(msg)
        dlg.layout = QVBoxLayout()
        dlg.layout.addWidget(dlg.label)
        dlg.layout.addWidget(dlg.buttonBox)
        dlg.setLayout(dlg.layout)
        dlg.exec()

    # Open image file to make icon application
    def openIconFile(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilters(["Images (*.png *.jpg *.ico)"])
        dlg.selectNameFilter("Images (*.png *.jpg *.ico)")
        if dlg.exec():
            selectedFiles = dlg.selectedFiles()
            self.txtIconFile.setText(selectedFiles[0])

    # Open executable file of application
    def openExecutableFile(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        if dlg.exec():
            selectedFiles = dlg.selectedFiles()
            self.txtExecutable.setText(selectedFiles[0])

    # Open root folder for create project
    def openRootFolder(self):
        self.totalFiles = 2
        self.filesCopied = 0
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)
        if dlg.exec():
            selectedFiles = dlg.selectedFiles()
            self.txtRootFolder.setText(selectedFiles[0])
            self.scanRootFolder()

    # Scan the root folder for create project files
    def scanRootFolder(self):
        self.txtProjectFiles.clear()
        for root, dirs, files in os.walk(self.txtRootFolder.text()):
            for name in files:
                self.totalFiles += 1
                self.txtProjectFiles.insertPlainText(
                    self.txtRootFolder.text()+"/"+name+"\n"
                )

    # Create SH file for exec dpkg commands
    def createDebFile(self):
        th3 = Thread(target=showResult, args=(self, "Making .deb file..."))
        th3.daemon = True
        th3.start()
        cmdBash = "dpkg-deb -b "+self.folder
        cmdBash += "/ "+self.folder
        cmdBash += "_"+self.txtVersion.text()+".deb"
        th4 = Thread(target=buildDebFile, args=(self, cmdBash))
        th4.daemon = True
        th4.start()

    # Create control file
    def createControlFile(self):
        txt = "Package: " + self.txtPackageName.text().replace(" ", "", 10)
        txt += "\nVersion: " + self.txtVersion.text()
        txt += "\nArchitecture: " + self.cbxArchitecture.currentText()
        txt += "\nDepends: " + self.txtDepends.text()
        txt += "\nMaintainer: " + self.txtMaintainer.text()
        txt += "\nDescription:" + self.txtDesc.text()
        if not os.path.exists(self.folder+"/DEBIAN"):
            os.makedirs(self.folder+"/DEBIAN")
        with open(self.folder+"/DEBIAN/control", 'w') as f:
            f.write(txt.strip()+"\n")
        th = Thread(target=showResult, args=(self, "Making control file..."))
        th.daemon = True
        th.start()

    # Create .desktop file
    def createShortCutFile(self):
        pathToShortCut = self.folder+"/usr/share/applications/"
        binFolderPath = "/etc/"+self.txtPackageName.text().replace(" ", "", 10).lower()
        arr1 = self.txtIconFile.text().split("/")
        iconFile = arr1[len(arr1)-1]
        arr2 = self.txtExecutable.text().split("/")
        execFile = arr2[len(arr2)-1]
        txt = "[Desktop Entry]"
        txt += "\nName="+self.txtPackageName.text()
        txt += "\nIcon="+binFolderPath+"/"+iconFile
        txt += "\nType=Application"
        txt += "\nCategories="+self.cbxCategory.currentText()
        txt += "\nExec="+binFolderPath+"/"+execFile
        txt += "\nStartupNotify="+str(self.cbShowNotify.isChecked())
        txt += "\nTerminal="+str(self.cbOpenInTerminal.isChecked())
        if not os.path.exists(pathToShortCut):
            os.makedirs(pathToShortCut)
        with open(
            pathToShortCut+self.txtPackageName.text().replace(" ", "", 10).lower() + ".desktop", 'w'
        ) as f:
            f.write(txt)
        # makin .desktop file in thread
        th = Thread(target=showResult, args=(self, "Making desktop file..."))
        th.daemon = True
        th.start()

    # Copy selected files projects for create package
    def copyFilesProject(self):
        self.btnCompile.setEnabled(False)
        self.btnBuildProject.setEnabled(False)
        p_folders = self.folder+"/etc/"+self.txtPackageName.text().replace(" ", "", 10).lower() +"/"
        if not os.path.exists(p_folders):
            os.makedirs(p_folders)
        cmdBash = " chmod -R 777 " + self.folder + "/*"
        th1 = Thread(target=execShellCommand, args=(self, self.sudoPass, cmdBash))
        th1.daemon = True
        th1.start()
        files = self.txtProjectFiles.toPlainText().split("\n")
        for fileLine in files:
            if len(fileLine) > 0:
                arr = fileLine.split("/")
                file = arr[len(arr)-1]
                th = Thread(target=copyFile, args=(
                    self, fileLine, p_folders+file
                ))
                th.daemon = True
                th.start()
        # copy icon file
        filename1 = self.txtIconFile.text().replace(" ", "\\ ", 10)
        arr1 = filename1.split("/")
        iconFile = arr1[len(arr1)-1]
        th2 = Thread(target=copyFile, args=(
            self, filename1, p_folders+iconFile
        ))
        th2.daemon = True
        th2.start()
        # copy executable file
        filename2 = self.txtExecutable.text().replace(" ", "\\", 10)
        arr2 = filename2.split("/")
        execFile = arr2[len(arr2)-1]
        th3 = Thread(target=copyFile, args=(
            self, filename2, p_folders+execFile
        ))
        th3.daemon = True
        th3.start()

    # Create files of project
    def createProjectFile(self):
        self.txtResult.clear()
        self.folder = str(
            Path.home()
        )+"/debcreator/build/"+self.txtPackageName.text().replace(" ", "", 10).lower()
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
            th = Thread(target=showResult, args=(
                self, "Make folder project: " + self.folder
            ))
            th.daemon = True
            th.start()
            self.txtResult.clear()
            self.createControlFile()
            self.createShortCutFile()
            self.copyFilesProject()
        else:
            msg = "Folder: \"" + self.folder + "\" is not empty!"
            th = Thread(target=showResult, args=(self, msg))
            th.daemon = True
            th.start()
            self.MessageBox("Warning", msg)

    # Dialog root passwd
    def getRootPassword(self):
        self.sudoPass = ""
        dlg = QDialog(self)
        dlg.setWindowTitle("Root Password:")
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        dlg.buttonBox = QDialogButtonBox(QBtn)
        dlg.buttonBox.accepted.connect(dlg.accept)
        dlg.buttonBox.rejected.connect(dlg.reject)
        dlg.txtPass = QLineEdit()
        dlg.txtPass.setMaxLength(30)
        dlg.txtPass.setEchoMode(QLineEdit.Password)
        dlg.layout = QVBoxLayout()
        dlg.layout.addWidget(dlg.txtPass)
        dlg.layout.addWidget(dlg.buttonBox)
        dlg.setLayout(dlg.layout)
        if(dlg.exec()):
            self.sudoPass = dlg.txtPass.text()
            if dlg.txtPass.text().strip() != "":
                return True
            else:
                self.MessageBox("Warning", "Enter the root password!")
                self.getRootPassword()
                return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
