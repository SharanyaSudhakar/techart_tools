import QtQuick 2.7
import Painter 1.0

PainterPlugin 
{
    property var mapsTool : null

    //imports the GenerateMapsDialog box as a component. Dont need an import statement
    GenerateMapsDialog
    {
        //id is matched to the one given inside GenerateMapsDialog
        id:window
    }

	Component.onCompleted:
	{
       alg.log.info("Bake Maps Plugin Loaded Successfully")
       mapsTool = alg.ui.addWidgetToPluginToolBar("ToolBarWidget.qml");
       mapsTool.windowref = window
	}

    onNewProjectCreated: 
    {
        window.visible = true
    }
}
