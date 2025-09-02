import datetime
import json
import csv
import os
from collections import Counter
from crypto_utils import load_key, decrypt_file, encrypt_file

import face_recognition 
import csv
import base64
from io import BytesIO
from PIL import Image
import face_recognition

import cv2
from pyzbar.pyzbar import decode

import requests
from flask import render_template, redirect, request,flash
from app import app

CONNECTED_SERVICE_ADDRESS = "http://127.0.0.1:9001"
NATIONAL_SERVER_ADDRESS ="https://evoting.pythonanywhere.com/"

import re

def validate_input(input_string):
    if re.match("^[A-Za-z0-9@&_? ]+$", input_string):
        return True
    else:
        return False
    
def extract_uid_from_qr(qr_text):
    match = re.search(r'uid="([A-Z]+\d+)"', qr_text)
    if match:
        return match.group(1)
    return None

def grab_ids():
    dict={}
    with open(os.path.join("recog/", "authorized_ids.csv"), mode ='r')as file:
        csvFile = csv.reader(file)
        for rows in csvFile:
            dict[rows[0]]=rows[1]
    return dict
            

def verify_document(document_image, voter_id):
    
    img = cv2.imread(document_image)
    qr_codes = decode(img)
    
    if not qr_codes:
        return False, "No QR code found in document"

    qr_text = qr_codes[0].data.decode('utf-8')    
    doc_uid = extract_uid_from_qr(qr_text)
    
    if not doc_uid:
        return False, "Invalid QR code format"
        
    dict_ids=grab_ids()
    if voter_id in list(dict_ids.keys()):
        if dict_ids[voter_id]==doc_uid:
            return True, "Document verified successfully"
        else:
            return False, "Document UID does not match voter ID"
    else:
        return False, f"Document verification not set up for voter ID:({voter_id})"
    

import os
import face_recognition
import csv

def load_known_faces_and_ids(directory, csv_file):
    known_faces = []
    authorized_voter_ids = {}

    with open(os.path.join(directory, csv_file), mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            image_path = os.path.join(directory, row["filename"])
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_faces.append(encoding)
            voter_ids = row["voter_ids"].split(":")
            for voter_id in voter_ids:
                if voter_id not in authorized_voter_ids:
                    authorized_voter_ids[voter_id] = []
                authorized_voter_ids[voter_id].append(encoding)

    return known_faces, authorized_voter_ids

known_faces, authorized_voter_ids = load_known_faces_and_ids("recog/", "authorized_voters.csv")



def load_candidates_from_csv(file_path):
    candidates = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            candidates.append({
                "name": row["name"],
                "logo": row["logo"],
            })
    return candidates



Candidatespresident = load_candidates_from_csv("candidatespresident.csv")
Candidateshead = load_candidates_from_csv("candidateshead.csv")

candidates_list_president = [x["name"] for x in Candidatespresident]
candidates_list_head = [x["name"] for x in Candidateshead]




def write_candidates_to_csv(candidates, file_path): 
    with open(file_path, mode='w', newline='') as file: 
        fieldnames = ['name', 'logo'] 
        writer = csv.DictWriter(file, fieldnames=fieldnames) 
        writer.writeheader() 
        for candidate in candidates: 
            writer.writerow({ 'name': candidate['name'], 'logo': candidate['logo']})



VOTER_IDS=[]

Passwords = {}
key = load_key()
decrypt_file("passwords.csv", key)

with open("passwords.csv", "r") as file:
    data = file.read()
    if data:
        Passwords = dict(ele.split(":") for ele in data.split(","))
    else:
        Passwords={}
    VOTER_IDS = list(Passwords.keys())

encrypt_file("passwords.csv", key)


vote_check=[]
posts = []


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_SERVICE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        vote_count = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)


        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)




@app.route('/vote')
def vote():
    available_voter_ids = [voter_id for voter_id in VOTER_IDS if voter_id not in vote_check]
    if len(available_voter_ids)>18:
        available_voter_ids = available_voter_ids[0:30]
    return render_template('vote_acc.html',
                           title='Vote',
                           node_address=CONNECTED_SERVICE_ADDRESS,
                           readable_time=timestamp_to_string,
                           candidates_list_head=candidates_list_head,
                           candidates_list_president=candidates_list_president,
                           voter_ids=available_voter_ids,
                           Candidatespresident=Candidatespresident,
                           Candidateshead=Candidateshead)

from concurrent.futures import ThreadPoolExecutor

@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    president = request.form["president"]
    head = request.form["head"]
    voter_id = request.form["voter_id"]
    password = request.form["password"]
    face_image_data = request.form["face_image"]
    document = request.files["document"]

    post_object = {
        'voter_id': voter_id,
        'president': president,
        'head': head,
    }

    if not validate_input(voter_id) or not validate_input(password) or not validate_input(president) or not validate_input(head):
        flash('Invalid input detected.', 'error')
        return redirect('/vote')

    if voter_id not in VOTER_IDS:
        flash('Voter ID invalid, please select a voter ID from sample!', 'error')
        return redirect('/vote')
    if voter_id in vote_check:
        flash('Voter ID (' + voter_id + ') has already voted, Vote can be done by unique vote ID only once!', 'error')
        return redirect('/vote')
    if password != Passwords[voter_id]:
        flash('Password doesn\'t match', 'error')
        return redirect('/vote')
    if not document:
        flash('No document uploaded', 'error')
        return redirect('/vote')

    document_path = "temp_doc.jpg"
    document.save(document_path)

    face_image_data = face_image_data.split(",")[1]
    face_image_bytes = base64.b64decode(face_image_data)
    face_image = Image.open(BytesIO(face_image_bytes))
    face_image.save("captured_image.jpg")

    def verify_document_task():
        return verify_document(document_path, voter_id)

    def face_recognition_task():
        image = face_recognition.load_image_file("captured_image.jpg")
        small_image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
        face_encodings = face_recognition.face_encodings(small_image)
        return face_encodings

    with ThreadPoolExecutor() as executor:
        doc_future = executor.submit(verify_document_task)
        face_future = executor.submit(face_recognition_task)

        is_valid, message = doc_future.result()
        face_encodings = face_future.result()

    if not is_valid:
        flash(message, 'error')
        return redirect('/vote')

    if len(face_encodings) > 0:
        match_found = False
        for encoding in face_encodings:
            if voter_id in authorized_voter_ids:
                matches = face_recognition.compare_faces(authorized_voter_ids[voter_id], encoding)
                if any(matches):
                    match_found = True
                    break
        if not match_found:
            flash('Facial recognition failed, unauthorized voter.', 'error')
            return redirect('/vote')
    else:
        flash('No face detected in the captured image.', 'error')
        return redirect('/vote')

    vote_check.append(voter_id)

    new_tx_address = "{}/new_transaction".format(CONNECTED_SERVICE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    mine_address = "{}/mine".format(CONNECTED_SERVICE_ADDRESS)
    mine_response = requests.get(mine_address)
    mine_data = mine_response.json()  # If no transaction to mine check to be added
    if mine_data == "No transaction to mine":
        return "Error: No transaction to mine"
    block_hash = mine_data["block_hash"]
    return render_template('final.html', title='Success!', block_hash=block_hash)




def fetch_chain():
    get_chain_address = "{}/chain".format(CONNECTED_SERVICE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        chain = json.loads(response.content)['chain']
        return chain
    return []

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        block_hash = request.form['hash']
        chain = fetch_chain()
        for block in chain:
            if block['hash'] == block_hash:
                return render_template('verify.html', title='Verify Hash', valid=True, block=block)
        return render_template('verify.html', title='Verify Hash', valid=False)
    return render_template('verify.html', title='Verify Hash',valid=None)



def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')

@app.route('/addvoter', methods=['POST'])
def addvoter():
    voter_id = request.form["voter_id"]
    password = request.form["password"]
    face_image = request.files["face_image"]
    document = request.files["document"]

    post_object = {
        'voter_id': voter_id,
    }

    voter_exists = voter_id in Passwords

    Passwords[voter_id] = password
    obj = str(Passwords)
    obj = obj.replace("}", "")
    obj = obj.replace("{", "")
    obj = obj.replace("'", "")
    obj = obj.replace(" ", "")
    with open("passwords.csv", "w") as file:
        file.write(obj)
    key = load_key()
    encrypt_file("passwords.csv", key)

    face_image_path = os.path.join("recog/", f"{voter_id}.jpg")
    face_image.save(face_image_path)

    document_path = os.path.join("recog/", f"{voter_id}_doc.jpg")
    document.save(document_path)

    img = cv2.imread(document_path)
    qr_codes = decode(img)
    if not qr_codes:
        flash('No QR code found in document', 'error')
        return redirect('/admin')
    qr_text = qr_codes[0].data.decode('utf-8')
    doc_uid = extract_uid_from_qr(qr_text)
    if not doc_uid:
        flash('Invalid QR code format', 'error')
        return redirect('/admin')

    authorized_ids_path = os.path.join("recog/", "authorized_ids.csv")
    updated = False
    rows = []

    with open(authorized_ids_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[0] == voter_id:
                row[1] = doc_uid
                updated = True
            rows.append(row)

    with open(authorized_ids_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    if not updated:
        with open(authorized_ids_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([voter_id, doc_uid])

    image = face_recognition.load_image_file(face_image_path)
    encoding = face_recognition.face_encodings(image)[0]
    if voter_id not in authorized_voter_ids:
        authorized_voter_ids[voter_id] = []
    authorized_voter_ids[voter_id].append(encoding)

    authorized_voters_path = os.path.join("recog/", "authorized_voters.csv")
    updated = False
    rows = []

    with open(authorized_voters_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row["filename"] == f"{voter_id}.jpg":
                row["voter_ids"] = voter_id
                updated = True
            rows.append(row)

    with open(authorized_voters_path, mode='w', newline='') as file:
        fieldnames = ['filename', 'voter_ids']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if not updated:
        with open(authorized_voters_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([f"{voter_id}.jpg", voter_id])

    if voter_exists:
        flash("Voter ID has been updated in the list, start a new election to activate it")
    else:
        flash("Voter ID has been added to the list, start a new election to activate it")

    fetch_posts()
    vote_gain_president = [post["president"] for post in posts]
    vote_gain_head = [post["head"] for post in posts]
    return render_template('index.html', title='Admin Page',
                           posts=posts, vote_gain_president=vote_gain_president, vote_gain_head=vote_gain_head,
                           node_address=CONNECTED_SERVICE_ADDRESS,
                           readable_time=timestamp_to_string,
                           voter_ids=VOTER_IDS,
                           Candidatespresident=Candidatespresident,
                           Candidateshead=Candidateshead)

@app.route('/')
def landing():
    return render_template('landing.html',)

@app.route('/admin')
def admin():
    return render_template('admin.html',)

def render_admin_page(message=None, category=None):
    fetch_posts()
    vote_gain_president = [post["president"] for post in posts]
    vote_gain_head = [post["head"] for post in posts]
    if message:
        flash(message, category)
    return render_template('index.html', title='Admin Page',
                           posts=posts, vote_gain_president=vote_gain_president,vote_gain_head=vote_gain_head,
                           node_address=CONNECTED_SERVICE_ADDRESS,
                           readable_time=timestamp_to_string,
                           voter_ids=VOTER_IDS,
                           Candidatespresident=Candidatespresident,
                           Candidateshead=Candidateshead)


@app.route('/login', methods=['POST'])
def login():
    ID = request.form["id"]
    password = request.form["passadmin"]

    if ID!="admin" or password!="pass":
        flash("Incorrect Username or Password")
        return redirect('/admin')
    else:
        return render_admin_page()
    

@app.route('/addcand', methods=['POST'])
def add_candidate():
    candname = request.form["candname"]
    candtype = request.form["candtype"]
    partysymbol = request.files["logo"]
    
    if candtype=="president":
        global candidates_list_president
        if candname in candidates_list_president:
            return render_admin_page(f'({candname}) Candidate already exists', 'error')
        else: 
            tempcand = {'name': candname,'logo': "static/" + partysymbol.filename}
            partysymbol.save("app/static/" + partysymbol.filename)
            Candidatespresident.append(tempcand)
            write_candidates_to_csv(Candidatespresident, "Candidatespresident.csv")
            candidates_list_president = [x["name"] for x in Candidatespresident]
    elif candtype=="head":
        global candidates_list_head
        if candname in candidates_list_head:
            return render_admin_page(f'({candname}) Candidate already exists', 'error')
        else: 
            tempcand = {'name': candname,'logo': "static/" + partysymbol.filename}
            partysymbol.save("app/static/" + partysymbol.filename)
            Candidateshead.append(tempcand)
            write_candidates_to_csv(Candidateshead, "Candidateshead.csv")
            candidates_list_head = [x["name"] for x in Candidateshead]

            return render_admin_page('Candidate added', 'success')
    else:
        return render_admin_page(f'({candtype}) Candidate type invalid', 'error')


@app.route('/delcand', methods=['POST'])
def delete_candidate():
    candname = request.form["candname"]
    candtype = request.form["candtype"]

    if candtype=="president":
        global candidates_list_president
        global Candidatespresident
        if candname not in candidates_list_president:
            return render_admin_page(f'({candname}) does not exist in {candidates_list_president}', 'error')
        else:
            Candidatespresident = [x for x in Candidatespresident if x['name'] != candname]
            write_candidates_to_csv(Candidatespresident, "Candidatespresident.csv")
            candidates_list_president = [x["name"] for x in Candidatespresident]
            return render_admin_page('Candidate deleted', 'success')
    elif candtype=="head":
        global candidates_list_head
        global Candidateshead
        if candname not in candidates_list_head:
            return render_admin_page(f'({candname}) does not exist in {candidates_list_head}', 'error')
        else:
            Candidateshead = [x for x in Candidateshead if x['name'] != candname]
            write_candidates_to_csv(Candidateshead, "Candidateshead.csv")
            candidates_list_head = [x["name"] for x in Candidateshead]
            return render_admin_page('Candidate deleted', 'success')

   

@app.route('/result')
def result():
    global decl
    if decl=="yes":
        fetch_posts()
        vote_gain_president = [post["president"] for post in posts]
        vote_gain_head = [post["head"] for post in posts]
    
        return render_template('resulty.html',
                           posts=posts,
                           vote_gain_president=vote_gain_president,
                           vote_gain_head=vote_gain_head,
                           node_address=CONNECTED_SERVICE_ADDRESS,
                           readable_time=timestamp_to_string,
                           Candidatespresident=Candidatespresident,
                           Candidateshead=Candidateshead,)
                           #data=data)
    else:
        turnout=(len(vote_check)/len(VOTER_IDS))*100
        return render_template('resultn.html',Turnout=turnout)


@app.route('/declare')
def declare():
    global decl
    decl="yes"
    return redirect('/result')


