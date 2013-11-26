# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
auth.settings.extra_fields['auth_user'] = [
			Field('Account_type',requires = IS_IN_SET(['Admin','User','Superuser']),default='User', readable=False, writable=False),
			Field('profile_pic', 'upload', uploadfield = 'picture_file'),
			Field('picture_file', 'blob'),
			Field('user_type', requires = IS_IN_SET(['Listener', 'Musician', 'Ensemble'])),
			Field('reputation', 'integer',default=100,readable=False,writable=False),
			Field('about', 'text')]
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',db.Field('mydb.Field','string'))
##
## db.Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' db.Field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(mydb.Field='value')
## >>> rows=db(db.mytable.mydb.Field=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.mydb.Field
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
db.define_table('category',
	db.Field('category_name','string',required=True)
	)
db.define_table('song',
	db.Field('Title','string',required=True),
	db.Field('user_id',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.first_name'),readable=False,writable=False),
	db.Field('raaga','string'),
	db.Field('taala','string'),
	db.Field('Composer','string'),
	db.Field('Genre','string',requires=IS_IN_SET(['Art music','Popular music','Traditional music'])),
	db.Field('Description','text'),
	db.Field('Audio_File','upload',required=True),
	db.Field('Num_views','integer',default=0,writable=False,readable=False),
	db.Field('Num_likes','integer',default=0,writable=False,readable=False),
	db.Field('Num_dislikes','integer',default=0,writable=False,readable=False),
###
#Making rating the actual float value.
###
	db.Field('Rating','float',default=0,readable=False,writable=False),
	db.Field('song_rank','integer',default=100,writable=False,readable=False),
	db.Field('post_time','datetime',default=request.now,readable=False,writable=False),
	db.Field('reported','integer',requires=IS_IN_SET([0,1]),default=0,readable=False,writable=False),
	format='%(Title)s'
	)

#################
###needs append
#################

#db.define_table('ragaa',
#	db.Field('song_id',db.song,requires=IS_IN_DB(db,'song.id','song.Title')),
#	db.Field('raaga_name','string',required=True)
#	)
db.define_table('report_song',
	db.Field('song_id',db.song,requires=IS_IN_DB(db,'song.id','song.Title'),readable=False,writable=False,default=request.args(1)),
	db.Field('user_id',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.first_name'),readable=False,writable=False,default=auth.user_id)
	)
db.define_table('comments',
	db.Field('song_id',db.song,requires=IS_IN_DB(db,'song.id','song.Title'),readable=False,writable=False,default=request.args(1)),
	db.Field('user_id',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.first_name'),readable=False,writable=False,default=auth.user_id),
	db.Field('comment_text','text',required=True),
	db.Field('reported','integer',requires=IS_IN_SET([0,1]),default=0,readable=False,writable=False),
	db.Field('comment_time','datetime',default=request.now,readable=False,writable=False)
	)
db.define_table('report_comment',
	db.Field('comment_id',db.comments,requires=IS_IN_DB(db,'comments.id','comments.Title'),readable=False,writable=False,default=request.args(1)),
	db.Field('user_id',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.first_name'),readable=False,writable=False,default=auth.user_id)
	)
###############
#giving default values here#
###############

db.define_table('rated',
	db.Field('song_id',db.song,requires=IS_IN_DB(db,'song.id','song.Title'),readable=False,writable=False,default=request.args(1)),
	db.Field('user_id',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.first_name'),readable=False,writable=False,default=auth.user_id),
	db.Field('Rating','integer',requires=IS_IN_SET([0,1,2,3,4,5])),
	)
db.define_table('likes',
	db.Field('song_id',db.song,requires=IS_IN_DB(db,'song.id','song.Title')),
	db.Field('user_id',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.first_name')),
	)
db.define_table('dislikes',
	db.Field('song_id',db.song,requires=IS_IN_DB(db,'song.id','song.Title')),	
	db.Field('user_id',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.first_name')),
	)
db.define_table('recommend',
	db.Field('song_id',db.song,requires=IS_IN_DB(db,'song.id','song.Title')),
	db.Field('recommended_by',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.first_name')),
	db.Field('recommended_to',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.first_name'))
	)
db.define_table('playlist',
	db.Field('song_id',db.song,requires=IS_IN_DB(db,'song.id','song.Title')),
	db.Field('user_id',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.first_name')),
	)

#db.define_table('profile',
#	db.Field('user_id',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.first_name')),
#	db.Field('profile_pic','upload', uploadfield='picture_file'),
#	db.Field('picture_file', 'blob'),
#	db.Field('user_type',requires=IS_IN_SET(['Listener','Musician','Ensemble'])),
#	db.Field('about','text'),
#	db.Field('interests',db.category,requires=IS_IN_DB(db,'category.id','category.category_name'))
#	)
