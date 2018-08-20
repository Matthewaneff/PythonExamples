from reportlab.pdfgen import canvas

def hello(c):
	c.drawString(100,100, "Hello World")
	return

c = canvas.Canvas("hello.pdf", bottomup=0)

hello(c)

c.showPage()
c.save()
