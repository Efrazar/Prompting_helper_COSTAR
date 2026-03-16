; Prompting Helper Installer Script
; Created with NSIS

;--------------------------------
; Includes

!include "MUI2.nsh"
!include "FileFunc.nsh"

;--------------------------------
; General Configuration

; Name and file
Name "Prompting Helper"
OutFile "PromptingHelper-Setup-1.0.0.exe"

; Default installation folder
InstallDir "$PROGRAMFILES\PromptingHelper"

; Get installation folder from registry if available
InstallDirRegKey HKCU "Software\PromptingHelper" ""

; Request application privileges
RequestExecutionLevel admin

;--------------------------------
; Interface Settings

!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

;--------------------------------
; Pages

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
; Languages

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer Sections

Section "Install"
  
  SetOutPath "$INSTDIR"
  
  ; Put files there
  File /r "dist\PromptingHelper\*.*"
  
  ; Store installation folder
  WriteRegStr HKCU "Software\PromptingHelper" "" $INSTDIR
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Create Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\Prompting Helper"
  CreateShortcut "$SMPROGRAMS\Prompting Helper\Prompting Helper.lnk" "$INSTDIR\PromptingHelper.exe"
  CreateShortcut "$SMPROGRAMS\Prompting Helper\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
  ; Create Desktop shortcut (optional)
  CreateShortcut "$DESKTOP\Prompting Helper.lnk" "$INSTDIR\PromptingHelper.exe"
  
  ; Add to Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PromptingHelper" \
                   "DisplayName" "Prompting Helper"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PromptingHelper" \
                   "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PromptingHelper" \
                   "DisplayIcon" "$INSTDIR\PromptingHelper.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PromptingHelper" \
                   "Publisher" "Your Name"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PromptingHelper" \
                   "DisplayVersion" "1.0.0"
  
SectionEnd

;--------------------------------
; Uninstaller Section

Section "Uninstall"
  
  ; Remove files
  Delete "$INSTDIR\*.*"
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\Prompting Helper\*.*"
  RMDir "$SMPROGRAMS\Prompting Helper"
  Delete "$DESKTOP\Prompting Helper.lnk"
  
  ; Remove registry keys
  DeleteRegKey HKCU "Software\PromptingHelper"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PromptingHelper"
  
SectionEnd

