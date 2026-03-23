## USD Variant Authoring Tools for Maya
In progress!

### Variant Authoring Management Tools
<table>
  <tr valign="middle">
    <td>
      <img src="https://github.com/nMDaas/USD_Switchboard/blob/main/icons/ModelVariant_AIcon.png" width="50px">
    </td>
    <td>
      Modeling Variant Manager
    </td>
  </tr>
  <tr valign="middle">
    <td>
      <img src="https://github.com/nMDaas/USD_Switchboard/blob/main/icons/TransformVariant_AIcon.png" width="50px">
    </td>
    <td>
      Transform Variant Manager
    </td>
  </tr>
  <tr valign="middle">
    <td>
      <img src="https://github.com/nMDaas/USD_Switchboard/blob/main/icons/MaterialVariant_AIcon.png" width="50px">
    </td>
    <td>
      Material Variant Manager
    </td>
  </tr>
</table>

### Installation
1. Download and unzip this repository in a location of your choosing
2. Rename the unzipped folder to Maya-USD-Variant-Author-Toolkit
3. With Maya opened, open the Script Editor
4. Click on 'File', and from the dropdown list, select 'Open Script'
5. With the Load Script dialog opened, locate the Maya-USD-Variant-Author-Toolkit folder
6. Click into the folder, and then select the install.py file
7. Click 'Open' - the install.py script will be loaded into the Script Editor
8. Click the blue run button (▶) at the top of the Script Editor to run the script
9. Once again, locate and select the Maya-USD-Variant-Author-Toolkit folder
10. Click 'Save' - Maya_USD_Variant_Author_Toolkit should be loaded into a shelf

### Documentation
[HELP | Maya-USD-Variant-Author-Toolkit](https://docs.google.com/document/d/1ipKrDLCjgtbGJnS1Inhu1NR4tvY33CLJlLu5xJTuQ54/edit?usp=sharing)

### Tutorial Using Toaster Project
Using the test project, these instructions walk through how to use this toolkit step-by-step:
- [TUTORIAL (beginner) | Maya USD Variant Author Toolkit](https://docs.google.com/document/d/1s75NcT0jil2NYX_dR0RY3g7EMvloyraf9dzsZMUVQ-M/edit?usp=sharing)

### Troubleshooting
<table>
  <tr valign="middle">
    <td>
      🛠️ TOOL(S)
    </td>
    <td>
      🐛 ISSUE 
    </td>
    <td>
      ✅ FIX 
    </td>
  </tr>
  <tr valign="middle">
    <td>
      <img src="https://github.com/nMDaas/USD_Switchboard/blob/main/icons/TransformVariant_AIcon.png" width="50px">
    </td>
    <td>
     Unexpected transform applied when variant created on prim with USD reference
    </td>
    <td>
      <ul>
        <li>Referenced USD asset should be exported from (0,0,0) with transforms frozen and history deleted </li> 
      </ul>
    </td>
  </tr>
  <tr valign="middle">
    <td>
      <img src="https://github.com/nMDaas/USD_Switchboard/blob/main/icons/MaterialVariant_AIcon.png" width="50px">
    </td>
    <td>
      Prim material not applied/changing after creating/toggling variants
    </td>
    <td>
      <ul>
        <li>In LookdevX, ensure that the image nodes for each material in the variant set are pointing to the right path in sourceimages/</li> 
        <li>With the prim selected, set 'Strength' in the attribute editor to 'Stronger than descendants'</li>
      </ul>
    </td>
  </tr>
</table>

### Credits
- Folder icons created by kmg design - Flaticon
- Files and folders icons created by Gajah Mada - Flaticon
- Dirrection icons created by popcic - Flaticon
- Warning icons created by Rakib Hassan Rahim - Flaticon
