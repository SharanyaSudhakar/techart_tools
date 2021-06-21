import QtQuick 2.7
import QtQuick.Window 2.2
import QtQuick.Layouts 1.2
import QtQuick.Controls 1.4

Item 
{
    width:24
    height:24
    objectName:"baker parameters"
    property alias rectangle:rect
    property var windowref:null
    id:bakemap

    Rectangle 
    {
        id:rect
        anchors.fill:parent
        color:"red"

        MouseArea 
        {
            id:mouseArea
            anchors.fill:parent
            onClicked:
            {
                windowref.visible = true;
            }
        }
    }

    /* 
     * function takes in parameters that is passed to the bake maps function.
     * This is done is two steps. mapSize, isLowAsHigh,highPath are set under commonParameters
     * while mapslist is under TextureSet
     * mapSize:[width, height] somes in as a paired set for the maps dimensions
     * isLowAsHigh:bool, to toggle the "Use_Low_Poly_Mesh_as_High_Poly_Mesh" checkbox
     * highPath:file url, this points to the high poly mesh path 
     * mapList:[normal, worldspace, id, acclusion, curvature, position, thickness]: bool values
     * -- these values represent if a map will get baked or not. False is not baked.
     */
    function createMaps(mapSize, isLowAsHigh, highPath, mapslist)
    {
        var i = 0
        //Accessing the document, the texture set or the baking can anytime throw an error.
        try {
            // get the common baking parameters
            var document = alg.baking.commonBakingParameters()
            document.commonParameters.Output_Size = mapSize
            document.detailParameters.Use_Low_Poly_Mesh_as_High_Poly_Mesh = isLowAsHigh
            document.detailParameters.High_Definition_Meshes.push(highPath)
            alg.baking.setCommonBakingParameters(document) 

            // successful result
            alg.log.info("Baking output size successfully changed:" + mapSize)
            alg.log.info("Is Low poly Mesh used as High Poly:" + isLowAsHigh)
            if(!isLowAsHigh)
                alg.log.info("High Poly Path :" + highPath)

            //maps are retrived and set to enabled true/ false
            var m = alg.mapexport.documentStructure().materials
            var name = m[0].name
            var parameters = alg.baking.textureSetBakingParameters(name)
            for (var bakerName in parameters.definitions) 
            {
                alg.log.info("Enable " + bakerName + " baker")
                parameters.definitions[bakerName] = { enabled:mapslist[i++] };
            }
            alg.baking.setTextureSetBakingParameters(name, parameters)
            
            // bake maps
            alg.baking.bake(name);
        } 

        catch (e) 
        {
            alg.log.warn(e.name)
            alg.log.warn(e.message)
        }
    }
}
