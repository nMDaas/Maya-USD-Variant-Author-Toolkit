import sys
from PySide6 import QtCore
from PySide6.QtCore import * 
from PySide6.QtGui import *
from PySide6.QtUiTools import *
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QPushButton, QMessageBox, QApplication
from functools import partial
import maya.cmds as cmds
from maya import OpenMayaUI
from pathlib import Path
from shiboken6 import wrapInstance
from functools import wraps
import math
import os
import ufe
import mayaUsd.ufe
from pxr import Usd, UsdGeom, Sdf, Gf
from PySide6.QtCore import QSettings
from abc import ABC, abstractmethod
from usd_utils import get_selected_usd_xform_prim
from errorDialog_exec_tool import errorDialog_exec_tool

from VariantAuthoringTool import VariantAuthoringTool

# ------------------------------------------------------------------------------------------

class TransformVariantAuthor(VariantAuthoringTool):

    def __init__(self, _tool_name):
        super().__init__(_tool_name)

        self.targetPrim = get_selected_usd_xform_prim() # set targetPrim - the XForm that will have the variant

        # icon paths
        self.trans_unset_icon = Path(__file__).parent / "icons" / "trans_unset.png"
        self.trans_set_icon  = Path(__file__).parent / "icons" / "trans_set.png"

    # UI FUNCTIONS -------------------------------------------------------------------------

    def close(self, ui):
        ui.close()

    def setupUserInterface(self, ui):
        successful = super().setupUserInterface(ui)

        if self.targetPrim is None:
            errorTitle = "Error: No Target Xform Prim Selected"
            errorMessage = """
            A target prim of type Xform must be selected to create a variant set.
            """
            errorDialog_exec_tool(errorTitle, errorMessage)
            return False
        
        ui.targetPrim.setText(f"Target Prim: {self.getTargetPrimPath()}")

        #connect buttons to functions
        ui.addVariantButton.clicked.connect(partial(self.add_variant_row, ui))

        if successful is False:
            return False
        else:
            # add radio buttons
            exists, existing_vsets = self.find_authoring_variant_sets("transform")
            newVariantOptionButton = QRadioButton("Create New Variant")
            newVariantOptionButton.setObjectName("radio_create_new_variant")
            ui.gridLayout_vs_options.addWidget(newVariantOptionButton, 0, 0)
            newVariantOptionButton.setEnabled(True)
            newVariantOptionButton.setChecked(True)
            newVariantOptionButton.clicked.connect(partial(self.setupUserInterface_NewVariant, ui))
            if exists: # only if existing variant sets of type "transform" on targetPrim
                existingVariantOptionButton = QRadioButton("Edit Existing Variant")
                existingVariantOptionButton.setObjectName("radio_edit_variant")
                ui.gridLayout_vs_options.addWidget(existingVariantOptionButton, 0, 1)  
                existingVariantOptionButton.setEnabled(True)
                existingVariantOptionButton.clicked.connect(partial(self.setupUserInterface_ExistingVariant, ui))
        
            remove_widget = ui.findChild(QPushButton, "vs_remove")
            if (remove_widget):
                remove_widget.hide() 

            ui.final_button.setText("Close")
            ui.final_button.clicked.connect(partial(self.close, ui))

            return True
        
    def manage_delete_variant_set(self, ui):
        self.resetUI(ui)
        exists, existing_vsets = self.find_authoring_variant_sets("transform")
        radio_create_new_variant_button = ui.findChild(QRadioButton, "radio_create_new_variant")
        radio__edit_variant_button = ui.findChild(QRadioButton, "radio_edit_variant")
        if not exists:
            radio_create_new_variant_button.setEnabled(True)
            radio_create_new_variant_button.setChecked(True)
            self.setupUserInterface_NewVariant(ui)
            widget = ui.findChild(QComboBox, "vs_name_dropdown")
            radio__edit_variant_button.hide() 
            widget.hide() 
            ui.vs_remove.hide()
        else:
            self.setupUserInterface_ExistingVariant(ui)

    def setupUserInterface_ExistingVariant(self, ui):
        # Check if the targetPrim already has a variant of this type (transform)
        exists, existing_vsets = self.find_authoring_variant_sets("transform")
        if exists:
            self.creatingNewVariant = False
            self.populateExistingVariantSetInUI(ui, existing_vsets)

        remove_widget = ui.findChild(QPushButton, "vs_remove")
        if (remove_widget):
            remove_widget.show() 

    def setupUserInterface_NewVariant(self, ui):
        self.resetUI(ui)
        widget = ui.findChild(QComboBox, "vs_name_dropdown")
        widget.hide() 

        remove_widget = ui.findChild(QPushButton, "vs_remove")
        if (remove_widget):
            remove_widget.hide() 

    def add_variant_row(self, ui):
        # Create widgets
        label = QLabel(f"Variant: ")
        variant_name_line_edit = QLineEdit()
        setButton = QPushButton()

        # Setting setButton settings
        setButton.setIcon(QIcon(str(self.trans_unset_icon)))
        setButton.setFlat(True)
        setButton.setToolTip("Set Xform For Transform Variant")
        setButton.setCursor(Qt.PointingHandCursor)
        setButton.setIconSize(QSize(self.width*0.02, self.height*0.02))

        # Get new row index
        rowIndex = ui.gridLayout.rowCount()

        if (rowIndex == 1):
            variant_name_line_edit.setText("Default")

        # Setting object names
        variant_name_line_edit.setObjectName(f"variant_input_{rowIndex}")
        setButton.setObjectName(f"set_button_{rowIndex}")

        # Add to the grid layout in new row
        ui.gridLayout.addWidget(label, rowIndex, 0)
        ui.gridLayout.addWidget(variant_name_line_edit, rowIndex, 1)    
        ui.gridLayout.addWidget(setButton, rowIndex, 2)   

        setButton.clicked.connect(lambda checked=False, r=rowIndex: self.setTransformVariant(ui, r))

    def resetUI(self, ui):
        ui.vs_name_input.setReadOnly(False)
        ui.vs_name_input.setText("")
        for i in reversed(range(1, ui.gridLayout.count())):
            item = ui.gridLayout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()

    # VARIANT AUTHORING SPECIFIC FUNCTIONS -------------------------------------------------------

    def show_confirmation(self, title, message):
        # Create the message box
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        # Define the standard buttons
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)

        # Execute and catch the result
        response = msg_box.exec()

        if response == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False
        
    # Check if self.targetPrim has any transformations
    def has_transform_deltas(self):
        xformable = UsdGeom.Xformable(self.targetPrim)
        ordered_ops = xformable.GetOrderedXformOps()
        
        for op in ordered_ops:
            val = op.Get()
            op_type = op.GetOpType()

            # Check if val has been set (translate/rotate/scale)
            if val is not None:
                # Get the constructor for the specific type (e.g., Gf.Vec3f, Gf.Vec3d)
                # to ensure IsClose compares identical C++ types.
                val_type = type(val)

                # Check for Translation/Rotation/Scale deviations
                if op_type == UsdGeom.XformOp.TypeTranslate:
                    # Checks if val is close to (0,0,0) with tolerance of 1e-6
                    if not Gf.IsClose(val, val_type(0), 1e-6): return True

                elif op_type == UsdGeom.XformOp.TypeScale:
                    # Checks if val is close to (1, 1, 1) with tolerance of 1e-6
                    if not Gf.IsClose(val, val_type(1), 1e-6): return True

                elif "Rotate" in str(op_type): # since there are many rotates (eg. RotateXYZ, RotateX, RotateZYX)
                    # val * 0 creates the "zero version" of whatever type val is (identity rotation)
                    # Checks if val is close to identity rotation with tolerance of 1e-6
                    if not Gf.IsClose(val, val * 0, 1e-6): return True

                elif op_type == UsdGeom.XformOp.TypeTransform: # in case prim is using a combined matrix
                    # val_type(1) for a GfMatrix results in an Identity Matrix
                    # Checks if val is close to identity matrix with tolerance of 1e-6
                    if not Gf.IsClose(val, val_type(1), 1e-6): return True
                
        return False

    # set XForm transform as variant for that row - linked to row number
    def setTransformVariant(self, ui, row_number):
        result = True # default

        # If self.targetPrim has no transformations, get confirmation from the user
        if not self.has_transform_deltas():
            result = self.show_confirmation("Confirmation Window", f"There are no transformations on {self.getTargetPrimPath()}.\n\nTransformation may have been accidentally applied to the wrong Xform/prim. Do you still want to proceed?")

        # If result is still True, continue
        if result == True:
            # create set
            ret, vset = self.createVariantSet(ui)

            if ret is True:
                # create transformation variant for set
                v_name_input_widget = ui.findChild(QLineEdit, f"variant_input_{row_number}")
                v_name_input = v_name_input_widget.text().strip()

                if (not v_name_input):
                    ui.error_label.setText(f"Variant name not set")
                    ui.error_label.show()
                    return False
                
                self.createATransformationVariantSet(self.targetPrim, vset, v_name_input)

                self.apply_permanent_order()
                self.apply_pipeline_tag(ui, "transform")

                # if successful, change pinned icon
                set_button = ui.findChild(QPushButton, f"set_button_{row_number}")
                set_button.setIcon(QIcon(str(self.trans_set_icon)))
                set_button.setToolTip("Xform Transform Applied To Variant")
                #set_button.setEnabled(False)
                set_button.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

                # set as read only
                v_name_input_widget.setReadOnly(True)

                ui.error_label.hide()
                return True
            else:
                return False

    def createATransformationVariantSet(self, targetPrim, vset, variant_name):
        # Get the manual overrides currently on the prim
        recorded_values = {}
        attrs_to_clear = []
        
        for attr in targetPrim.GetAttributes():
            if attr.IsAuthored() and attr.Get() is not None:
                attr_name = attr.GetName()
                recorded_values[attr_name] = attr.Get()
                attrs_to_clear.append(attr)

        # Create/select the new variant and author the values
        vset.AddVariant(variant_name)
        vset.SetVariantSelection(variant_name)

        with vset.GetVariantEditContext():
            for attr_name, val in recorded_values.items():            
                attr = targetPrim.GetAttribute(attr_name)
                if (attr):
                    attr.Set(val)
        # Clear the top-level overrides so the variant can take over
        for attr in attrs_to_clear:
            attr.Clear()

        vset.SetVariantSelection("") 
            
        print(f"Recorded variant '{variant_name}' and cleared top-level overrides.")

    def apply_permanent_order(self):
        attr = self.targetPrim.GetAttribute("xformOpOrder")
        if attr.HasValue():
            print(f"Prim already has attribute")
            return
        
        else:
            stage = self.targetPrim.GetStage()
            
            target_layer = stage.GetRootLayer()

            with Usd.EditContext(stage, target_layer):
                xformable = UsdGeom.Xformable(self.targetPrim)

                tOp = xformable.AddTranslateOp()
                rOp = xformable.AddRotateXYZOp()
                sOp = xformable.AddScaleOp()

                xformable.SetXformOpOrder([tOp, rOp, sOp])
                
            print(f"Authored xformOpOrder to layer: {target_layer.identifier}")   
            

    

