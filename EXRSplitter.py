
#-------------------------------------------------------------------#
#                                                                   #
#                                                                   #
#                                                                   #
#                                                                   #
#   Nuke script for extracting all channels inside exr file         #
#   and grouping them together for visual/reference purposes        #
#   as well as ease of access for adjustments.                      #
#                                                                   #
#   Created by Jordan Alphonso on 4/15/2013                         #
#   email: jordan@pixelmagicfx.com                                  #
#   version: 1.0                                                    #
#                                                                   #
#                                                                   #
#                                                                   #
#                                                                   #
#-------------------------------------------------------------------#


import nuke as n
import string as str

def EXRSplit():
    
    readNode = n.selectedNode()
    if readNode.Class()=='Read':
        #get resolution
        resX = readNode.width()
        resY = readNode.height()
        
        #get the path to the Read node
        readPath = readNode['file'].value()
        pathArray = str.split(readPath, "/")
        i = 0
        for pathSplit in pathArray:
            if (i == len(pathArray)-1):
                fileName=pathSplit
                break
            i = i+1
        
        #find and store file extension and filename
        nameExts = str.split(fileName, ".")
        i = 0
        for nameExt in nameExts:
            if (i == len(nameExt)-1):
                fileType = nameExt
            i = i+1
        
        if fileType=='exr':
            cStore = ""
            nx = readNode['xpos'].value()
            ny = readNode['ypos'].value()
            
            i = 0
            groupNodes = []
            textNodes = []
            theNames = []
            normalChannels = ['r','g','b','a','red','green','blue','alpha','x','y','z','MX','MY','MZ','NX','NY','NZ','Z']
            
            #does exr file contain other layers?
            otherChannelsExist = False
            for rnc in readNode.channels():
                chans = str.split(rnc, ".")
                if not (chans[0] == 'rgba'):
                    otherChannelsExist = True
                    break
            
            if otherChannelsExist:
                #create dot for organization
                dot = n.createNode('Dot', inpanel = False)
            
                for c in readNode.channels():
                    layerChans = str.split(c, ".")
                    layerName = layerChans[0]
                    channelName = layerChans[1]
                    
                    if not(layerName==cStore) or (channelName not in normalChannels):

                        #extract new layer if found and add it to a group node
                        group = n.createNode('Group', inpanel = False)
                        if channelName in normalChannels:
                            groupName = checkNodeName(layerName)
                        else:
                            groupName = checkNodeName(layerName+'.'+channelName)
                        group['name'].setValue(groupName)
                        
                        group.begin()
                        inp = nuke.createNode('Input', inpanel = False)
                        inp['selected'].setValue('False')
                        
                        if channelName in normalChannels:
                            shuffle = n.createNode('Shuffle', inpanel = False)
                            shuffle.setInput(0,inp)
                            shuffle['in'].setValue(layerName)

                            #if this is only RGBA then we set the alpha to black
                            count = 0
                            for c2 in readNode.channels():
                                shuffleChans = string.split(c2, ".")
                                if shuffleChans[0]==layerName:
                                    count = count+1
                            if count==3:

                                #there are three channels with this layer's name
                                shuffle['alpha'].setValue('black')
                                
                            shuffle['selected'].setValue('True')
                            
                        else:
                            copy = n.createNode('Copy', inpanel = False)
                            copy.setInput(0,inp)
                            copy.setInput(1,inp)
                            for f in ['from0','from1','from2','from3']:
                                copy[f].setValue(c)
                            copy['to0'].setValue('rgba.red')
                            copy['to1'].setValue('rgba.green')
                            copy['to2'].setValue('rgba.blue')
                            copy['to3'].setValue('rgba.alpha')
                            copy['selected'].setValue('True')
                            
                            
                        remove = n.createNode('Remove', inpanel = False)
                        remove['operation'].setValue('keep')
                        remove['channels'].setValue('rgba')
                        n.createNode('Output', inpanel = False)
                        group.end()
                        
                        group.setInput(0,dot)
                        group['postage_stamp'].setValue(True)
                        newXpos = nx - (100*i)
                        group['xpos'].setValue(newXpos)
                        group['ypos'].setValue(ny+250)
                        if layerName=='rgba':
                            group.knob('tile_color').setValue(int(0xaaff55ff))
                        else:
                            group.knob('tile_color').setValue(int(0xe955ffff))
                        
                        groupNodes.append(group)
                        if channelName in normalChannels:
                            theNames.append(layerName)
                        else:
                            theNames.append(layerName+'.'+channelName)
                        i = i + 1
                    cStore = layerName
                
                #contact sheet and text group node
                csGroup = n.createNode('Group', inpanel = False)
                groupName = checkNodeName('EXR_sheet')
                
                csGroup['name'].setValue(groupName)
                csGroup['xpos'].setValue(newXpos)
                csGroup['ypos'].setValue(ny+100)
                csGroup['postage_stamp'].setValue(True)
                
                csGroup.begin()
                
                #contact sheet
                cs = n.createNode('ContactSheet', inpanel = False)
                cs.knob('width').setValue(float(resX))
                cs.knob('height').setValue(float(resY))
                cs['center'].setValue(True)
                cs['roworder'].setValue('TopBottom')
                cs['gap'].setValue(5)
                cs['selected'].setValue(False)
                
                #create another contact sheet node to get outline alpha (so the sheet background will appear grey)
                csMatte = nuke.createNode('ContactSheet', inpanel = False)
                csMatte.knob('width').setValue(float(resX))
                csMatte.knob('height').setValue(float(resY))
                csMatte['center'].setValue(True)
                csMatte['roworder'].setValue('TopBottom')
                csMatte['gap'].setValue(5)
                csMatte['selected'].setValue(False)
                
                numGroups = len(groupNodes)
                
                for i in range(0,numGroups):
                    #create input
                    inp = n.createNode('Input', inpanel = False)
                    
                    #create text for contact sheet
                    t = n.createNode('Text', inpanel = False)
                    t['message'].setValue(theNames[i])
                    t['Transform'].setValue(True)
                    t['box'].setValue([float(resX)*0.01,float(resY)*0.9,float(resX)*0.99,float(resY)*0.98])
                    t['yjustify'].setValue('top')
                    t['size'].setValue(int(resX)/20) #adjust the size based on the EXR resolution
                    
                    #create reformat node
                    ref = n.createNode('Reformat', inpanel = False)
                    ref['type'].setValue('scale')
                    theScale = 1.0 / numGroups
                    ref['scale'].setValue(theScale)
                    
                    #create shuffle node
                    sh = n.createNode('Shuffle', inpanel = False)
                    sh['red'].setValue('black')
                    sh['green'].setValue('black')
                    sh['blue'].setValue('black')
                    sh['alpha'].setValue('white')
                    sh['black'].setValue('white')
                    
                    cs.setInput(i,ref)
                    sh.setInput(0,ref)
                    csMatte.setInput(i,sh)
                    
                    ref['selected'].setValue(False)
                    sh['selected'].setValue(False)
                    
                    
                #choose the best layout depending on the number of layers
                if numGroups==1:
                    cs['rows'].setValue(1)
                    cs['columns'].setValue(1)
                    csMatte['rows'].setValue(1)
                    csMatte['columns'].setValue(1)
                elif numGroups==2:
                    cs['rows'].setValue(1)
                    cs['columns'].setValue(2)
                    csMatte['rows'].setValue(1)
                    csMatte['columns'].setValue(2)    
                elif numGroups==3 or numGroups==4:
                    cs['rows'].setValue(2)
                    cs['columns'].setValue(2)
                    csMatte['rows'].setValue(2)
                    csMatte['columns'].setValue(2)    
                elif numGroups==5 or numGroups==6:
                    cs['rows'].setValue(2)
                    cs['columns'].setValue(3)
                    csMatte['rows'].setValue(2)
                    csMatte['columns'].setValue(3)    
                elif numGroups==7:
                    cs['rows'].setValue(2)
                    cs['columns'].setValue(4)
                    csMatte['rows'].setValue(2)
                    csMatte['columns'].setValue(4)    
                elif numGroups==8 or numGroups==9:
                    cs['rows'].setValue(3)
                    cs['columns'].setValue(3)
                    csMatte['rows'].setValue(3)
                    csMatte['columns'].setValue(3)
                elif numGroups==10 or numGroups==11 or numGroups==12:
                    cs['rows'].setValue(3)
                    cs['columns'].setValue(4)
                    csMatte['rows'].setValue(3)
                    csMatte['columns'].setValue(4)
                else:
                    #do nothing
                    cs['center'].setValue(True)    
                    csMatte['center'].setValue(True)
                
                #create grade node to produce background color
                csMatte['selected'].setValue(True)
                gr = n.createNode('Grade', inpanel = False)
                gr['add'].setValue(0.1)
                gr['maskChannelInput'].setValue('rgba.alpha')
                gr['invert_mask'].setValue('true')
                
                #create invert node
                inv = n.createNode('Invert', inpanel = False)
                inv['channels'].setValue('alpha')
                
                #create premult node
                pre = n.createNode('Premult', inpanel = False)
                
                #create merge and output node
                cs['selected'].setValue(True)
                mer = n.createNode('Merge', inpanel = False)
                n.createNode('Output', inpanel = False)
                csGroup.end()
                
                #connect the groups to the contact sheet group inputs
                for i in range(0,numGroups):
                    csGroup.setInput(i,groupNodes[i])
                
                #select everything except the read node
                for g in groupNodes:
                    g['selected'].setValue(True)
                #for t in textNodes:
                    #t['selected'].setValue(True)
                dot['selected'].setValue(True)
                csGroup['selected'].setValue(True)
                readNode['selected'].setValue(False)
                
            else:
                n.message('This EXR only contains RGBA channels.')
