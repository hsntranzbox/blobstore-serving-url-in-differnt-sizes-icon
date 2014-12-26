import os
import webapp2
import logging
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
from google.appengine.api import images
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Fil(ndb.Model):
    fill = ndb.StringProperty(indexed=True)
    blob_inf = ndb.BlobKeyProperty()


class MainHandler(webapp2.RequestHandler):
	def get(self):
		file=Fil().fill
		template_values = {
			'file':Fil.fill,
         }
		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))

class UrlCreateHandler(webapp2.RequestHandler):	
	def get(self):
		upload_url = blobstore.create_upload_url('/upload')
		logging.info (upload_url);
		self.response.write(upload_url)

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
	fil=Fil()
	upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
	blob_info = upload_files[0]
	fil.blob_inf=blob_info.key()
	fil.put()
	self.redirect('/serve/%s'%fil.blob_inf)
	logging.info ('%s'%fil.blob_inf);

class ServeHandler(webapp2.RequestHandler):
  def get(self,resource):
	self.response.out.write("<html><head><script>function goBack() {window.history.back()} </script></head><body>")
	self.response.out.write("<a href='%s'>Origonal Size</a> <br><a href='%s'>Object in 150 Size(for Images)</a><br> <a href='%s'>Object in 80 Size(for Images)</a><br><br><button onclick='goBack()'>Upload Another File</button> " % (images.get_serving_url(resource),
	images.get_serving_url(resource, 150),
	images.get_serving_url(resource, 80)))
	#For showing images directly use the code below
	# self.response.out.write("<b>Origonal Size   :   </b>  <img src='%s' alt='Origonal Size'> <br><b>Object in 150 Size(for Images)   :   </b>  <img src='%s' alt='Object in 150 Size(for Images)'><br> <b>Object in 80 Size(for Images)   :   </b>  <img src='%s' alt='Object in 80 Size(for Images)'><br><button onclick='goBack()'>Upload Another File</button> " % (images.get_serving_url(resource),

	self.response.out.write("</html></body>")

app = webapp2.WSGIApplication([('/', MainHandler),
							   ('/urlcreate', UrlCreateHandler),
                               ('/upload', UploadHandler),
                               ('/serve/([^/]+)?', ServeHandler)
							   ],
                              debug=True)