#http://127.0.0.1:8000/seller_database (To get access to the seller details)
#http://127.0.0.1:8000/company_database (To get access to the company registration details)

#importing the required libraries!
from flask import *
import hashlib
import datetime
import sqlite3 as sql
import qrcode 
from PIL import Image
import io
import base64
# import png
import cv2
app= Flask(__name__)

#index or home page 
@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")

#login page for seller
@app.route("/login")
def login():
    return render_template("login.html")

#registration page for seller
@app.route("/register")
def register():
    return render_template("register.html")

#product registration page for seller
@app.route("/seller",methods=['POST','GET'])
def seller():
    return render_template("seller.html")

#creating a new entry for each seller registered in the database
@app.route("/seller_registered",methods=['POST','GET'])
def seller_registered():
    cin = str(request.form.get("cin"))
    cname = str(request.form.get("cname"))
    url = str(request.form.get("url"))
    email = str(request.form.get("email"))
    password = str(request.form.get("password"))
    address= str(request.form.get("address"))

    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("DELETE FROM companydetails where companyname = 'None'")
    #cur.execute("CREATE TABLE companydetails(cin TEXT, companyname TEXT, url TEXT, email TEXT, password TEXT, address TEXT)")
    cur = con.execute("select cin,companyname from companydetails")
    row = cur.fetchall()
    for row in row:
        if (cin != row[0]) and (cname != row[1]) :
            cur = con.cursor()
            cur.execute("INSERT INTO companydetails (cin, companyname, url, email, password, address) VALUES (?,?,?,?,?,?)",(cin,cname,url,email,password,address))
            con.commit()
            return render_template("register.html",msg="thank you for registering!")
        
        else:
            return render_template("register.html",msg="THE ACCOUNT ALREADY EXISTS!!")

    #sname = str(request.form.get("sname"))
    #domain = str(request.form.get("domain"))
    #url = str(request.form.get("url"))
    #email = str(request.form.get("email"))
    #password = str(request.form.get("password"))
    #contactnumber = str(request.form.get("contactnumber"))
    #address = str(request.form.get("address"))
    #country = str(request.form.get("country"))
    #state = str(request.form.get("state"))
    #pincode = str(request.form.get("pincode"))
        
    #con = sql.connect("database.db")
    #cur=con.execute("DELETE FROM company where Email = 'abc@gmail'")
    #cur = con.execute("select SellerName,email from company")
    #row = cur.fetchall()
    #for row in row:
    #    if (sname != row[0]) and (email != row[1]) :
            #cur = con.cursor()
            #cur.execute("CREATE TABLE company (SellerName TEXT, Domain TEXT, URL TEXT, Email TEXT, Password TEXT, Contact TEXT, Address TEXT, Country TEXT, State TEXT, Pincode TEXT )")
    #        cur = con.cursor()
    #        cur.execute("INSERT INTO company (SellerName, Domain, URL, Email,Password, Contact, Address, Country, State, Pincode) VALUES (?,?,?,?,?,?,?,?,?,?)",(sname,domain,url,email,password,contactnumber,address,country,state,pincode) )
    #        con.commit()
    
            #cur.execute("DELETE FROM company")
            #cur.execute("DELETE FROM company where SellerName = 'None'")
    #        return render_template("register.html",msg="Thank You For Registering with us. You will receive a confirmation Email within 48 Hours.")
            
    #    else:
    #        return render_template("register.html",msg="THE ACCOUNT ALREADY EXISTS!!")

#Login verification for the seller     
@app.route("/seller_login", methods=['POST','GET'])

def seller_login():
             
        sname = str(request.form.get("sname"))
        email=str(request.form.get("email"))
        password= str(request.form.get("password"))
        con = sql.connect("database.db")
        cur = con.execute("select SellerName,email,password from company where SellerName = (?)",(sname,))
        row = cur.fetchall()
        for row in row:    
            if (sname == row[0]) and (email == row[1]) and (password == row[2]):    
                return render_template("seller.html")      
            else:
                return render_template("login.html",msg="The Below Entered Information is Incorrect!")
                
#To access the company details database in the tabular form        
@app.route("/company_database") 
def company_database():
    
    con = sql.connect("database.db")  
    con.row_factory = sql.Row  
    cur = con.cursor()  
    cur.execute("select * from companydetails")  
    rows = cur.fetchall() 
    return render_template("company_database.html",rows=rows)

#to access the product details database in the tabular form 
@app.route("/seller_database") 
def seller_database():
    
    con = sql.connect("database.db")  
    con.row_factory = sql.Row  
    cur = con.cursor()  
    cur.execute("select * from data")  
    rows = cur.fetchall() 
    return render_template("seller_database.html",rows=rows)
    
#gather product details from the form 
@app.route("/registered", methods=['POST','GET'])
def registered():
    sname=str(request.form.get("sname"))
    pname=str(request.form.get("pname"))
    mdate=(request.form.get("mdate"))
    timestamp = str(datetime.datetime.now())
    hname = str(sname+pname)
    hash = hashlib.sha256(hname.encode())
    hashvalue=(hash.hexdigest())
    with sql.connect("database.db") as con:
            
            cur = con.cursor()
            #cur.execute("CREATE TABLE data (SellerName TEXT , ProductName TEXT , ManufactureDate TEXT, Hashvalue TEXT UNIQUE, TimeStamp TEXT)")
            cur.execute("INSERT INTO data (SellerName, ProductName, ManufactureDate, HashValue,TimeStamp) VALUES (?,?,?,?,?)",(sname,pname,mdate,hashvalue,timestamp) )
            #cur.execute("DELETE FROM data")
            cur.execute("DELETE FROM data where SellerName = 'None'")    
            con.commit()
    return render_template("registered.html")
hash_value = []
name=[]  

#generating the qr code
@app.route("/generateqr")
def generateqr():
    con = sql.connect("database.db")
    cur = con.execute("select HashValue, ProductName from data")    
    row = cur.fetchall()
    for row in row:
        hash_value.append(row[0])
        name.append(row[1])

    img = qrcode.make(hash_value[-1])
    qr_name = "qr_" +name[-1] + ".png"
    img.save(qr_name)
    im = Image.open(qr_name)
    data = io.BytesIO()
    im.save(data,"JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())
    
    return render_template("generateqr.html",img_data = encoded_img_data.decode('utf-8'))

#customer page 
@app.route("/customer")
def customer():
    return render_template("customer.html")

#to get the data from the qr code 
@app.route("/uploaded",methods=['POST','GET'])
def qrdecode():
    
    f = request.files['file']
    #f.save(f.filename)
    img = cv2.imread(f.filename)
    detector= cv2.QRCodeDetector()
    while True:
        try:
                
            data, vertices_array, _ = detector.detectAndDecode(img)
            if vertices_array is not None:
                if data:
            
            #data,bbox, straight_qrcode = detector.detectAndDecode(img)
                    con = sql.connect("database.db")
                    con.row_factory = sql.Row  
                    cur = con.cursor()  
                    cur.execute("select SellerName, ProductName, ManufactureDate, HashValue,TimeStamp from data where HashValue = (?)",(data,))
                    rows = cur.fetchall()
                    return render_template("uploaded.html",rows=rows)
        except Exception as e: 
            return render_template("uploaded.html",msg="No Data Found")

#initializing the webcam to scan the QR Code 
@app.route("/webcam",methods=['POST','GET'])
def webcam():
    # initalize the camera
    cap = cv2.VideoCapture(0)
    # initialize the OpenCV QRCode detector
    detector = cv2.QRCodeDetector()

    while True:
        try:
            _, img = cap.read()
        # detect and decode
            data, vertices_array, _ = detector.detectAndDecode(img)
            # check if there is a QRCode in the image
            if vertices_array is not None:
                if data:
                    con = sql.connect("database.db")
                    con.row_factory = sql.Row  
                    cur = con.cursor()  
                    cur.execute("select SellerName, ProductName, ManufactureDate, HashValue,TimeStamp from data where HashValue = (?)",(data,))
                    rows = cur.fetchall()    
                    return render_template("webcam.html",rows=rows)
                
        except Exception as e: 
            return render_template("webcam.html")
                #else: 
                    #    return render_template("uploaded.html",msg="No Data Found")
    #Enter q to Quit
        if cv2.waitKey(1) == ord("q"):
           break
    cap.release()
    cv2.destroyAllWindows()

#Example of API DATABASE 
@app.route("/api_database")
def api_database():
    con = sql.connect("database.db")
    cur = con.cursor()
    #cur.execute("CREATE TABLE API_DATABASE(cin TEXT, companyname TEXT, email TEXT, address TEXT)")
    #cur.execute("INSERT INTO API_DATABASE (cin,companyname,email,address) VALUES(?,?,?,?)",("L17110MH1973PLC019786","RELIANCE INDUSTRIES LIMITED","savithri.parekh@ril.com","3 RD FLOORMAKER CHAMBER IV 222 NARIMAN POINT MUMBAI MH 400021 IN"))
    #cur.execute("INSERT INTO API_DATABASE (cin,companyname,email,address) VALUES(?,?,?,?)",("U01100DL1994PLC063704","AMAZON INDIA LIMITED","secretarialdeptt@yahoo.com","PARSVNATH TOWER NEAR SHAHDARA METRO STATION, SHAHDARA DELHI East Delhi DL 110032 IN"))

    #cur.execute("DELETE FROM API_DATABASE")
    con.commit()
    con.row_factory = sql.Row  
    cur = con.cursor()  
    cur.execute("select * from API_DATABASE")  
    rows = cur.fetchall() 
    
    return render_template("api_database.html",rows=rows)
    
if __name__ == '__main__':
    app.run(debug=True, port=8000)