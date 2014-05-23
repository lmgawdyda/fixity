'''
Created on May 14, 2014
@author: Furqan <furqan@geekschicago.com>
'''

from GUI import GUILibraries
from Core import SharedApp, EmailNotification


# Class to manage the Algorithm change to be implemented for the files to get Hashes
class ChangeAlgorithmGUI(GUILibraries.QDialog):

    def __init__(self,parent_win):
        GUILibraries.QDialog.__init__(self,parent_win)

        self.parent_win = parent_win
        self.setWindowModality(GUILibraries.Qt.WindowModal)
        self.Fixity = SharedApp.SharedApp.App

        self.setWindowTitle('Checksum Manager')
        self.parent_win.setWindowTitle('Checksum Manager')
        self.setWindowIcon(GUILibraries.QIcon(r''+(str((self.Fixity.Configuration.getLogoSignSmall())))))
        self.change_algorithm_layout = GUILibraries.QVBoxLayout()
        self.is_method_changed = False
        self.is_all_files_confirmed = False
        self.notification = GUILibraries.NotificationGUI.NotificationGUI()

    # Distructor
    def destroy(self):
        del self

    # Reject'''
    def reject(self):
        self.parent_win.setWindowTitle("Fixity "+self.Fixity.Configuration.getApplicationVersion())
        super(ChangeAlgorithmGUI,self).reject()


    # Create Show Window'''
    def ShowDialog(self):
        self.show()
        self.exec_()


    # Create Show Window'''
    def SetLayout(self, layout):
        self.change_algorithm_layout = layout


    # Set Layout for Windows'''
    def SetWindowLayout(self):
        self.setLayout(self.change_algorithm_layout)


    # Get Layout'''
    def GetLayout(self):
        return self.change_algorithm_layout

    # All design Management Done in Here'''
    def SetDesgin(self):

        is_enable = True
        all_project_list = self.Fixity.getProjectList()

        if len(all_project_list) <= 0:
            is_enable = False
            all_project_list.append('Create & Save Project')

        self.GetLayout().addStrut(200)
        self.projects = GUILibraries.QComboBox()
        self.projects.addItems(all_project_list)
        self.methods = GUILibraries.QComboBox()
        self.methods.addItems(self.Fixity.Configuration.getCheck_sum_methods())
        self.GetLayout().addWidget(self.projects)
        self.set_information = GUILibraries.QPushButton("Save && Close")
        self.cancel = GUILibraries.QPushButton("Close Without Saving")
        self.GetLayout().addWidget(self.methods)
        self.GetLayout().addWidget(self.set_information)
        self.GetLayout().addWidget(self.cancel)

        self.set_information.clicked.connect(self.Save)
        if not is_enable:
            self.methods.setDisabled(True)
            self.set_information.setDisabled(True)
            self.projects.setDisabled(True)

        self.cancel.clicked.connect(self.Cancel)
        self.projects.currentIndexChanged.connect(self.ProjectChanged)
        self.SetWindowLayout()
        self.ProjectChanged()
        selected_project = self.projects.currentText()
        project_core = self.Fixity.getSingleProject(str(selected_project))

        if project_core.getAlgorithm() == 'md5':
            self.methods.setCurrentIndex(1)
        else:
            self.methods.setCurrentIndex(0)


    def Save(self):

        msgBox = GUILibraries.QLabel('Loading')

        selected_project = self.projects.currentText()
        algo_value_selected = self.methods.currentText()

        if selected_project is None or selected_project == '':
            self.notification.showError(self, "Warning", GUILibraries.messages['no_project_selected'])
            return

        project_core = self.Fixity.getSingleProject(str(selected_project))

        if project_core.getAlgorithm() == algo_value_selected:
            self.notification.showWarning(self, "Failure", GUILibraries.messages['already_using_algorithm'])
            return

        if project_core.getProject_ran_before() == 0 or project_core.getProject_ran_before() == '0':
            self.notification.showError(self, "Failure", GUILibraries.messages['project_not_ran_before'])
            return

        msgBox.setWindowTitle("Processing ....")
        msgBox.setText("Reading Files, please wait ...")
        msgBox.show()

        GUILibraries.QCoreApplication.processEvents()
        project_core.SaveSchedule()
        result_of_all_file_confirmed = project_core.Run(True)
        email_config = self.Fixity.Configuration.getEmailConfiguration()

        msgBox.close()


        if bool(result_of_all_file_confirmed['file_changed_found']):
            email_notification = EmailNotification.EmailNotification()
            self.notification.showWarning(self, 'Failure', GUILibraries.messages['alog_not_changed_mail'])
            email_notification.ErrorEmail(project_core.getEmail_address(), result_of_all_file_confirmed['report_path'], GUILibraries.messages['alog_not_changed_mail'], email_config)
            return

        update_project_algo = {}
        update_project_algo['selectedAlgo'] = algo_value_selected

        self.Fixity.Database.update(self.Fixity.Database._tableProject, update_project_algo, "id='" + str(project_core.getID()) + "'")

        project_core.setAlgorithm(algo_value_selected)

        msgBox.setWindowTitle("Processing ....")
        msgBox.setText("Changing Algorithm, please wait ...")
        msgBox.show()

        GUILibraries.QCoreApplication.processEvents()
        project_core.SaveSchedule()
        project_core.Run()
        msgBox.close()

        self.notification.showInformation(self, "Success", selected_project+"'s " + GUILibraries.messages['algorithm_success'])


    def ProjectChanged(self):
        selected_project = self.projects.currentText()
        project_core = self.Fixity.getSingleProject(str(selected_project))

        if project_core.getAlgorithm() == 'md5':
            self.methods.setCurrentIndex(1)
        else:
            self.methods.setCurrentIndex(0)
        return



    #Close the Dialog Box

    def Cancel(self):
        self.parent_win.setWindowTitle("Fixity "+self.Fixity.Configuration.getApplicationVersion())
        self.destroy()
        self.close()

    # Launch Dialog
    def LaunchDialog(self):
        self.SetDesgin()
        self.ShowDialog()