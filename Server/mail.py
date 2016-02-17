import smtplib
import myconfig

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header

class Mail:

	def send(self, to, subject, text, photos):

		msg = MIMEMultipart()
		msg['Subject'] = Header(subject, 'utf-8')
		msg['From'] = myconfig.mail
		msg['To'] = to

		msgText = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
		msg.attach(msgText)

		i = 0

		for photo in photos:
			i = i + 1
			#msgText = MIMEText("Captura %d" %(i), 'plain')
			#msg.attach(msgText)
			msgImg = MIMEImage(photo.decode("base64"), name="Img%d.jpg" % (i))
			msg.attach(msgImg)
	

		try:
			server = smtplib.SMTP('smtp.gmail.com:587')
			server.starttls()
			server.login(myconfig.mail,myconfig.passMail)
			server.sendmail(myconfig.mail, to, msg.as_string())
			server.quit()
		
		except smtplib.SMTPException:
			print "Unable send mail"
