import sys
import os
import PySide2.QtGui as qtg
import csv
import maya.cmds as cmds

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance

def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()

    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
        
class MyWidget(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(MyWidget, self).__init__(parent)   
        
        self.setWindowTitle('Render Curve to Arnold')
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setFixedSize(325, 100)
        
        self.__labelTxt = QtWidgets.QLabel("Curve Width ")
        self.__labelTxt.setGeometry(250, 50, 50, 35)
        
        self.__lineEdit = QtWidgets.QLineEdit(str(1))
        self.__lineEdit.setGeometry(250, 50, 50, 35)
        self.__lineEdit.returnPressed.connect(self.valueChangedLine)
        
        self.__slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.__slider.setGeometry(10, 10, 300, 40)
        self.__slider.valueChanged.connect(self.valueChangedSlide)
        self.__slider.setValue(1)

        
        self.__button_SetCurveToRender = QtWidgets.QPushButton("Set Curve To Render", self)
        self.__button_SetCurveToRender.clicked.connect(self.SetCurveToRender)
        
        self.CurveWidth_widget = QtWidgets.QWidget(self)
        CurveWidth_widget_layout = QtWidgets.QHBoxLayout(self.CurveWidth_widget)
        CurveWidth_widget_layout.addWidget(self.__labelTxt)  
        CurveWidth_widget_layout.addWidget(self.__lineEdit)
        CurveWidth_widget_layout.addWidget(self.__slider)
        
        #  Layout
        #
        
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        
        self.mainLayout.addWidget(self.CurveWidth_widget)
        self.mainLayout.addWidget(self.__button_SetCurveToRender)
             
        # Connect event


    def valueChangedSlide(self, value):        
        self.__lineEdit.setText("{:.2f}".format(value))
        self.updateAttr("aiCurveWidth", value)
                    
    def valueChangedLine(self):
        value = self.__lineEdit.text()
        self.__slider.setValue(float(value))
        self.updateAttr("aiCurveWidth", value)
           
    def updateAttr(self, attr, value):
        sel= cmds.ls(sl=1)
        
        for crv in sel:
            shapes = cmds.listRelatives(crv, shapes=True, f=True)
            for shape in shapes:
                try:
                    cmds.setAttr(f"{shape}.{attr}", value)
                except Exception as e:
                    print(f"Error processing shape {shape}: {e}")
    
    def SetCurveToRender(self):  
        # Create all the lambert        
        # used a list to generate the dict
        color_index_to_lambert ={0: [0.4699999988079071, 0.4699999988079071, 0.4699999988079071], 1: [0.0, 0.0, 0.0], 2: [0.25, 0.25, 0.25], 3: [0.6000000238418579, 0.6000000238418579, 0.6000000238418579], 4: [0.6079999804496765, 0.0, 0.15700000524520874], 5: [0.0, 0.01600000075995922, 0.37599998712539673], 6: [0.0, 0.0, 1.0], 7: [0.0, 0.2750000059604645, 0.09799999743700027], 8: [0.14900000393390656, 0.0, 0.2630000114440918], 9: [0.7839999794960022, 0.0, 0.7839999794960022], 10: [0.5410000085830688, 0.28200000524520874, 0.20000000298023224], 11: [0.24699999392032623, 0.13699999451637268, 0.12200000137090683], 12: [0.6000000238418579, 0.14900000393390656, 0.0], 13: [1.0, 0.0, 0.0], 14: [0.0, 1.0, 0.0], 15: [0.0, 0.2549999952316284, 0.6000000238418579], 16: [1.0, 1.0, 1.0], 17: [1.0, 1.0, 0.0], 18: [0.3919999897480011, 0.8629999756813049, 1.0], 19: [0.2630000114440918, 1.0, 0.6389999985694885], 20: [1.0, 0.6899999976158142, 0.6899999976158142], 21: [0.8939999938011169, 0.675000011920929, 0.4749999940395355], 22: [1.0, 1.0, 0.3880000114440918], 23: [0.0, 0.6000000238418579, 0.32899999618530273], 24: [0.8549000024795532, 0.5686299800872803, 0.4274500012397766], 25: [0.8784300088882446, 0.784309983253479, 0.30588001012802124], 26: [0.6352900266647339, 0.8117600083351135, 0.2784300148487091], 27: [0.2313700020313263, 0.7568600177764893, 0.5803899765014648], 28: [0.2549000084400177, 0.8196099996566772, 0.7254899740219116], 29: [0.22744999825954437, 0.6156899929046631, 0.8078399896621704]}
        for index in color_index_to_lambert:
            shd_name = f"surface_utility{index}"
            
            if not cmds.objExists(shd_name):
                lamb = cmds.createNode('surfaceShader', name = shd_name)
                cmds.setAttr( lamb +'.outColor', color_index_to_lambert[index][0], color_index_to_lambert[index][1], color_index_to_lambert[index][2], type="double3")

        # Run ton script
        sel= cmds.ls(sl=1)
        
        for crv in sel:
            shapes = cmds.listRelatives(crv, shapes=True, f=True)
            for shape in shapes:
                try:
                    # get color
                    # check Shape or Transform 
                    if cmds.getAttr(f"{shape}.overrideEnabled") == 1: 
                        color_index = cmds.getAttr(f"{shape}.overrideColor")
                    else:
                        color_index = cmds.getAttr(f"{crv}.overrideColor")
                    cmds.setAttr(f"{shape}.aiRenderCurve", 1)
                    cmds.setAttr(f"{shape}.aiCurveWidth", CurveWidth)
                    cmds.setAttr(f"{shape}.aiSelfShadows", 0)
                    cmds.setAttr(f"{shape}.castsShadows", 0)
                    cmds.setAttr(f"{shape}.aiVisibleInSpecularReflection", 0)
                    cmds.setAttr(f"{shape}.aiVisibleInDiffuseReflection", 0)
                    cmds.connectAttr( f"surface_utility{color_index}.outColor", f"{shape}.aiCurveShader", f=True )
                    
                except Exception as e:
                    print(f"Error processing shape {shape}: {e}")
            
    

if __name__ == "__main__":
    try:
        ui.deleteLater()
    except:
        pass
    ui = MyWidget()

    try:
        ui.show()
    except:
        ui.deleteLater()
