import sys
from PySide6.QtCore import * 
from PySide6.QtGui import *
from PySide6.QtUiTools import *
from PySide6.QtWidgets import *
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
from pxr import Usd, UsdGeom, Gf, UsdShade, Sdf
from PySide6.QtCore import QSettings
from abc import ABC, abstractmethod

my_script_dir = "/Users/natashadaas/USD_Switchboard/src" 
if my_script_dir not in sys.path:
    sys.path.append(my_script_dir)

from VariantAuthoringTool import VariantAuthoringTool

# ------------------------------------------------------------------------------------------

class GeoVariantAuthor(VariantAuthoringTool):

    def __init__(self, _tool_name):
        super().__init__(_tool_name)

        self.usd_filepath_dict = {} # stores [row, filepath]

        # icon paths
        self.pin_icon = Path(__file__).parent / "icons" / "pin.png"
        self.pinned_icon  = Path(__file__).parent / "icons" / "pin-confirmed.png"

    # UI FUNCTIONS -------------------------------------------------------------------------

    def apply(self, ui):
        variant_set_name = ui.vs_name_input.text()
        vset = self.createVariantSet(variant_set_name)
        
        self.createVariantsForSet(ui, vset)
        ui.close()

    def setupUserInterface(self, ui):
        super().setupUserInterface(ui)

        """
        # Check if the targetPrim already has a variant of this type (usd_file)
        exists, existing_vsets = self.find_authoring_variant_sets("material")
        remove_widget = ui.findChild(QPushButton, "vs_remove")
        if exists:
            self.creatingNewVariant = False
            self.handle_vs_selection_change(ui, existing_vsets[0].GetName())
            if (remove_widget):
                remove_widget.show() 
        else:
            remove_widget.hide() 
        """

        ui.final_button.setText("Create Variants")
        ui.final_button.clicked.connect(partial(self.apply, ui))
        

    def add_variant_row(self, ui):
        # Create widgets
        label = QLabel(f"Variant: ")
        variant_name_line_edit = QLineEdit()

        # Get new row index
        rowIndex = ui.gridLayout.rowCount()

        if (rowIndex == 1):
            variant_name_line_edit.setText("Default")

        # Setting object names
        variant_name_line_edit.setObjectName(f"variant_input_{rowIndex}")

        # Add to the grid layout in new row
        ui.gridLayout.addWidget(label, rowIndex, 0)
        ui.gridLayout.addWidget(variant_name_line_edit, rowIndex, 1)    

    # VARIANT AUTHORING SPECIFIC FUNCTIONS -------------------------------------------------------

    def createVariantsForSet(self, ui, vset):
        # Iterate through all num_variants
        # num_variants = ui.gridLayout.rowCount() - 1
        for i in range(1, ui.gridLayout.rowCount()):
            v_name_input_widget = ui.findChild(QLineEdit, f"variant_input_{i}")

            # Only make variants for NEW variants (ones that do not have object name pattern of variant_input_x)
            # This works because when populating existing variants, I didn't give it object names
            if v_name_input_widget:
                v_name_input = v_name_input_widget.text().strip() # strip white spaces just in case
                file_selected = self.usd_filepath_dict[i]
                self.createVariant(vset, v_name_input, file_selected)

        # set default variant as the first variant, only if the variant set is new
        if self.creatingNewVariant:
            v_name_input_widget_1 = ui.findChild(QLineEdit, f"variant_input_1")
            v_name_input_1 = v_name_input_widget_1.text().strip() 
            vset.SetVariantSelection(v_name_input_1)

    #TODO: warning if file has not been selected
    #TODO: There should be error checking for if the variant_name already exists for the vset
    def createVariant(self, vset, variant_name, file_selected):
        vset.AddVariant(variant_name)

        vset.SetVariantSelection(variant_name)

        # Go inside the variant and add the file reference
        with vset.GetVariantEditContext():
            self.targetPrim.GetReferences().AddReference(file_selected)
            attr = self.targetPrim.CreateAttribute("variant_set_pipeline_tag", Sdf.ValueTypeNames.String)
            attr.Set("usd_file")
        
        print(f"Variant '{variant_name}' authored with reference to: {file_selected}")

