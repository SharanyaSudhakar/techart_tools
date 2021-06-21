import AlgWidgets 2.0
import QtQuick 2.7
import QtQml 2.0
import Qt.labs.platform 1.0

Item {
    id: saveWindow

    function openDialog()
    {
        msgDialog.visible = true
    }

    FileDialog {
        id:fileDlg
        title: "Save As"
        defaultSuffix: ".spp"
        fileMode: FileDialog.SaveFile
        modality: Qt.ApplicationModal
        nameFilters: [ "Substance files (*.spp)", "All files (*)" ]
        folder:alg.project.isOpen()? alg.project.lastImportedMeshUrl() :shortcuts.home

        onAccepted:
        {
            alg.project.save(fileDlg.file, alg.project.SaveMode.Full)
        }
    }

    MessageDialog {
        id: msgDialog
        title: "Save As?"
        modality: Qt.ApplicationModal
        text: "Current project has been modified. \n\n Do you want to save your changes?"
        detailedText: "To not save a file means that its existing contents will be lost."
        buttons: MessageDialog.Save | MessageDialog.Discard | MessageDialog.Cancel
        onSaveClicked:  alg.project.needSaving()? fileDlg.open() : alg.project.saveAndClose(alg.project.SaveMode.Full)
        onCancelClicked: alg.log.info("save operation cancelled")
        onDiscardClicked: alg.project.close()
        Component.onCompleted: visible = false
    }
}
