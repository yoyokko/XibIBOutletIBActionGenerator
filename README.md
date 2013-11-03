# XibOutletActionGenerator
  XOAG is a python script to generate IBOutlet and IBAction for u.
  
  .xib, .h, .m files will be modified to generate properties, ibactions and connection with .h and .xib file.

## Usage:
  python generator.py [-a -c] xibfile
  
  -a: arc enabled, if not specified, disable.
  
  -c: make a copy of .xib .h .m file when saving, if not specified, overwrite the original file.

## Limitations:
  IBAction current only support one argument selector like `- (IBAction) buttonAction:(id) sender;`

## Xcode:
  Just create the UIViewController subclass with xib file.
  
  Drag n drop views on your xib and fill the xcode user label with property name and action name. Then run the script in terminal. There u go.

  Fill in the property name and action name in XcodeSpecificLabel field in xcode xib editor with this kind of format `buttonName;@sel(buttonAction:)`, `labelName` or `@sel(buttonAction)`.
  
  ![image](example.png)
