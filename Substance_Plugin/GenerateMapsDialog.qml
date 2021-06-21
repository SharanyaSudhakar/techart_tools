import AlgWidgets 1.0
import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2
import "."

AlgWindow
{
    id:window
    title:"Bake Maps Plugin"
    visible:false
    //Plugin Width and Height
    width:400
    height:350
 
    //main column layout for all UI
    ColumnLayout 
    {
        id:horizaontalLayout
        anchors.fill:parent

        // Holder for output size section
        Rectangle 
        {
            id:outputSizeBar
            anchors.left:parent.left
            anchors.right:parent.right
            width:390
            height:70
            color:window.color

            //layout pattern for the outputSizeBar
            RowLayout 
            {
                anchors.fill:parent

                //Output Size Label
                AlgLabel 
                {
                    text:"Output Size:"
                    leftPadding:15
                }

                //OutputSize Width Slider with its outputsize label
                ColumnLayout
                {
                    AlgSlider 
                    {
                        id:mapSizeW
                        value:10
                        minValue:5
                        maxValue:13
                        stepSize:1
                        precision:0
                        text:"width"
                    }

                    AlgLabel 
                    {
                        text:Math.pow(2, Math.round(mapSizeW.value))
                        anchors.horizontalCenter:mapSizeW.horizontalCenter
                        topPadding:5
                    }  
                }
                //OutputSize Height Slider with its outputsize label
                ColumnLayout
                {
                    AlgSlider 
                    {
                        id:mapSizeH
                        value:10
                        minValue:5
                        maxValue:13
                        stepSize:1
                        precision:0
                        text:"height"
                    }

                    AlgLabel 
                    {
                        text:Math.pow(2, Math.round(mapSizeH.value))
                        anchors.horizontalCenter:mapSizeH.horizontalCenter
                        topPadding:5
                    }  
                }
            }//end row
        }//end rectangle

        //low poly high poly section
        Rectangle
        {
            anchors.left:parent.left
            anchors.right:parent.right
            width:300
            height:40
            color:window.color

            ColumnLayout
            {
                anchors.horizontalCenter:parent.horizontalCenter
                
                AlgCheckBox 
                {
                    id:useLowAsHigh
                    implicitHeight:20
                    text:"Use Low Poly Mesh as High Poly Mesh"
                    checked:false
                    anchors.horizontalCenter:parent.horizontalCenter
                    onCheckedChanged:
                    {
                        if (checked)
                        {
                            highPolyPathInput.enabled = false
                            openButton.enabled = false
                            highText.enabled = false
                        }
                        else
                        {
                            highPolyPathInput.enabled = true
                            openButton.enabled = true
                            highText.enabled = true
                        }
                    }
                }

                RowLayout
                {
                    AlgLabel
                    {
                        id:highText
                        text:"High Definition Mesh:"
                    }

                    AlgTextInput 
                    {
                        id:highPolyPathInput
                        Layout.preferredWidth:200
                        backgroundColor:enabled? "#1a1a1a" :"#4d4d4d"
                    }

                    Button 
                    {
                        id:openButton
                        implicitHeight:20
                        implicitWidth:20
                        Image
                        {
                            source:openButton.hovered? "browse.svg":"browse_ovr.svg"
                            width:sourceSize.width
                            height:sourceSize.height
                        }
                        onClicked:
                        {
                            fileDialog.title = "Browse High Definition Polygon File"
                            fileDialog.nameFilters = [ "All files (*)" ]
                            fileDialog.selectExisting = true
                            fileDialog.open()
                        }
                    }

                    FileDialog 
                    {
                        id:fileDialog
                        width:1000
                        height:600
                        folder:alg.project.isOpen()? alg.project.lastImportedMeshUrl() :shortcuts.home
                        selectMultiple:false
                        selectFolder:false
                        onAccepted:
                        {
                            if (fileDialog.selectExisting == true) 
                            {
                                console.log(fileDialog.fileUrl)
                                highPolyPathInput.text = fileUrl
                            }
                            else 
                            {
                                console.log(fileDialog.fileUrl)
                            }
                        }
                    }
                }
            }
        }

        //Different maps group
        Rectangle
        {
            anchors.left:parent.left
            anchors.right:parent.right
            width:300
            height:160
            color:window.color

            RowLayout
            {
                anchors.horizontalCenter:parent.horizontalCenter

                //maps label and all maps check box
                ColumnLayout
                {   
                    AlgLabel 
                    {
                        text:"Mesh Maps: "
                    }

                    AlgCheckBox 
                    {
                        id:allckbx
                        text:"ALL Maps"
                        checked:true
                        implicitHeight:25
                        onCheckedChanged:
                        {
                            if (checked)
                            {
                                normalckbx.checked = true
                                wsnckbx.checked = true
                                idckbx.checked = true
                                acckbx.checked = true
                                curveckbx.checked = true
                                posckbx.checked = true
                                thickckbx.checked = true
                            }
                            else
                            {
                                normalckbx.checked = false
                                wsnckbx.checked = false
                                idckbx.checked = false
                                acckbx.checked = false
                                curveckbx.checked = false
                                posckbx.checked = false
                                thickckbx.checked = false
                            }
                        }
                    }
                }

                //maps checkbox grp
                ColumnLayout
                {

                    AlgCheckBox 
                    {
                        id:normalckbx
                        text:"Normal"
                        checked:true
                        onCheckedChanged:
                        {
                            if (!checked)
                                allckbx.checked = false
                        }
                    }

                    AlgCheckBox 
                    {
                        id:wsnckbx
                        text:"World Space Normal"
                        checked:true
                        onCheckedChanged:
                        {
                            if (!checked)
                                allckbx.checked = false
                        }
                    }

                    AlgCheckBox 
                    {
                        id:idckbx
                        text:"Id"
                        checked:true
                        onCheckedChanged:
                        {
                            if (!checked)
                                allckbx.checked = false
                        }
                    }

                    AlgCheckBox 
                    {
                        id:acckbx
                        text:"Ambient Occlusion"
                        checked:true
                        onCheckedChanged:
                        {
                            if (!checked)
                                allckbx.checked = false
                        }
                    }

                    AlgCheckBox 
                    {
                        id:curveckbx
                        text:"Curvature"
                        checked:true
                        onCheckedChanged:
                        {
                            if (!checked)
                                allckbx.checked = false
                        }
                    }

                    AlgCheckBox 
                    {
                        id:posckbx
                        text:"Position"
                        checked:true
                        onCheckedChanged:
                        {
                            if (!checked)
                                allckbx.checked = false
                        }
                    }

                    AlgCheckBox 
                    {
                        id:thickckbx
                        text:"Thickness"
                        checked:true
                        onCheckedChanged:
                        {
                            if (!checked)
                                allckbx.checked = false
                        }
                    }  
                }
            }
        }

        //Final Action Button "Bakes Maps"
        Rectangle
        {
            id:buttonRect
            anchors.left:parent.left
            anchors.right:parent.right
            width:390
            height:50
            color:window.color

            //Mesh Bake and Cancel Button Layout
            RowLayout
            {
                anchors.horizontalCenter:buttonRect.horizontalCenter

                //Bake Mesh Button
                AlgButton
                {
                    id:mapBtn
                    text:"Bake Mesh Maps"

                    Text
                    {
                        opacity:1
                        horizontalAlignment:Text.AlignHCenter
                        color:mapBtn.down ? "#222522" :"#818181"
                        verticalAlignment:Text.AlignVCenter
                        elide:Text.ElideRight
                    }
                    
                    background:Rectangle 
                    {
                        implicitWidth:100
                        implicitHeight:30
                        opacity:enabled ? 1 :0.3
                        color:mapBtn.hovered? "#404040" :"#4d4d4d"
                    }

                    //all info is retrived and sent to mbake maps.
                    onClicked:
                    {
                        var mapSize = [Math.round(mapSizeW.value), Math.round(mapSizeH.value)]
                        var mapslist = [normalckbx.checked, 
                                        wsnckbx.checked, 
                                        idckbx.checked, 
                                        acckbx.checked, 
                                        curveckbx.checked, 
                                        posckbx.checked, 
                                        thickckbx.checked]
                        var highPath = highPolyPathInput.text.slice(8)

                        //if  high poly mesh is not given, default to low mesh.
                        if (!useLowAsHigh.checked)
                        {
                            if (!highPath)
                                useLowAsHigh.checked = true
                        }
                        
                        if (useLowAsHigh.checked)
                        {
                            highPath = null
                        }
                        
                        mapsTool.createMaps(mapSize, useLowAsHigh.checked, highPath, mapslist);
                        window.visible = false // close window after bake command runs
                    }
                } 

                //Cancel Button turns the visiblity of the window to off
                AlgButton
                {
                    id:cancelBtn
                    text:"Cancel"
                    
                    Text
                    {
                        opacity:1
                        horizontalAlignment:Text.AlignHCenter
                        color:mapBtn.down ? "#222522" :"#818181"
                        verticalAlignment:Text.AlignVCenter
                        elide:Text.ElideRight
                    }
                    
                    background:Rectangle 
                    {
                        implicitWidth:100
                        implicitHeight:30
                        opacity:enabled ? 1 :0.3
                        color:mapBtn.hovered? "#404040" :"#4d4d4d"
                    }
                    onClicked:
                    {
                        window.visible = false
                    }
                } 
            }
        }
        
    }
}
