# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


@auth.requires_login()
def index():
	if not session.counter:
		session.counter = 1
	else:
		session.counter += 1
	record=db().select(db.item.ALL,orderby= ~(db.item.like))
	for i in range(0,len(record)):
		record[i]['like']=(likes(record[i]['heading']))
#return dict(message="Reddit", counter=session.counter,record=record,form=auth())
	message="Reddit"
	counter=session.counter
	return locals()
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
def display_form():
    return dict()
def displaylist():
    record=db().select(db.item.heading,db.item.category,db.item.url)
    return dict(record=record)
@auth.requires_login()
def insert():
	form=SQLFORM(db.item)
	if form.accepts(request.vars):
        	response.flash=T('Item inserted !!')
	return dict(form=form)
@auth.requires_login()
def rate():
	form=SQLFORM(db.like)
	if form.accepts(request.vars):
		response.flash=T('Item Rated !!')
	return dict(form=form)
@auth.requires_login()
def comment():
	import datetime
	form=SQLFORM(db.comment)
	if form.accepts(request.vars):
		response.flash=T('Commented !! ')
	return dict(form=form)
def likes(itemname):
	ctr=100
	record=db(db.like.item==(itemname)).select()
#ctr=len(record)
	for i in range(0,len(record)):
		if record[i]['like']=='Yes':
			ctr += 5
		elif record[i]['like']=='No':
			ctr -= 3
	rec=db(db.item.heading==itemname).update(like=ctr)
        return dict(ctr=ctr)
def viewcomment():
    	itemname=request.args(0)
    	record=db((db.comment.item==itemname) & (db.comment.userid==db.auth_user.id)).select(db.comment.comm,db.auth_user.first_name,db.comment.time)
	return dict(record=record)
@auth.requires_login()
def addcategory():
	record=db(db.auth_user.id==auth.user.id).select(db.auth_user.usertype)
	if record[0]['usertype']=='User':
		return 'Permission Denied.Only Admin has permission to add categories...'
	else:
		form=SQLFORM(db.category)
		if form.accepts(request.vars):
			response.flash=T('Category added !!')
		return dict(form=form)

def category():
	record=db().select(db.category.name)
	return dict(record=record)
def viewcat():
    	record=db(db.item.category==(request.args(0))).select(db.item.heading,db.item.url)
    	return dict(record=record)
@auth.requires_login()
def delete():
	record=db(db.auth_user.id==auth.user.id).select(db.auth_user.usertype)
	if record[0]['usertype']=='User':
		return 'Permission Denied.Only Admin has permission to add categories...'
	else:	
		item=request.vars['delete']
		db(db.item.heading==item).delete()
		redirect(URL(index))

@auth.requires_login()
def update():
	record=db(db.auth_user.id==auth.user.id).select(db.auth_user.usertype)
	if record[0]['usertype']=='User':
		return 'Permission Denied.Only Admin has permission to add categories...'
	else:
#		form=SQLFORM.factory(
#				Field('name','string',requires=IS_IN_DB(db,db.auth_user.first_name))
#	)
		form=crud.update(db.item,request.args(0))
		return dict(form=form)
@auth.requires_login()
def deleteacc():
	if(auth.user.usertype=='Admin'):
		form=SQLFORM.factory(
				Field('name','string',requires=IS_IN_DB(db,db.auth_user.first_name))
				)
		if form.accepts(request.vars):
			rec=db(db.auth_user.first_name==form.vars.name).select(db.auth_user.id)
			db(db.auth_user.first_name==form.vars.name).delete()
			db(db.item.posted_by==rec[0]['id']).delete()
		return dict(form=form)
	else:
		print 'Permission Denied.You are not a Admin'
