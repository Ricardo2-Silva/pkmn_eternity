# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\gui\styleDB.py
from .style import *
from client.data.gui.button import ButtonData
from client.data.utils.utils import DynamicObject
from client.data.skins import skinDB
from client.render.cache import textureCache
transparentTexture = textureCache.getBackgroundColor(Color.TRANSPARENT)
blackTexture = textureCache.getBackgroundColor(Color.BLACK)
windowBackground = BackgroundData(skinDB.getWindowColor())
transparentBackground = BackgroundData(Color.TRANSPARENT)
darkGreyBackground = BackgroundData(Color.DARK_GREY)
blackBackground = BackgroundData((Color.BLACK), alpha=100)
greyBackground = BackgroundData(Color.GREY)
whiteBackground = BackgroundData(Color.WHITE)
redBackground = BackgroundData(Color.RED)
roseBackground = BackgroundData(Color.ROSE)
blueBackground = BackgroundData(Color.BLUE)
titleBackground = BackgroundData((Color.BLACK), alpha=30)
titleBackgroundFocus = BackgroundData((Color.RED), alpha=30)
announceBackground = BackgroundData((Color.BLACK), alpha=100, anchor=(AnchorType.CENTER))
defaultPadding = PaddingData(0, 0, 0, 0)
defaultButtonPadding = PaddingData(0, 0, 7, 7)
smallPadding = PaddingData(2, 2, 2, 2)
defaultWindowPadding = PaddingData(6, 6, 6, 6)
noMargins = PaddingData(0, 0, 0, 0)
windowMargins = PaddingData(9, 9, 12, 12)
lineBorder = BorderData(color=(Color.BLACK), top=False, right=False, left=False, alpha=30)
shadowBackground = BackgroundData(color=None, image=textureCache.getBorderGUI("common/shadow", stretch=(PaddingData(10, 10, 10, 10))),
  patchType=(PatchType.NINE))
shadowColorBackground = BackgroundData(color=None, image=textureCache.getBorderGUI("common/shadowcolor", stretch=(PaddingData(10, 10, 10, 10))),
  patchType=(PatchType.NINE))
lineRoundedBackground = BackgroundData(color=None, image=(textureCache.getBorderGUI("common/linerounded")),
  patchType=(PatchType.NINE))
lineFullRoundedBackground = BackgroundData(color=None, image=(textureCache.getBorderGUI("common/linefullrounded")),
  patchType=(PatchType.NINE))
primaryShadow = ShadowData(skinDB.getPrimaryShadow(), ShadowType.MIN)
secondaryShadow = ShadowData(skinDB.getSecondaryShadow(), ShadowType.MIN)
whiteMinShadow = ShadowData(Color.WHITE, ShadowType.MIN)
whiteFullShadow = ShadowData(Color.WHITE, ShadowType.FULL)
blackMinShadow = ShadowData(Color.BLACK, ShadowType.MIN)
blackFullShadow = ShadowData(Color.BLACK, ShadowType.MIN)
primarySimpleText = TextData(color=(skinDB.getPrimaryColor()))
secondarySimpleText = TextData(color=(skinDB.getSecondaryColor()))
primaryTextShadow = TextData(color=(skinDB.getSecondaryColor()), shadow=primaryShadow)
secondaryTextShadow = TextData(color=(skinDB.getSecondaryColor()), shadow=secondaryShadow)
whiteSimpleText = TextData(color=(Color.WHITE))
blackSimpleText = TextData(color=(Color.BLACK))
whiteTextShadow = TextData(color=(Color.WHITE), shadow=blackMinShadow)
blackTextShadow = TextData(color=(Color.BLACK), shadow=whiteMinShadow)
redTextShadow = TextData(color=(Color.RED), shadow=blackMinShadow)
cursorText = TextData(color=(Color.WHITE_BLUE), shadow=blackFullShadow)
femaleText = TextData(color=(200, 92, 84), shadow=(ShadowData((200, 160, 156), ShadowType.MIN)))
maleText = TextData(color=(72, 136, 188), shadow=(ShadowData((139, 159, 204), ShadowType.MIN)))
whiteBoldTextFullShadow = TextData(color=(Color.WHITE), shadow=blackFullShadow)
goldText = TextData(color=(255, 215, 0), shadow=blackMinShadow)
announceText = TextData(color=(255, 215, 0), shadow=blackMinShadow, font=(fontDB.getFont("mediumbig")))
shadowWidgetStyle = Style(shadowBackground, padding=(PaddingData(10, 10, 10, 10)))
lineRoundedStyle = Style(lineRoundedBackground, padding=(PaddingData(5, 5, 5, 5)))
shadowColorWidgetStyle = Style(shadowColorBackground, padding=(PaddingData(10, 10, 10, 10)))
lineFullRoundedStyle = Style(background=None, border=BorderData(images=textureCache.getBorderGUI("common/linefullrounded", stretch=(PaddingData(5, 5, 5, 5)))),
  padding=(PaddingData(8, 5, 5, 5)))
windowsNoStyle = Style(None)
windowsNoStylePadded = Style(None, padding=defaultWindowPadding)
windowsDefaultStyle = Style(windowBackground, (skinDB.getWindowBorder()),
  padding=defaultWindowPadding,
  margins=windowMargins)
windowsDefaultStyleNoPadding = Style(windowBackground, (skinDB.getWindowBorder()),
  margins=windowMargins)
windowsDefaultStyleNoPadding = Style(windowBackground, (skinDB.getWindowBorder()),
  margins=windowMargins)
windowsDefaultStyleSmallPadding = Style(windowBackground, (skinDB.getWindowBorder()),
  padding=smallPadding,
  margins=windowMargins)
windowNoBgStyle = Style(background=None, border=(skinDB.getWindowBorder()),
  margins=windowMargins)
notificationWindow = Style(None, padding=(PaddingData(100, 0, 0, 0)))
hotbarWindow = Style(border=(skinDB.getWindowBorder()), background=BackgroundData(color=None, image=(textureCache.getGuiImage("common/hotbar"))),
  text=whiteTextShadow,
  margins=(PaddingData(5, 5, 0, 0)))
timeWindowStyle = Style(None, padding=(PaddingData(2, 0, -2, 0)))
questDetailsStyle = Style(border=BorderData(textureCache.getBorderFromImage("questlog/quest_details", (textureCache.getGuiImage("questlog/quest_details")),
  stretch=(PaddingData(5, 9, 5, 5))),
  padding=windowMargins))
pokedexLabelStyle = Style(background=None, text=TextData(color=(96, 96, 96), anchor=(AnchorType.RIGHT),
  shadow=(ShadowData((208, 208, 208), ShadowType.MIN))))
pokedexDescriptionLabelStyle = Style(background=None, text=TextData(color=(96, 96,
                                                                           96), anchor=(AnchorType.LEFT),
  shadow=(ShadowData((208, 208, 208), ShadowType.MIN))))
summaryLabelStyle = Style(background=None, text=TextData(font=(fontDB.getFont("summary")), color=(65,
                                                                                                  65,
                                                                                                  65),
  shadow=(ShadowData((172, 172, 172), ShadowType.MIN))))
chatLabelStyle = Style(background=None, text=TextData(font=(fontDB.getFont("chat")), color=(Color.BLACK),
  anchor=(AnchorType.LEFT)))
trainerCardLabelStyle = Style(background=None, text=TextData(color=(151, 151, 151), shadow=blackMinShadow))
blackCheckboxStyle = Style(background=None, text=TextData(color=(skinDB.getPrimaryColor()), anchor=(AnchorType.LEFTCENTER)),
  padding=(PaddingData(0, 0, 20, 0)))
itemStyle = Style(background=None, text=TextData(color=(Color.BLACK), shadow=whiteMinShadow,
  anchor=(AnchorType.BOTTOMRIGHT)),
  padding=smallPadding)
npcLabelStyle = Style(background=None, text=TextData(font=(fontDB.getFont("npc")), color=(Color.BLACK),
  anchor=(AnchorType.LEFT)))
journalTitleLabel = Style(background=None, text=TextData(font=(fontDB.getFont("mediumbig")), color=(Color.BLACK),
  anchor=(AnchorType.LEFT)))
whiteShadowLabelStyle = Style(background=None, text=whiteBoldTextFullShadow)
titleLabelStyle = Style(background=titleBackground, text=TextData(color=(skinDB.getPrimaryColor()), shadow=primaryShadow),
  padding=(PaddingData(0, 0, 3, 3)))
titleLabelFocusStyle = Style(background=titleBackgroundFocus, text=TextData(color=(skinDB.getPrimaryColor()), shadow=primaryShadow),
  padding=(PaddingData(0, 0, 3, 3)))
whiteLabelStyle = Style(background=None, text=whiteTextShadow,
  padding=defaultButtonPadding)
bgLabelStyle = Style(background=redBackground, text=whiteTextShadow,
  padding=defaultButtonPadding)
shopMoneyLabelStyle = Style(background=None, text=TextData(color=(Color.WHITE), shadow=blackMinShadow, anchor=(AnchorType.RIGHT)),
  padding=defaultButtonPadding)
hotbarLabelStyle = Style(background=None, text=TextData(color=(Color.WHITE), anchor=(AnchorType.TOPRIGHT),
  shadow=blackMinShadow))
buffLabelStyle = Style(background=None, text=whiteBoldTextFullShadow)
textboxLabelStyle = Style(background=None, text=TextData(color=(Color.WHITE), shadow=blackMinShadow,
  anchor=(AnchorType.LEFTCENTER)),
  padding=defaultButtonPadding)
errorNotificationLabelStyle = Style(background=None, text=redTextShadow,
  padding=smallPadding)
announceNotificationLabel = Style(background=announceBackground, text=announceText,
  padding=(PaddingData(0, 0, 0, 0)))
whiteNoPaddingStyle = Style(background=None, text=whiteTextShadow,
  padding=defaultPadding)
blackLabelStyle = Style(background=None, text=TextData(color=(Color.BLACK), anchor=(AnchorType.LEFT)))
blackLabelStyleRight = Style(background=None, text=TextData(color=(Color.BLACK), anchor=(AnchorType.RIGHT)))
noPaddingStyle = Style(background=None, text=blackSimpleText, padding=defaultPadding)
blackLabelPaddingStyle = Style(background=None, text=blackSimpleText, padding=(PaddingData(0, 4, 7, 7)))
pokemonWhiteGuiStyle = Style(background=None, text=TextData(color=(Color.WHITE), shadow=(ShadowData((104,
                                                                                                     104,
                                                                                                     104), ShadowType.MIN))),
  padding=defaultPadding)
redDetailsStyle = Style(background=None, text=femaleText)
blueDetailsStyle = Style(background=None, text=maleText)
leaderLabelStyle = Style(background=None, text=goldText)
nonLeaderLabelStyle = Style(background=None, text=TextData(color=(Color.BLACK), shadow=(ShadowData((225,
                                                                                                    225,
                                                                                                    225))), anchor=(AnchorType.LEFT)))
nameStyle = Style(background=None, text=TextData(color=(Color.WHITE), shadow=blackFullShadow))
chatMessageStyle = Style(background=BackgroundData((Color.BLACK), alpha=100), text=whiteSimpleText,
  padding=(PaddingData(4, 1, 4, 2)))
chatMessageWindowStyle = Style(background=BackgroundData(image=(textureCache.getBorderGUI("common/linerounded_white", PaddingData(8, 8, 8, 8))),
  patchType=(PatchType.NINE),
  alpha=100),
  text=whiteSimpleText,
  padding=(PaddingData(4, 4, 4, 4)))
skinDB.getWindowBorder()
defaultButtonStretch = PaddingData(5, 5, 8, 8)
simpleButtonStyle = ButtonStyle(noPaddingStyle)
transparentButtonStyle = ButtonStyle(noPaddingStyle)
transparentButtonStyleRight = ButtonStyle(Style(background=None, text=TextData(color=(Color.BLACK), anchor=(AnchorType.RIGHT)),
  padding=defaultPadding))
pokedexButtonStyle = ButtonStyle(Style(background=None, text=TextData(color=(96, 96,
                                                                             96), anchor=(AnchorType.TOPRIGHT),
  shadow=(ShadowData((208, 208, 208), ShadowType.MIN)))))
testButtonStyle = ButtonStyle(Style(background=blackBackground, text=blackSimpleText,
  padding=defaultPadding))
iconButtonStyle = ButtonStyle(whiteNoPaddingStyle)
buffIconStyle = ButtonStyle(Style(background=None, text=TextData(color=(Color.WHITE), shadow=(ShadowData(Color.BLACK, ShadowType.FULL)), anchor=(AnchorType.TOPRIGHT), bold=True),
  padding=defaultPadding))
closeButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.FOUR_IMAGE)
closeButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/close", PatchType.FOUR_IMAGE))
questButtonStyle = ButtonStyle(Style(background=None, text=blackSimpleText,
  padding=(PaddingData(0, 4, 7, 7))), PatchType.THREE)
questButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("questlog/button", PatchType.THREE, defaultButtonStretch))
maximizeButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.FOUR_IMAGE)
maximizeButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/maximize", PatchType.FOUR_IMAGE))
reduceButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.FOUR_IMAGE)
reduceButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/reduce", PatchType.FOUR_IMAGE))
blueButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.THREE)
blueButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/blueButton", PatchType.THREE, defaultButtonStretch))
dropdownButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.THREE)
dropdownButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/dropdown", PatchType.THREE, defaultButtonStretch))
whiteLineStyle = ButtonStyle(Style(background=transparentBackground, text=blackSimpleText,
  border=BorderData(color=(225, 225, 225), top=False, right=False, left=False, bottom=True)))
whiteLineStyle.setBackgroundColors(DynamicObject(normal=(Color.WHITE), over=(Color.WHITE_BLUE),
  down=(Color.WHITE_BLUE),
  disabled=(Color.WHITE)))
defaultTabStyle = ButtonStyle(whiteLabelStyle, PatchType.THREE)
defaultTabStyle.setBackgroundImage(skinDB.getTabImage())
redButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.THREE)
redButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/redButton", PatchType.THREE, defaultButtonStretch))
greenButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.THREE)
greenButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/greenButton", PatchType.THREE, defaultButtonStretch))
grayButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.THREE)
grayButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/grayButton", PatchType.THREE, defaultButtonStretch))
downArrowButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.FOUR_IMAGE)
downArrowButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/arrowDown", PatchType.FOUR_IMAGE))
upArrowButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.FOUR_IMAGE)
upArrowButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/arrowUp", PatchType.FOUR_IMAGE))
leftArrowButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.FOUR_IMAGE)
leftArrowButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/arrowLeft2", PatchType.FOUR_IMAGE))
rightArrowButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.FOUR_IMAGE)
rightArrowButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/arrowRight2", PatchType.FOUR_IMAGE))
roundButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.FOUR_IMAGE)
roundButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/roundButton", PatchType.FOUR_IMAGE))
scrollDownButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.FOUR_IMAGE)
scrollDownButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/scrollDown2", PatchType.FOUR_IMAGE))
scrollUpButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.FOUR_IMAGE)
scrollUpButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/scrollUp2", PatchType.FOUR_IMAGE))
checkboxButtonStyle = ButtonStyle(blackCheckboxStyle, PatchType.FOUR_IMAGE)
checkboxButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/checkbox", PatchType.FOUR_IMAGE))
loginCheckboxButtonStyle = ButtonStyle(Style(background=None, text=TextData(color=(Color.WHITE), anchor=(AnchorType.LEFTCENTER),
  shadow=ShadowData(color=(Color.BLACK))),
  padding=(PaddingData(0, 0, 20, 0))), PatchType.FOUR_IMAGE)
loginCheckboxButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/checkbox", PatchType.FOUR_IMAGE))
scrollBarButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.THREE_VERT)
scrollBarButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/scrollBar", PatchType.THREE_VERT, defaultButtonStretch))
defaultTextboxStyle = ButtonStyle(textboxLabelStyle, PatchType.THREE)
defaultTextboxStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/basicTextbox", PatchType.THREE, defaultButtonStretch))
loginTextBoxStyle = ButtonStyle(textboxLabelStyle, PatchType.THREE)
loginTextBoxStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/basicTextbox", PatchType.THREE, defaultButtonStretch))
itemButtonStyle = ButtonStyle(itemStyle, PatchType.THREE)
itemButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/itemButton", PatchType.THREE, defaultButtonStretch))
hotbarNormalButtonStyle = ButtonStyle(Style(background=None, text=TextData(color=(Color.BLACK), shadow=whiteMinShadow,
  anchor=(AnchorType.BOTTOMRIGHT)),
  padding=smallPadding))
hotbarSkillButtonStyle = ButtonStyle(Style(background=None, text=TextData(color=(Color.NAME_GREEN), anchor=(AnchorType.CENTER),
  shadow=whiteMinShadow),
  padding=smallPadding))
shopButtonStyle = ButtonStyle(Style(background=None, text=TextData(color=(Color.BLACK), shadow=whiteMinShadow,
  anchor=(AnchorType.TOPRIGHT)),
  padding=(PaddingData(3, 3, 3, 3))), PatchType.THREE)
shopButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/itemButton", PatchType.THREE, defaultButtonStretch))
graySkillButtonStyle = ButtonStyle(whiteNoPaddingStyle, PatchType.THREE)
graySkillButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/graySkillButton", PatchType.THREE, defaultButtonStretch))
cancelButtonStyle = ButtonStyle(whiteLabelStyle, PatchType.THREE)
cancelButtonStyle.setBackgroundImage(textureCache.getButtonBackgroundGUI("common/blueCancelButton", PatchType.THREE, PaddingData(5, 5, 5, 5)))
menuItemStyle = ButtonStyle(Style(background=transparentBackground, text=whiteTextShadow,
  padding=defaultPadding))
menuItemStyle.setBackgroundColors(DynamicObject(normal=(Color.TRANSPARENT), over=(Color.GREY),
  down=(Color.DARK_GREY),
  disabled=(Color.TRANSPARENT)))
menuItemStyle.setTextColors(ButtonData(blackTextShadow, whiteTextShadow, whiteTextShadow, blackTextShadow))
defaultBarStyle = BarStyle(backgroundColor=(200, 200, 200), borderImg=(textureCache.getBorderGUI("common/bar", PaddingData(1, 1, 1, 1))),
  secondary=False)
defaultBarStyle.setPrimaryColor(100, 99, 191, 0)
defaultBarStyle.setPrimaryColor(75, 252, 221, 3)
defaultBarStyle.setPrimaryColor(25, 229, 110, 0)
defaultBarStyle.setPrimaryColor(5, 189, 2, 21)
faintedBarStyle = BarStyle(backgroundColor=(139, 0, 0), borderImg=(textureCache.getBorderGUI("common/bar", PaddingData(1, 1, 1, 1))),
  secondary=False)
faintedBarStyle.setPrimaryColor(100, 99, 191, 0)
faintedBarStyle.setPrimaryColor(75, 252, 221, 3)
faintedBarStyle.setPrimaryColor(25, 229, 110, 0)
faintedBarStyle.setPrimaryColor(5, 189, 2, 21)
defaultBarWithHpColors = BarStyle(backgroundColor=(200, 200, 200), borderImg=(textureCache.getBorderGUI("common/bar", PaddingData(1, 1, 1, 1))),
  secondary=False)
defaultBarWithHpColors.setPrimaryColor(100, 35, 220, 35)
defaultBarWithHpColors.setPrimaryColor(50, 255, 225, 27)
defaultBarWithHpColors.setPrimaryColor(35, 255, 171, 64)
defaultBarWithHpColors.setPrimaryColor(15, 239, 49, 67)
hpBarStyle = BarStyle(patchType=(PatchType.NOPATCH), margins=(PaddingData(1, 1, 1, 1)))
hpBarStyle.setPrimaryColor(100, 35, 220, 35)
hpBarStyle.setSecondaryColor(100, 153, 248, 76)
hpBarStyle.setPrimaryColor(50, 255, 225, 27)
hpBarStyle.setSecondaryColor(50, 255, 255, 75)
hpBarStyle.setPrimaryColor(35, 255, 171, 64)
hpBarStyle.setSecondaryColor(35, 153, 248, 76)
hpBarStyle.setPrimaryColor(15, 239, 49, 67)
hpBarStyle.setSecondaryColor(15, 255, 92, 138)
xpBarStyle = BarStyle(borderImg=(textureCache.getBorderGUI("common/bar", PaddingData(1, 1, 1, 1))), secondary=False)
xpBarStyle.setPrimaryColor(100, 84, 164, 212)
xpBarStyle.setPrimaryColor(50, 84, 164, 212)
xpBarStyle.setPrimaryColor(25, 84, 164, 212)
xpBarStyle.setPrimaryColor(5, 84, 164, 212)
xpInfoBarStyle = BarStyle(patchType=(PatchType.NOPATCH))
xpInfoBarStyle.setPrimaryColor(100, 153, 102, 255)
xpInfoBarStyle.setSecondaryColor(100, 208, 190, 248)
sliderBarStyle = BarStyle(backgroundColor=(200, 200, 200), borderImg=(textureCache.getBorderGUI("common/bar", PaddingData(1, 1, 1, 1))),
  secondary=False)
sliderBarStyle.setPrimaryColor(100, 122, 146, 224)
sliderBarStyle.setPrimaryColor(50, 122, 146, 224)
sliderBarStyle.setPrimaryColor(25, 122, 146, 224)
sliderBarStyle.setPrimaryColor(5, 122, 146, 224)
energyBarStyle = BarStyle(patchType=(PatchType.NOPATCH))
energyBarStyle.setPrimaryColor(100, 35, 144, 220)
energyBarStyle.setSecondaryColor(100, 49, 186, 206)
castBarStyle = BarStyle(backgroundColor=(200, 200, 200), borderImg=(textureCache.getBorderGUI("common/bar", PaddingData(1, 1, 1, 1))),
  secondary=False)
castBarStyle.setPrimaryColor(100, 84, 164, 212)
castBarStyle.setPrimaryColor(50, 84, 164, 212)
castBarStyle.setPrimaryColor(25, 84, 164, 212)
castBarStyle.setPrimaryColor(5, 84, 164, 212)
defaultPictureStyle = PictureStyle()
pictureNoPaddingStyle = PictureStyle(margins=(0, 0, 0, 0))
chatColors = {
 'DEFAULT': (255, 255, 255), 
 'MOTD': (107, 252, 180), 
 'BATTLE': (204, 0, 0), 
 'SYSTEM': (107, 252, 180), 
 'SYSTEM_ERROR': (241, 86, 69), 
 'ITEM': (107, 252, 180), 
 'GUILD': (34, 177, 76), 
 'PARTY': (40, 158, 215), 
 'ANNOUNCE': (244, 182, 96), 
 'PM_FROM': (101, 20, 182), 
 'PM_TO': (101, 20, 182), 
 'LOCAL': (120, 232, 242), 
 'GLOBAL': (169, 204, 243), 
 'JOIN': (188, 250, 158), 
 'LEAVE': (248, 160, 160)}
chatStyles = {}
for name, color in chatColors.items():
    chatStyles[name] = Style(background=None, text=TextData(font=(fontDB.getFont("chat")), color=color,
      anchor=(AnchorType.LEFT)))
