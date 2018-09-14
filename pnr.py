from urllib.request import urlopen
from bs4 import BeautifulSoup
from colorama import Fore, Style
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
pnr_list = {}

login_user = "donotreply@ankit"
login_password = "a2I5cTNqeGhuZGkw"
smtp_server = "mail.smtp2go.com"
smtp_port = "2525"
from_addr = "aman.zed.mehra@gmail.com"
to_addr = "ankitseeme@gmail.com"

class ServerDownError(Exception):
    pass


def sendmail(pnr,train_name,boarding_date,old_status,current_status):
    msg = MIMEMultipart()
    msg['From'] = login_user
    msg['To'] = to_addr
    msg['Subject'] = "Change in PNR Status"
    body = "PNR".ljust(17) + str(pnr)
    body += "\n" + "Train".ljust(17) + train_name
    body += "\n" + "Boarding Date".ljust(17) + boarding_date
    body += "\n" + "Old Status".ljust(17) + old_status
    body += "\n" + "Current Status".ljust(17) + current_status
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(login_user, login_password)
    text = msg.as_string()
    server.sendmail(from_addr, to_addr, text)

try:
    with open('input_list.txt','r') as f:
        for line in f:
            if len(line.split('|')) == 2:
                pnr_list[line.split('|')[0]] = line.split('|')[1].strip()
            else:
                pnr_list[line.split('|')[0]] = ''
except:
    print("Input File Error... Please check")
    exit(1)
for pnr in pnr_list.keys():
    url = "https://www.railyatri.in/pnr-status/" + str(pnr)
    try:
        html = urlopen(url)
        if html.url.find(pnr) == -1:
            raise ServerDownError
    except ServerDownError:
        print("Server is down... Please try again")
    except:
        print("Url access error for PNR : " + str(pnr))
    else:
        try:
            bsobj = BeautifulSoup(html.read(),'html.parser')
            #print(bsobj)
            src_dst = bsobj.find('div',{'class':'train-route'}).findAll('div',{'class':' col-xs-4'})
            src = src_dst[0].find('p',{'class':'pnr-bold-txt'}).text
            dst = src_dst[1].find('p',{'class':'pnr-bold-txt'}).text
            boarding_date = bsobj.find('div',{'class':'boarding-detls'}).findAll('div',{'class':' col-xs-4'})[0].find('p',{'class':'pnr-bold-txt'}).text
            statuses = bsobj.findAll('div',{'id':'status'})[0].findAll('p',{'class':'pnr-bold-txt'})
            booking_status = statuses[0].text.strip()
            current_status = statuses[1].text.strip()
            train_name = bsobj.find('div',{'class':' col-xs-12 train-info'}).find('p',{'class':'pnr-bold-txt'}).text
            chart_status = bsobj.find('p',{'class','chart-status-txt'}).text
        except:
            print("Please check if the PNR : " + str(pnr) + " is valid")
            print("If PNR is valid, try later")
            print("You can visit " + url + " for details")
        else:
            print("PNR".ljust(17) + str(pnr))
            print("Train".ljust(17) + train_name)
            print("Source".ljust(17) + src)
            print("Destination".ljust(17) + dst)
            print("Date of Journey".ljust(17) + boarding_date)
            print("Booking Status".ljust(17) + booking_status)
            if current_status.find('RAC') != -1:
                print("Current Status".ljust(17) + Fore.LIGHTRED_EX + Style.BRIGHT + current_status + Style.RESET_ALL)
            elif current_status.find('W/L') != -1:
                print("Current Status".ljust(17) + Fore.RED + Style.BRIGHT + current_status + Style.RESET_ALL)
            elif current_status.find('CNF') != -1:
                print("Current Status".ljust(17) + Fore.GREEN + Style.BRIGHT + current_status + Style.RESET_ALL)
            else:
                print("Current Status".ljust(17) + Fore.YELLOW + Style.BRIGHT + current_status + Style.RESET_ALL)
            if chart_status.find('NOT') != -1:
                print("Chart Status".ljust(17) + Fore.YELLOW + Style.BRIGHT + chart_status + Style.RESET_ALL)
            else:
                print("Chart Status".ljust(17) + Fore.LIGHTGREEN_EX + Style.BRIGHT + chart_status + Style.RESET_ALL)
            print("More Details".ljust(17) + url)
            if current_status != pnr_list[pnr] and pnr_list[pnr] != '':
                #print("CHANGED")
                print("There has been a change in status. Sending details via email")
                #sendmail(pnr,train_name,boarding_date,pnr_list[pnr],current_status)
                print("Email sent")
            pnr_list[pnr] = current_status        
        print("\n")
#for pnr in pnr_list.keys():
#    print(pnr + "|" + pnr_list[pnr])
with open('input_list.txt','w') as f:
    for pnr in pnr_list.keys():
        f.write(pnr + "|" + pnr_list[pnr])
        f.write("\n")
print("-"*25 + " END " + "-"*25)