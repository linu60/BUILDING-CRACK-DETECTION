from flask import Flask, render_template, flash, request, session
import mysql.connector

app = Flask(__name__)
app.config['DEBUG']
app.config['SECRET_KEY'] = 'abc'


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/AdminLogin")
def AdminLogin():
    return render_template('AdminLogin.html')


@app.route("/NewUser")
def NewUser():
    return render_template('Newuser.html')


@app.route("/Newuser", methods=['GET', 'POST'])
def Newuser():
    if request.method == 'POST':
        Name = request.form['name']
        Age = request.form['age']
        Gender = request.form['gender']
        Mobile = request.form['mobile']

        Email = request.form['email']

        Address = request.form['address']

        Username = request.form['username']
        Password = request.form['password']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='buildingcrackdb')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO regtb VALUES ('','" + Name + "','" + Gender + "','" + Age + "' , '" + Email + "','" + Mobile + "','" + Address + "','" + Username + "','" + Password + "')")
        conn.commit()
        conn.close()
        flash(' USER REGISTER SUCCESSFULLY')

    return render_template('Userlogin.html')


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':

            flash("LOGIN SUCCESSFULLY")

            conn = mysql.connector.connect(user='root', password='', host='localhost', database='buildingcrackdb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb ")
            data1 = cur.fetchall()
            return render_template('AdminHome.html', data1=data1)

        else:
            flash("UserName Or Password Incorrect!")
            return render_template('AdminLogin.html')


@app.route("/UserLogin")
def UserLogin():
    return render_template('UserLogin.html')


@app.route("/Adminhome")
def Adminhomee():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='buildingcrackdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM  regtb ")
    data1 = cur.fetchall()

    return render_template('Adminhome.html', data=data1)
@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        name = request.form['uname']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='buildingcrackdb')
        cursor = conn.cursor()
        cursor.execute(
            "insert into regtb values('','" + name + "','" + mobile + "','" + email + "','" + address + "','" + username + "','" + password + "')")
        conn.commit()
        conn.close()
        flash("Record Saved!")
    return render_template('UserLogin.html')
@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['uname'] = request.form['username']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='buildingcrackdb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + username + "' and password='" + password + "'")
        data = cursor.fetchone()
        if data is None:

            flash('Username or Password is wrong')
            return render_template('Userlogin.html')
        else:

            session['mob'] = data[2]
            session['email'] = data[3]

            conn = mysql.connector.connect(user='root', password='', host='localhost', database='buildingcrackdb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb where username='" + username + "' and Password='" + password + "'")
            data1 = cur.fetchall()
            flash("LOGIN SUCCESSFULLY")
            return render_template('Userhome.html', data=data1)


@app.route("/Userhome")
def Userhome():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='buildingcrackdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb where username='" + session['uname'] + "' ")
    data1 = cur.fetchall()
    return render_template('Userhome.html', data=data1)



@app.route("/Predict")
def Predict():
    Camera1()
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='buildingcrackdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb where username='" + session['uname'] + "' ")
    data1 = cur.fetchall()
    return render_template('Userhome.html', data=data1)

def Camera1():
    import cv2
    from ultralytics import YOLO

    # Load the YOLOv8 model
    model = YOLO('runs/detect/crack/weights/best.pt')
    # Open the video file
    # video_path = "path/to/your/video/file.mp4"
    cap = cv2.VideoCapture(0)
    dd1 = 0

    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()
        if success:
            # Run YOLOv8 inference on the frame
            results = model(frame, conf=0.8)
            for result in results:
                if result.boxes:
                    box = result.boxes[0]
                    class_id = int(box.cls)
                    object_name = model.names[class_id]
                    print(object_name)

                    if object_name == 'crack':
                        dd1 += 1

                    if dd1 == 20:
                        dd1 = 0
                        import winsound
                        filename = 'alert.wav'
                        winsound.PlaySound(filename, winsound.SND_FILENAME)

                        annotated_frame = results[0].plot()

                        cv2.imwrite("alert.jpg", annotated_frame)
                        sendmail()
                        sendmsg(session['mob'], "Prediction Name:" + object_name)

            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            # Display the annotated frame
            cv2.imshow("YOLO11 Inference", annotated_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()




def sendmsg(targetno,message):
    import requests
    requests.post(
        "http://sms.creativepoint.in/api/push.json?apikey=6555c521622c1&route=transsms&sender=FSSMSS&mobileno=" + targetno + "&text=Dear customer your msg is " + message + "  Sent By FSMSG FSSMSS")


def sendmail():
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "projectmailm@gmail.com"
    toaddr =  session['email']

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Alert"

    # string to store the body of the mail
    body = "Crack Detection"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = "alert.jpg"
    attachment = open("alert.jpg", "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "qmgn xecl bkqv musr")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()





if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
