# loading necesssary dependencies and librares
import matplotlib.pyplot as plt
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import mimetypes
from email.message import EmailMessage
from email import encoders
from email.mime.base import MIMEBase



####################################################################################################
# load the pre-built face detection results which was generated from the previous meeting.
def load_face_detection_results(input_file_name_face):
    #initilializing temporary variables
    server_time = []
    server_face_results = []
    #initilializing face detection temporary variables
    client_time = []
    client_face_results = []
    #initilializing time temporary variables
    server_una_time = []
    client_una_time = []
    #initilializing dictionary temporary variables
    server_sequence_ids = []
    client_sequence_ids = []
    
    # open the pre-built face detection results
    f = open(input_file_name_face)
    data = json.load(f)
    
    # iterate throughout the json data extracted
    for i in data:
        temp_key = list(i.keys())[0]
        temp_dct=i[temp_key]
        temp_key_1 = list(temp_dct.keys())[0]
        # tag the transcripts extracted from the json file to extract unattentiveness timelines
        if temp_key_1 == "server":
            temp_time_str = temp_dct[temp_key_1][0][0].replace("$", ":")
            #print(temp_time_str)
            server_time.append(temp_time_str)
            server_face_results.append(str(temp_dct[temp_key_1][1][0]))
            #print(type(temp_dct[temp_key_1][1][0]))
            # tagging unattentiveness timeline at the server's end
            if (temp_dct[temp_key_1][1][0] == 1) or (temp_dct[temp_key_1][1][0] == 2):
                server_una_time.append(temp_time_str)
                server_sequence_ids.append(temp_key)
        # tag the transcripts extracted from the json file to extract unattentiveness timelines
        if temp_key_1 == "client":
            temp_time_str_1 = temp_dct[temp_key_1][0][0].replace("$", ":")
            # tagging unattentiveness timeline at the client's end
            client_time.append(temp_time_str_1)
            client_face_results.append(str(temp_dct[temp_key_1][1][0]))   
            if (temp_dct[temp_key_1][1][0] == 1) or (temp_dct[temp_key_1][1][0] == 2):
                client_una_time.append(temp_time_str)
                client_sequence_ids.append(temp_key)
     # close the file object to avoid read and write deadlocks       
    f.close()
    return server_time, server_face_results, server_una_time, server_sequence_ids, client_time, client_face_results, client_una_time, client_sequence_ids
    
#################################################################################################

def load_audio_transcripts_data(input_file_name_audio):
    # read the pre-built audio transcripts file.
    f_1 = open(input_file_name_audio)
    # initialize the file object to read the data
    another_data = json.load(f_1)
    
    audio_sequence_transcripts = {}
    # initialize the temporary variables
    temp_text_audio_transcripts = ""
    
    # iterate through the list
    for temp_i in another_data:
        # indexing the dictionary to extract temporary key
        audio_temp_key = list(temp_i.keys())[0]
        audio_temp_dct=temp_i[audio_temp_key]
        audio_temp_key_1 = list(audio_temp_dct.keys())[0]
        # loadng transcripts via index into another temporary dictionary
        audio_sequence_transcripts[audio_temp_key] = [[audio_temp_key_1], [audio_temp_dct[audio_temp_key_1][1][0]]]
        # tagging the transcripts into server and clients to make the meeting transcriptions more interactive
        if audio_temp_key_1 == "server":
            temp_text_audio_transcripts = temp_text_audio_transcripts + str("\nPremith: ") + str(audio_temp_dct[audio_temp_key_1][1][0])
        else:
            temp_text_audio_transcripts = temp_text_audio_transcripts + str("\nNikhil: ") + str(audio_temp_dct[audio_temp_key_1][1][0])
    # clode teh file object        
    f_1.close()
    # opening another text file to store the meeting notes
    file_object = open("meeting_notes.txt", "w", encoding="utf-8")
    file_object.write(temp_text_audio_transcripts)
    # closing the file object
    file_object.close()
    
    #print(audio_sequence_transcripts)
    return audio_sequence_transcripts

##################################################################################################


# function to calculate the closest index in "lst" with respect to K.
def closest(lst, K):
    return lst[min(range(len(lst)), key = lambda i: abs(int(lst[i])-int(K)))]


def match_audio_transcripts_server(input_lst, audio_sequence_transcripts):
    # initilized temporary store variable for meeting transcription
    server_missed_meeting = {}
    # iterate throught eh list
    for sed_id in input_lst:
        ret_closest = closest(list(audio_sequence_transcripts.keys()), sed_id)
        #print(ret_closest)
        #if ret_closest in server_missed_meeting:
            #print(ret_closest)
        server_missed_meeting[ret_closest] = audio_sequence_transcripts[ret_closest]
        #server_mised_meeting.append(audio_sequence_transcripts[])
    # return the meeting transcripts.
    return server_missed_meeting


def match_audio_transcripts_client(input_lst, audio_sequence_transcripts):
    # initilized temporary store variable for meeting transcription
    client_missed_meeting = {}
    # iterate throught eh list
    for sed_id_1 in input_lst:
        ret_closest_1 = closest(list(audio_sequence_transcripts.keys()), sed_id_1)
        #print(type(ret_closest_1))
        #if ret_closest_1 not in client_missed_meeting:
        client_missed_meeting[ret_closest_1] = audio_sequence_transcripts[ret_closest_1]
    # return the meeting transcripts.
    return client_missed_meeting
##################################################################################################

def email_triggering(email_body, to_email, image_file_path):
    # email details
    sender_email = "sid2lose@outlook.com"
    receiver_email = to_email
    subject = "Personlized Meeting Attentiveness summary"
    body = email_body
    #image_file = "client_graph.png"

    # create a multipart message object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # add body to the message
    msg.attach(MIMEText(body, 'plain'))

    # add image to the message
    with open(image_file_path, 'rb') as fp:
        img = MIMEImage(fp.read())
    img.add_header('Content-Disposition', 'attachment', filename='image.png')
    msg.attach(img)
    
    attachment = open("meeting_notes.txt", "rb")
      
    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
      
    # To change the payload into encoded form
    p.set_payload((attachment).read())
      
    # encode into base64
    encoders.encode_base64(p)
       
    p.add_header('Content-Disposition', "attachment; filename= %s" % "meeting_notes.txt")
      
    # attach the instance 'p' to instance 'msg'
    msg.attach(p)


    # connect to SMTP server and send email
    smtp_server = "smtp-mail.outlook.com"
    smtp_port = 587
    smtp_username = "sid2lose@outlook.com"
    smtp_password = "Siddh@rth.99"
    # meeting message objects for sending
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())


def load_meeting_meta_data():
    # load meeting invitation json
    meeting_file = open("form_data.json")
    # load invitation data
    meeting_data = json.load(meeting_file)
    # index the data accordingly to get server side's email address, port address, and names
    host_ip = meeting_data[0]["main"]["ipaddress"]
    host_email = meeting_data[0]["main"]["email"]
    host_port_address = meeting_data[0]["main"]["port"]
    host_name = meeting_data[0]["main"]["name"]
    
    #print(host_ip, host_email, host_port_address, host_name)
    # index the data accordingly to get server side's email address, port address, and names
    parasite_ip = meeting_data[1]["others"][0]["ipaddress"]
    parasite_email = meeting_data[1]["others"][0]["email"]
    parasite_port_address = meeting_data[1]["others"][0]["port"]
    parasite_name = meeting_data[1]["others"][0]["name"]
    
    #print(host_ip, host_email, host_port_address, host_name)
    
    #print(parasite_ip, parasite_email, parasite_port_address, parasite_name)
    # returning the extracted data.
    return host_ip, host_email, host_port_address, host_name, parasite_ip, parasite_email, parasite_port_address, parasite_name




def use_case_1():
    try:
        # loadinig th emeeting data
        h_ip, h_email, h_port_address, h_name, p_ip, p_email, p_port_address, p_name = load_meeting_meta_data()
        # printing their data
        print(h_email, p_email)
        # loadiing the unattentivenss timeline
        server_time, server_face_results, server_una_time, server_sequence_ids, client_time, client_face_results, client_una_time, client_sequence_ids = load_face_detection_results("face_detection_results.json")
        print("participant - 1 's unattentiveness timings:")
        print(server_una_time)
        #print(server_sequence_ids)
        print("participant - 2 's unattentiveness timings:")
        print(client_una_time)
        #print(client_sequence_ids)
        #plt.xticks(np.arange(min(unemployment_rate), max(unemployment_rate), 1.0))
        # plotting participant-1's attention graph
        plt.figure(figsize=(7, 7))
        plt.plot(server_time, server_face_results)
        plt.title('Personalized meeting attention plot\n(0: attentive)  (1: not-attentive)  (2: face not identified)')
        plt.xlabel('Meeting Duration')
        plt.ylabel('Attentiveness Scale')
        #plt.xticks(range(len(unemployment_rate)), unemployment_rate)
        #plt.xticks(color='w')
        plt.xticks(server_time, [str(i) for i in server_time], rotation=90)
        plt.tick_params(axis='x', which='major', labelsize=5)
        # saving the graph
        plt.savefig('participant_1.png', dpi =300)
        
        # plotting participant-2's attention graph
        plt.figure(figsize=(7, 7))
        plt.plot(client_time, client_face_results)
        plt.title('Personalized meeting attention plot\n(0: attentive)  (1: not-attentive)  (2: face not identified)')
        plt.xlabel('Meeting Duration')
        plt.ylabel('Attentiveness Scale')
        #plt.xticks(range(len(unemployment_rate)), unemployment_rate)
        #plt.xticks(color='w')
        plt.xticks(client_time, [str(j) for j in client_time], rotation=90)
        plt.tick_params(axis='x', which='major', labelsize=5)
        # saving the graph
        plt.savefig('participant_2.png', dpi =300)
        # load the audio tanscriptions
        audio_sequence_transcripts = load_audio_transcripts_data("audio_results.json")
        # get the matched meeting audio parts via text matching
        server_final_results = match_audio_transcripts_server(server_sequence_ids, audio_sequence_transcripts)
        client_final_results = match_audio_transcripts_client(client_sequence_ids, audio_sequence_transcripts)
        # building Eail text for PARTICIPANT-1
        if len(server_una_time)>0:
            server_email_body_text = "In the Meeting, You did not pay attention during the following timings : "
            
            server_email_body_text = server_email_body_text + ", ".join(server_una_time)
            
            server_email_body_text = server_email_body_text + "\n \n \n"
            
            server_email_body_text = server_email_body_text + "Also, you might have missed the following context during the meeting :\n"
            # personlized tagging of meeting transcripts.
            for temp_key_srvr in list(server_final_results.keys()):
                if server_final_results[temp_key_srvr][0][0] == "server":
                    server_email_body_text = server_email_body_text + "Premith: " + str(server_final_results[temp_key_srvr][1][0]) + "\n"
                else:
                    server_email_body_text = server_email_body_text + "Nikhil: " + str(server_final_results[temp_key_srvr][1][0]) + "\n"
            # triggerng the email
            email_triggering(server_email_body_text, h_email, "participant_1.png")
        # building Eail text for PARTICIPANT-2   
        if len(client_una_time)>0:
            client_email_body_text = "In the Meeting, You did not pay attention during the following timings : "
            
            client_email_body_text = client_email_body_text + ", ".join(client_una_time)
            
            client_email_body_text = client_email_body_text + "\n \n \n"
            
            client_email_body_text = client_email_body_text + "Also, you might have missed the following context during the meeting :\n"
            
            # personlized tagging of meeting transcripts.
            for temp_key_client in list(client_final_results.keys()):
                if client_final_results[temp_key_client][0][0] == "server":
                    client_email_body_text = client_email_body_text + "Premith: " + str(server_final_results[temp_key_srvr][1][0]) + "\n"
                else:
                    client_email_body_text = client_email_body_text + "Nikhil: " + str(server_final_results[temp_key_srvr][1][0]) + "\n"
            # triggerng the email
            email_triggering(client_email_body_text, p_email, "participant_2.png")
             
        
        # returning the finalized meeting context which the participants missed due to unattentiveness
        return server_final_results, client_final_results
    
    except:
        print("please check the dependencies")
    
    
print(use_case_1())
