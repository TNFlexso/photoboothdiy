#!/usr/bin/env python3
import pygame
import pygame.camera
import time
import os
import PIL.Image
import cups
import RPi.GPIO as GPIO
import subprocess

from threading import Thread
from pygame.locals import *
from time import sleep
from PIL import Image, ImageDraw
from subprocess import *

# initialise global variables
Numeral = ""  # Numeral is the number display
Message = ""  # Message is a fullscreen message
SubMessage = ""
LongMessage = ""
BackgroundColor = ""
CountDownPhoto = ""
CountPhotoOnCart = ""
SmallMessage = ""  # SmallMessage is a lower banner message
TotalImageCount = 0  # Counter for Display and to monitor paper usage
PhotosPerCart = 30  # Selphy takes 16 sheets per tray
imagecounter = 0
imagefolder = 'Photos'
templatePath = os.path.join('Photos', 'Template', "template.png") #Path of template image
ImageShowed = False
Printing = False
BUTTON_PIN = 25
IMAGE_WIDTH = 594
IMAGE_HEIGHT = 445
os.environ["SDL_AUDIODRIVER"] = "dsp"

# Load the background template
bgimage = PIL.Image.open(templatePath)

#Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# initialise pygame
pygame.init()  # Initialise pygame
pygame.font.init()
pygame.camera.init()
# pygame.mouse.set_visible(False) #hide the mouse cursor
infoObject = pygame.display.Info()
screen_size = (infoObject.current_w,infoObject.current_h)
screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)  # Full screen  , pygame.FULLSCREEN
background = pygame.Surface(screen_size)  # Create the background object
background = background.convert()  # Convert it to a background

screenPicture = pygame.display.set_mode(screen_size, pygame.RESIZABLE)  # Full screen
backgroundPicture = pygame.Surface(screen_size)  # Create the background object
backgroundPicture = background.convert()  # Convert it to a background

transform_x = infoObject.current_w # how wide to scale the jpg when replaying
transfrom_y = infoObject.current_h # how high to scale the jpg when replaying

# Initialise the camera object
# camera.resolution = (infoObject.current_w, infoObject.current_h)
camera_resolution = (infoObject.current_w, infoObject.current_h)
camera_devices = pygame.camera.list_cameras()
camera = pygame.camera.Camera(camera_devices[0],camera_resolution)
camera.set_controls(hflip = True, vflip = False, 50)
#camera.rotation              = 0
#camera.hflip                 = True
#camera.vflip                 = False
#camera.brightness            = 50
#camera.preview_alpha = 120
#camera.preview_fullscreen = True
#camera.framerate             = 24
#camera.sharpness             = 0
#camera.contrast              = 8
#camera.saturation            = 0
#camera.ISO                   = 0
#camera.video_stabilization   = False
#camera.exposure_compensation = 0
#camera.exposure_mode         = 'auto'
#camera.meter_mode            = 'average'
#camera.awb_mode              = 'auto'
#camera.image_effect          = 'none'
#camera.color_effects         = None
#camera.crop                  = (0.0, 0.0, 1.0, 1.0)


# A function to handle keyboard/mouse/device input events
def input(events):
    for event in events:  # Hit the ESC key to quit the slideshow.
        if (event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)):
            pygame.quit()

   
# set variables to properly display the image on screen at right ratio
def set_demensions(img_w, img_h):
    # Note this only works when in booting in desktop mode. 
    # When running in terminal, the size is not correct (it displays small). Why?

    # connect to global vars
    global transform_y, transform_x, offset_y, offset_x

    # based on output screen resolution, calculate how to display
    ratio_h = (infoObject.current_w * img_h) / img_w 

    if (ratio_h < infoObject.current_h):
        #Use horizontal black bars
        #print "horizontal black bars"
        transform_y = ratio_h
        transform_x = infoObject.current_w
        offset_y = (infoObject.current_h - ratio_h) / 2
        offset_x = 0
    elif (ratio_h > infoObject.current_h):
        #Use vertical black bars
        #print "vertical black bars"
        transform_x = (infoObject.current_h * img_w) / img_h
        transform_y = infoObject.current_h
        offset_x = (infoObject.current_w - transform_x) / 2
        offset_y = 0
    else:
        #No need for black bars as photo ratio equals screen ratio
        #print "no black bars"
        transform_x = infoObject.current_w
        transform_y = infoObject.current_h
        offset_y = offset_x = 0

def InitFolder():
    global imagefolder
    global Message
    global LongMessage
    global SubMessage
 
    Message = 'Folder Check...'
    UpdateDisplay()
    Message = ''

    #check image folder existing, create if not exists
    if not os.path.isdir(imagefolder): 
        os.makedirs(imagefolder) 
            
    imagefolder2 = os.path.join(imagefolder, 'images')
    if not os.path.isdir(imagefolder2):
        os.makedirs(imagefolder2)
    
def DisplayText(fontSize, textToDisplay):
    global Numeral
    global Message
    global LongMessage
    global SubMessage
    global screen
    global background
    global pygame
    global ImageShowed
    global screenPicture
    global backgroundPicture
    global CountDownPhoto

    if (BackgroundColor != ""):
        #print(BackgroundColor)
        background.fill(pygame.Color("black"))
    if (textToDisplay != ""):
        #print(displaytext)
        font = pygame.font.Font(None, fontSize)
        text = font.render(textToDisplay, 1, (227, 157, 200))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        if(ImageShowed):
            backgroundPicture.blit(text, textpos)
        else:
            background.blit(text, textpos)

def UpdateDisplay():
    # init global variables from main thread
    global Numeral
    global Message
    global SubMessage
    global LongMessage
    global screen
    global background
    global pygame
    global ImageShowed
    global screenPicture
    global backgroundPicture
    global CountDownPhoto
   
    background.fill(pygame.Color("white"))  # White background

    if (BackgroundColor != ""):
        background.fill(pygame.Color("black"))
        
    if (Message != ""):
        font = pygame.font.SysFont("Brandon Grotesque Bold", 100)
        text = font.render(Message, True, (0, 0, 0))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        if(ImageShowed):
            backgroundPicture.blit(text, textpos)
        else:
            background.blit(text, textpos)
            
    if(LongMessage != ""):
        font = pygame.font.SysFont("Brandon Grotesque Bold", 80)
        text = font.render(LongMessage, True, (0, 0, 0))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery - 40
        if(ImageShowed):
            backgroundPicture.blit(text, textpos)
        else:
            background.blit(text, textpos)
        font = pygame.font.SysFont("Brandon Grotesque Bold", 100)
        text = font.render(SubMessage, True, (0, 0, 0))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery + 40
        if(ImageShowed):
            backgroundPicture.blit(text, textpos)
        else:
            background.blit(text, textpos)
        
    if (Numeral != ""):
        font = pygame.font.SysFont("Brandon Grotesque Bold", 200)
        text = font.render(Numeral, True, (255, 255, 255))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        if(ImageShowed):
            backgroundPicture.blit(text, textpos)
        else:
            background.blit(text, textpos)

    if (CountDownPhoto != ""):
        #print(displaytext)
        font = pygame.font.SysFont("Brandon Grotesque Bold", 200)
        text = font.render(CountDownPhoto, True, (0, 0, 0))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        if(ImageShowed):
            backgroundPicture.blit(text, textpos)
        else:
            background.blit(text, textpos)

    if(ImageShowed == True):
        screenPicture.blit(backgroundPicture, (0, 0))       
    else:
        screen.blit(background, (0, 0))
   
    pygame.display.flip()
    return


def ShowPicture(file, delay):
    global pygame
    global screenPicture
    global backgroundPicture
    global ImageShowed
    backgroundPicture.fill((0, 0, 0))
    img = pygame.image.load(file)
    img = pygame.transform.scale(img, (1020,780))  # Make the image full screen
    #backgroundPicture.set_alpha(200)
    backgroundPicture.blit(img, (120,0))
    screen.blit(backgroundPicture, (0, 0))
    pygame.display.flip()  # update the display
    ImageShowed = True
    time.sleep(delay)
    
def ShowResult(file, delay):
    global pygame
    global screenPicture
    global backgroundPicture
    global ImageShowed
    backgroundPicture.fill((255, 255, 255))
    img = pygame.image.load(file)
    img = pygame.transform.scale(img, (320,720))  # Make the image fit screen
    #backgroundPicture.set_alpha(200)
    backgroundPicture.blit(img, (480,0))
    screen.blit(backgroundPicture, (0, 0))
    pygame.display.flip()  # update the display
    ImageShowed = True
    time.sleep(delay)
    
# display one image on screen
def show_image(image_path): 
    screen.fill(pygame.Color("white")) # clear the screen   
    img = pygame.image.load(image_path) # load the image
    img = img.convert() 
    set_demensions(img.get_width(), img.get_height()) # set pixel dimensions based on image 
    x = (infoObject.current_w / 2) - (img.get_width() / 2)
    y = (infoObject.current_h / 2) - (img.get_height() / 2)
    screen.blit(img,(x,y))
    pygame.display.flip()

def CapturePicture():
    global imagecounter
    global imagefolder
    global Numeral
    global Message
    global LongMessage
    global SubMessage
    global screen
    global background
    global screenPicture
    global backgroundPicture
    global pygame
    global ImageShowed
    global CountDownPhoto
    global BackgroundColor
    
    image = None

    BackgroundColor = ""
    Numeral = ""
    Message = ""
    UpdateDisplay()
    time.sleep(1)
    CountDownPhoto = ""
    UpdateDisplay()
    background.fill(pygame.Color("black"))
    screen.blit(background, (0, 0))
    pygame.display.flip()
    #camera.start_preview()
    BackgroundColor = "black"
    
    camera.start()
    # camera.set_controls(hflip = True, vflip = False)
    streaming = True
    countdown = 0
    x = 3
    Numeral = str(x)
    Message = ""    
    #UpdateDisplay()
    print(camera.get_size())
    print(background.get_size())
    
    while streaming:
        if image:
            if camera.query_image():
                image = camera.get_image(image)
        else:
            image = camera.get_image()
        
        image2 = pygame.transform.scale(image,screen_size)
        background.blit(image2, (0, 0))
        font = pygame.font.SysFont("Brandon Grotesque Bold", 200)
        text = font.render(str(x), True, (255, 255, 255))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        background.blit(text, textpos)
        screen.blit(background, (0,0))
        pygame.display.flip()  # update the display
        countdown = countdown + 1
        if countdown == 10:
            x = x - 1
            if x == 0:
                streaming = False
            else:
                countdown = 0         
    BackgroundColor = ""
    Numeral = ""
    LongMessage = ""
    Message = ""
    UpdateDisplay()
    image = camera.get_image(image)
    image2 = pygame.transform.scale(image,screen_size)
    background.blit(image2, (0, 0))
    screen.blit(background, (0,0))
    imagecounter = imagecounter + 1
    ts = time.time()
    filename = os.path.join(imagefolder, 'images', str(imagecounter)+"_"+str(ts) + '.png')
    pygame.image.save(background, filename)
    # camera.capture(filename, resize=(IMAGE_WIDTH, IMAGE_HEIGHT))
    camera.stop()
    time.sleep(1)
    ShowPicture(filename, 1)
    ImageShowed = False
    return filename
    
def TakePictures():
    global imagecounter
    global imagefolder
    global Numeral
    global Message
    global LongMessage
    global SubMessage
    global screen
    global background
    global pygame
    global ImageShowed
    global CountDownPhoto
    global BackgroundColor
    global Printing
    global PhotosPerCart
    global TotalImageCount
    
    LongMessage = ""

    input(pygame.event.get())
    CountDownPhoto = "Foto 1/3"    
    filename1 = CapturePicture()

    CountDownPhoto = "Foto 2/3"
    filename2 = CapturePicture()

    CountDownPhoto = "Foto 3/3"
    filename3 = CapturePicture()

    CountDownPhoto = ""
    Message = "Even geduld..."
    UpdateDisplay()

    image1 = PIL.Image.open(filename1)
    image2 = PIL.Image.open(filename2)
    image3 = PIL.Image.open(filename3)   
    TotalImageCount = TotalImageCount + 1

    bgimage.paste(image1, (57, 194))
    bgimage.paste(image2, (57, 664))
    bgimage.paste(image3, (57, 1137))
    
    # Create the final filename
    ts = time.time()
    Final_Image_Name = os.path.join(imagefolder, "Final_" + str(TotalImageCount)+"_"+str(ts) + ".png")
    # Save it to the usb drive
    bgimage.save(Final_Image_Name)
    # uploadToGP(Final_Image_Name)
    # Save a temp file, its faster to print from the pi than usb
    temppath = os.path.join('Temp', 'tempprint.png')
    bgimage.save(temppath)
    ShowResult(temppath,3)
    #bgimage2 = bgimage.rotate(90)
    #bgimage2.save(temppath)
    ImageShowed = False
    Message = ""
    Printing = False
    WaitForPrintingEvent()
    Numeral = ""
    Message = ""
    SubMessage = ""
    LongMessage = ""
    print(Printing)
    if Printing:
        if os.path.isfile(temppath):
            # Open a connection to cups
            conn = cups.Connection()
            # get a list of printers
            # printers = conn.getPrinters()
            # select printer 0
            printer_name = "Canon_MP250_series"
            Message = "Aan het printen..."
            UpdateDisplay()
            time.sleep(1)
            # print the buffer file
            printqueuelength = len(conn.getJobs())
            if printqueuelength > 1:
                ShowPicture(temppath,3)
                conn.enablePrinter(printer_name)
                Message = "Probleem met de printer... :("                
                UpdateDisplay()
                time.sleep(1)
            else:
                conn.printFile(printer_name, temppath, "PhotoBooth", {})
                time.sleep(40)            
    Message = ""
    Numeral = ""
    ImageShowed = False
    UpdateDisplay()
    os.remove(filename1)
    os.remove(filename2)
    os.remove(filename3)    

def MyCallback(channel):
    global Printing
    GPIO.remove_event_detect(BUTTON_PIN)
    Printing=True

def WaitForPrintingEvent():
    global BackgroundColor
    global Numeral
    global Message
    global LongMessage
    global SubMessage
    global Printing
    global pygame
    countDown = 5
    GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING)
    GPIO.add_event_callback(BUTTON_PIN, MyCallback)
    
    while Printing == False and countDown > 0:
        if(Printing == True):
            return
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    GPIO.remove_event_detect(BUTTON_PIN)
                    Printing = True
                    return        
        BackgroundColor = ""
        Numeral = ""
        SubMessage = str(countDown)
        LongMessage = "Druk op de knop om je foto af te drukken"
        UpdateDisplay()        
        countDown = countDown - 1
        time.sleep(1)

    GPIO.remove_event_detect(BUTTON_PIN)
        
def uploadToGP(filename):
    p = Popen(['/usr/bin/share/gpup','-a "trouw"', filename], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
def WaitForEvent():
    global pygame
    NotEvent = True
    while NotEvent:
            input_state = GPIO.input(BUTTON_PIN)
            if input_state == False:
                    NotEvent = False
                    return
        
            try:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                        if event.key == pygame.K_DOWN:
                            NotEvent = False
                            return
                    if event.type == QUIT:
                        pygame.quit()
            except:
                pygame.quit()
                        
            time.sleep(0.2)

def main(threadName, *args):
    InitFolder()
    
    try:
        while True:
            show_image('images/start_camera.jpg')
            WaitForEvent()
            time.sleep(0.2)
            TakePictures()
    except Exception as e:
        print(e)
        GPIO.cleanup()
        pygame.quit()
                    

# launch the main thread
Thread(target=main, args=('Main', 1)).start()
