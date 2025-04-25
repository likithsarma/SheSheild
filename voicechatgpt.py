import RPi.GPIO as  GPIO
import telepot
import time
import cv2
import cv2
import time
import serial

vs = cv2.VideoCapture(0)
time.sleep(2)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
import speech_recognition as sr
ss=2
buz=26
GPIO.setup(ss, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(buz,GPIO.OUT)
GPIO.output(buz,False)
def GPS_Info():
    global NMEA_buff
    global lat_in_degrees
    global long_in_degrees
    nmea_time = []
    nmea_latitude = []
    nmea_longitude = []
    nmea_time = NMEA_buff[0]                    #extract time from GPGGA string
    nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
    nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string
    
    #print("NMEA Time: ", nmea_time,'\n')
    #print ("NMEA Latitude:", nmea_latitude,"NMEA Longitude:", nmea_longitude,'\n')
    try:
        lat = float(nmea_latitude)                  #convert string into float for calculation
        longi = float(nmea_longitude)               #convertr string into float for calculation
    except:
        lat=0
        longi=0
    lat_in_degrees = convert_to_degrees(lat)    #get latitude in degree decimal format
    long_in_degrees = convert_to_degrees(longi) #get longitude in degree decimal format
    

def send_sms():
    global map_link
    print("sending SMS..")

    cmd='AT\r\n'
    ser.write(cmd.encode())
    time.sleep(2)
    rcv = ser.read(20)
    print(rcv)
    cmd='AT+CMGF=1\r\n'
    ser.write(cmd.encode())
    time.sleep(2)
    rcv = ser.read(20)
    print(rcv)                                             
    phno="phone_number"                          
    cmd='AT+CMGS="'+str(phno)+'"\r\n'
    ser.write(cmd.encode())
    rcv = ser.read(20)
    print(rcv)                        
    time.sleep(1)
    cmd="women is in danger at"
    ser.write(cmd.encode())  # Message
    cmd=map_link
    ser.write(cmd.encode())  # Message
    #ser.write(msg.encode())  # Message
    time.sleep(1)
    cmd = "\x1A"
    ser.write(cmd.encode()) # Enable to send SMS
    time.sleep(10)
    print('SMS Sent')
    time.sleep(1)

def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f" %(position)
    return position


gpgga_info = "$GPGGA,"
ser = serial.Serial ("/dev/ttyS0",timeout=0.1)              #Open port with baud rate
GPGGA_buffer = 0
NMEA_buff = 0
lat_in_degrees = 0
long_in_degrees = 0
kk=0

def handle(msg):
  global telegramText
  global chat_id
  global receiveTelegramMessage
  
  chat_id = msg['chat']['id']
  telegramText = msg['text']
  
  print("Message received from " + str(chat_id))
  
  if telegramText == "/start":
    bot.sendMessage(chat_id, "Welcome to project Bot")

  
  else:
    buzzer.beep(0.1, 0.1, 1)
    receiveTelegramMessage = True

def capture():
    
    print("Sending photo to " + str(chat_id))
    bot.sendPhoto(chat_id, photo = open('./image.jpg', 'rb'))


bot = telepot.Bot("token")
chat_id='id'
bot.message_loop(handle)

print("Telegram bot is ready")

bot.sendMessage(chat_id, 'BOT STARTED')
time.sleep(2)



map_link=''





def listen_and_respond():
    global kk
    global map_link
    r = sr.Recognizer()

    # Listen for input
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    # Try to recognize the audio
    try:
        prompt = r.recognize_google(audio)
        print("You said:", prompt)
        if(prompt =='good morning'):
            canc=0
            ii=0
            while(ii<10):
                GPIO.output(buz,1)
                ii=ii+1
                time.sleep(0.25)
                GPIO.output(buz,0)
                time.sleep(0.25)
                if(GPIO.input(ss)==0):
                    canc=1
            if(canc==0):
              GPIO.output(buz,1)
              received_data = (str)(ser.readline())                   #read NMEA string received
              GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string
              if(kk==0):
                  lat_in_degrees=0
                  lat_in_degrees=0
              if (GPGGA_data_available>0):
                  kk=1
                  GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string 
                  NMEA_buff = (GPGGA_buffer.split(','))               #store comma separated data in buffer
                  GPS_Info()                                          #get time, latitude, longitude
                  map_link = 'http://maps.google.com/?q=' + str(lat_in_degrees) + ',' + str(long_in_degrees)    #create link to plot location on Google map
              
              map_link = 'http://maps.google.com/?q=' + str(lat_in_degrees) + ',' + str(long_in_degrees)    #create link to plot location on Google map
              print("lat in degrees:", lat_in_degrees," long in degree: ", long_in_degrees, '\n')
              print()


              (grabbed, frame) = vs.read()
              cv2.imshow('input',frame)
              cv2.waitKey(1)
              cv2.imwrite("image.jpg",frame)
              cv2.waitKey(1)
              bot.sendMessage(chat_id, map_link)
              capture()
              send_sms()
              time.sleep(1)
            else:
              print('skipped')
    except:
        print('not recognized')

 
def main():
    while True:
          

        listen_and_respond()

if __name__ == "__main__":
    main()
