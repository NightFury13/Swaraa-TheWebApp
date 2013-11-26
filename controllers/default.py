# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    if auth.user_id>0:
        redirect(URL(r=request,f='homepage'))
    response.flash = T("Welcome to web2py!")
    return dict(message=T('Hello World'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@auth.requires_login()
def recommend():
        x=int(request.vars.id1)
	l=[]
	recommends_made=db((db.recommend.song_id==x)&(db.recommend.recommended_by==auth.user_id)).select(db.recommend.ALL)
	users=db(db.auth_user.id>0).select(db.auth_user.ALL)
	for i in recommends_made:
	    l.append(i['recommended_to'])
	return locals()
def search():
	x=request.vars['keyword']
	result=db(db.song.Title.contains(x) | db.song.raaga.contains(x) | db.song.Composer.contains(x)).select(orderby=~(db.song.Rating))
	return locals()
@auth.requires_login()
def recommend_to():
    x=int(request.vars.id1)
    y=int(request.vars.id2)
    db.recommend.insert(song_id=x,recommended_by=auth.user_id,recommended_to=y)
    response.flash="Succesfully recommended"
    redirect(URL('recommend?id1=%d'%(x)))
    return locals()
@auth.requires_login()
def remove_recommend():
    x=int(request.vars.id1)
    y=int(request.vars.id2)
    myset=db((db.recommend.song_id==x)&(db.recommend.recommended_to==y)&(db.recommend.recommended_by==auth.user_id))
    myset.delete()
    response.flash="Succesfully recommend removed"
    redirect(URL('recommend?id1=%d'%(x)))

@auth.requires_login()
def view_reported():
    comm=db().select(db.report_comment.ALL)
    son=db((db.report_song.song_id==db.song.id)&(db.report_song.user_id==db.auth_user.id)).select(db.song.ALL,db.report_song.ALL,db.auth_user.id,db.auth_user.username)
    return locals()
def view_others_Profile():
    c=int(request.vars.id1)
    r=db(db.auth_user.id==auth.user.id).select(db.auth_user.id,db.auth_user.reputation)
    x = db(db.auth_user.id ==c ).select()
    y = db(x[0]['id'] == db.auth_user.id).select(db.auth_user.first_name)
    a = db((x[0]['id'] == db.playlist.user_id)&(db.playlist.song_id==db.song.id)).select(db.playlist.song_id,db.song.ALL)
    liked = db((x[0]['id'] == db.likes.user_id)&(db.likes.song_id==db.song.id)).select(db.likes.song_id,db.song.ALL)
    disliked = db((x[0]['id'] == db.dislikes.user_id)&(db.dislikes.song_id==db.song.id)).select(db.dislikes.song_id,db.song.ALL)
    recommended = db((x[0]['id'] == db.recommend.recommended_to)&(db.recommend.song_id==db.song.id)&(db.recommend.recommended_by==db.auth_user.id)).select(db.recommend.ALL,db.song.ALL,db.auth_user.ALL)
    b = db(db.song.user_id == x[0]['id']).select()
    return locals()
def add_to_playlist():
    x=int(request.vars.id1)
    db.playlist.insert(song_id=x,user_id=auth.user_id)
    redirect(URL('songpage?id1=%d'%(x)))
def remove_from_playlist():
        x=int(request.vars.id1)
	db(db.playlist.song_id==x,db.playlist.user_id==auth.user_id).delete()
	redirect(URL('songpage?id1=%d'%(x)))
	return locals()
def report_song():
    x=int(request.vars.id1)
    db.report_song.insert(song_id=x,user_id=auth.user_id)
    db(db.song.id==x).update(reported=1)
    n=db(db.song.id==x).select(db.song.user_id)
    reputations=db(db.auth_user.id==n[0]['user_id']).select(db.auth_user.id,db.auth_user.reputation)
    init_rep=reputations[0]['reputation']
    db(db.auth_user.id==n[0]['user_id']).update(reputation=init_rep-40)
    redirect(URL('songpage?id1=%d'%(x)))
    return locals()
def report_song_undo():
    x=int(request.vars.id1)
    db(db.report_song.song_id==x,db.report_song.user_id==auth.user_id).delete()
    db(db.song.id==x).update(reported=0)
    n=db(db.song.id==x).select(db.song.user_id)
    reputations=db(db.auth_user.id==n[0]['user_id']).select(db.auth_user.id,db.auth_user.reputation)
    init_rep=reputations[0]['reputation']
    db(db.auth_user.id==n[0]['user_id']).update(reputation=init_rep+40)
    redirect(URL('songpage?id1=%d'%(x)))
    return locals()
def report_song_undo1():
    x=int(request.vars.id1)
    db(db.report_song.song_id==x,db.report_song.user_id==auth.user_id).delete()
    db(db.song.id==x).update(reported=0)
    n=db(db.song.id==x).select(db.song.user_id)
    reputations=db(db.auth_user.id==n[0]['user_id']).select(db.auth_user.id,db.auth_user.reputation)
    init_rep=reputations[0]['reputation']
    db(db.auth_user.id==n[0]['user_id']).update(reputation=init_rep+40)
    redirect(URL('view_reported'))
    return locals()
def report_comment():
    y=int(request.vars.id1)
    x=int(request.vars.id2)
    db.report_comment.insert(comment_id=x,user_id=auth.user_id)
    db(db.comments.id==x).update(reported=1)
    n=db(db.comments.id==x).select(db.comments.user_id)
    reputations=db(db.auth_user.id==n[0]['user_id']).select(db.auth_user.id,db.auth_user.reputation)
    init_rep=reputations[0]['reputation']
    db(db.auth_user.id==n[0]['user_id']).update(reputation=init_rep-20)
    redirect(URL('songpage?id1=%d'%(y)))
    return locals()
def report_comment_undo():
    y=int(request.vars.id1)
    x=int(request.vars.id2)
    db(db.report_comment.comment_id==x,db.report_comment.user_id==auth.user_id).delete()
    db(db.comments.id==x).update(reported=0)
    n=db(db.comments.id==x).select(db.comments.user_id)
    reputations=db(db.auth_user.id==n[0]['user_id']).select(db.auth_user.id,db.auth_user.reputation)
    init_rep=reputations[0]['reputation']
    db(db.auth_user.id==n[0]['user_id']).update(reputation=init_rep+20)
    redirect(URL('songpage?id1=%d'%(y)))
    return locals()

@auth.requires_login()
def songpage():
    x1=request.vars.id1
    get = db(db.song.id == x1).select(db.song.ALL)
    db(db.song.id == x1).update(Num_views = get[0]['Num_views'] + 1)
    get1 = db((db.song.id == x1) & (db.song.user_id == auth.user.id)).select()
    stat1 = 0
    status = 0
    if(len(get1) != 0):
        stat1 = 1
    if(auth.user.Account_type == 'Admin'):
        status = 1
    elif(auth.user.Account_type == 'Superuser'):
        status = 2
    else:
        status = 3
    yy=request.vars.id1
    if yy is None:
		print "YY IS NONE"
    song=db(db.song.id==int(yy)).select(db.song.ALL)
    #song=db(db.song.Title.contains(x)).select()
    if song:
        pass
    else:
        song=None
        #print 'no
        return locals()
    x=song[0]['id']
    likesongid=request.post_vars.songid
    dislikesongid=request.post_vars.dsongid
    rate1=request.post_vars.r1
    rate2=request.post_vars.r2
    rate3=request.post_vars.r3
    rate4=request.post_vars.r4
    rate5=request.post_vars.r5
    likes=song[0]['Num_likes']
    dislikes=song[0]['Num_dislikes']
    if likesongid is not None and int(likesongid)==song[0]['id']:
            flag=0
            lk=db(db.likes.song_id==song[0]['id']).select(db.likes.ALL)
            dlk=db(db.dislikes.song_id==song[0]['id']).select(db.dislikes.ALL)
            for j in range(len(lk)):
                if lk[j]['song_id']==song[0]['id'] and lk[j]['user_id']==auth.user_id:
                    flag=1
                    likes-=1
                    db(db.likes.id==lk[j]['id']).delete()
                    db(db.song.id==song[0]['id']).update(song_rank=100+(2*likes)-dislikes)
                    x=db(db.song.id==song[0]['id']).select(db.song.song_rank)
                    db(db.song.id==song[0]['id']).update(Num_likes=likes,Num_dislikes=dislikes)
            for j in range(len(dlk)):
                if dlk[j]['song_id']==song[0]['id'] and dlk[j]['user_id']==auth.user_id:
                    flag=1
                    dislikes-=1
                    likes+=1
                    db.likes.insert(song_id=song[0]['id'],user_id=auth.user_id)
                    db(db.dislikes.id==dlk[j]['id']).delete()
                    db(db.song.id==song[0]['id']).update(song_rank=100+(2*likes)-dislikes)
                    db(db.song.id==song[0]['id']).update(Num_likes=likes,Num_dislikes=dislikes)
            if flag==0:
                db.likes.insert(song_id=song[0]['id'],user_id=auth.user_id)
                likes+=1
                db(db.song.id==song[0]['id']).update(song_rank=100+(2*likes)-dislikes)
                db(db.song.id==song[0]['id']).update(Num_likes=likes,Num_dislikes=dislikes)
    if dislikesongid is not None:
            if int(dislikesongid)==song[0]['id']:
                flag=0
                lk=db(db.likes.song_id==song[0]['id']).select(db.likes.ALL)
                dlk=db(db.dislikes.song_id==song[0]['id']).select(db.dislikes.ALL)
                flag=0
                for j in range(len(dlk)):
                    if dlk[j]['song_id']==song[0]['id'] and dlk[j]['user_id']==auth.user_id:
                        flag=1
                        dislikes-=1
                        db(db.dislikes.id==dlk[j]['id']).delete()
                        db(db.song.id==song[0]['id']).update(song_rank=100+(2*likes)-dislikes)
                        db(db.song.id==song[0]['id']).update(Num_likes=likes,Num_dislikes=dislikes)
                for j in range(len(lk)):
                    if lk[j]['song_id']==song[0]['id'] and lk[j]['user_id']==auth.user_id:
                        flag=1
                        dislikes+=1
                        likes-=1
                        db(db.likes.id==lk[j]['id']).delete()
                        db.dislikes.insert(user_id=auth.user_id,song_id=song[0]['id'])
                        db(db.song.id==song[0]['id']).update(song_rank=100+(2*likes)-dislikes)
                        db(db.song.id==song[0]['id']).update(Num_likes=likes,Num_dislikes=dislikes)
                     #redirect(URL(r=request,f='songpage'))
                if flag==0:
                    dislikes+=1
                    db.dislikes.insert(user_id=auth.user_id,song_id=song[0]['id'])
                    db(db.song.id==song[0]['id']).update(song_rank=100+(2*likes)-dislikes)
                    db(db.song.id==song[0]['id']).update(Num_likes=likes,Num_dislikes=dislikes)
                 #redirect(URL(r=request,f='songpage'))
    lk=db().select(db.likes.ALL)
    dlk=db().select(db.dislikes.ALL)
    likeform=0
    dislikeform=0
    for k in range(len(lk)):
        if lk[k]['user_id']==auth.user_id and lk[k]['song_id']==song[0]['id']:
            likeform=1
        else:
            likeform=0
    for k in range(len(dlk)):
        if dlk[k]['user_id']==auth.user_id and dlk[k]['song_id']==song[0]['id']:
            dislikeform=1
        else:
            dislikeform=0
    if rate1 is not None and int(rate1)==song[0]['id']:
        rate=db().select(db.rated.ALL)
        flag=0
        for j in range(len(rate)):
            if rate[j]['song_id']==song[0]['id'] and rate[j]['user_id']==auth.user_id:
                flag=1
      	        db(db.rated.id==rate[j]['id']).update(Rating=1)
        if flag==0:
            db.rated.insert(song_id=song[0]['id'],user_id=auth.user_id,Rating=1)
        #redirect(URL(r=request,f='homepage'))
    if rate2 is not None and int(rate2)==song[0]['id']:
        rate=db().select(db.rated.ALL)
        flag=0
        for j in range(len(rate)):
            if rate[j]['song_id']==song[0]['id'] and rate[j]['user_id']==auth.user_id:
                flag=1
                db(db.rated.id==rate[j]['id']).update(Rating=2)
        if flag==0:
            db.rated.insert(song_id=song[0]['id'],user_id=auth.user_id,Rating=2)
        #    redirect(URL(r=request,f='homepage'))
    if rate3 is not None and int(rate3)==song[0]['id']:
        rate=db().select(db.rated.ALL)
        flag=0
        for j in range(len(rate)):
            #flag=1
            if rate[j]['song_id']==song[0]['id'] and rate[j]['user_id']==auth.user_id:
                flag=1
                db(db.rated.id==rate[j]['id']).update(Rating=3)
        if flag==0:
            db.rated.insert(song_id=song[0]['id'],user_id=auth.user_id,Rating=3)
    #        redirect(URL(r=request,f='homepage'))
    if rate4 is not None and int(rate4)==song[0]['id']:
        rate=db().select(db.rated.ALL)
        flag=0
        for j in range(len(rate)):
            #flag=1
            if rate[j]['song_id']==song[0]['id'] and rate[j]['user_id']==auth.user_id:
                flag=1
                db(db.rated.id==rate[j]['id']).update(Rating=4)
        if flag==0:
            db.rated.insert(song_id=song[0]['id'],user_id=auth.user_id,Rating=4)
    #        redirect(URL(r=request,f='homepage'))
    if rate5 is not None and int(rate5)==song[0]['id']:
        rate=db().select(db.rated.ALL)
        flag=0
        for j in range(len(rate)):
            #flag=1
            if rate[j]['song_id']==song[0]['id'] and rate[j]['user_id']==auth.user_id:
                flag=1
                db(db.rated.id==rate[j]['id']).update(Rating=5)
        if flag==0:
            db.rated.insert(song_id=song[0]['id'],user_id=auth.user_id,Rating=5)
#            redirect(URL(r=request,f='homepage'))
    #print likeform
    #print dislikeform
    check=db((db.rated.user_id==auth.user_id) & (db.rated.song_id==song[0]['id'])).select(db.rated.ALL)
    #ctr=rate()
    rate=db(db.rated.song_id==song[0]['id']).select(db.rated.user_id,db.rated.song_id,db.rated.Rating)
    ctr=0
    users=[]
    for i in rate:
        if i['user_id'] not in users:
            users.append(i['user_id'])
            last=db(db.rated.user_id==i['user_id']).select(db.rated.Rating)
            l=len(last)
            rt=last[l-1]['Rating']
            ctr+=rt
        else:
            continue
    ctr=ctr*1.0
    if len(users)==0:
        ctr=0
    else:
        ctr=(ctr/len(users))
    db(db.song.id==song[0]['id']).update(Rating=ctr)
    comments=db(db.comments.song_id==song[0]['id']).select(db.comments.ALL)
    userpic=[]
    for i in comments:
        x=db(db.auth_user.id==i['user_id']).select(db.auth_user.profile_pic)
        userpic.append(x[0]['profile_pic'])
	COMMENT_USERS=[]
    stat=[]
    for i in comments:
        uname=db(db.auth_user.id==i['user_id']).select(db.auth_user.username)
        COMMENT_USERS.append(uname[0])
        if(i['user_id'] == auth.user.id):
            stat.append(1)
        else:
            stat.append(0)
    commform=SQLFORM.factory(db.Field("cmt","text",label="Add comment:",required=True),
                                        submit_button="Comment")
    if commform.process(formname="commform").accepted:
        db.comments.insert(song_id=song[0]['id'],user_id=auth.user_id,comment_text=commform.vars.cmt,comment_time=request.now)
        redirect(URL(r=request,f='songpage?id1=%d'%int(yy)))
    flag=0
    rate1var=0
    rate2var=0
    rate3var=0
    rate4var=0
    rate5var=0
    flag=0
    for i in rate:
        if i['song_id']==song[0]['id'] and i['user_id']==auth.user_id:
            flag=1
            if i['Rating']>=1:
                rate1var=1
            if i['Rating']>=2:
                rate2var=1
            if i['Rating']>=3:
                rate3var=1
            if i['Rating']>=4:
                rate4var=1
            if i['Rating']==5:
                rate5var=1
    #rateform=crud.create(db.rated)
    song=db(db.song.id==song[0]['id']).select(db.song.ALL)
    in_playlist=len(db((db.playlist.user_id==auth.user_id)&(db.playlist.song_id==yy)).select())
    already_reported=len(db((db.report_song.user_id==auth.user_id)&(db.report_song.song_id==yy)).select())
#    redirect(URL('songpage?id1=%d'%(yy)))
    return locals()

@auth.requires_login()
def rate():
	rate=db(db.rated.song_id==int(request.args(1))).select(db.rated.user_id,db.rated.song_id,db.rated.Rating)
	ctr=0
	users=[]
	for i in rate:
		if i['user_id'] not in users:
			users.append(i['user_id'])
			last=db(db.rated.user_id==i['user_id']).select(db.rated.Rating)
			l=len(last)
			rt=last[l-1]['Rating']
			ctr += rt
		else:
			continue
	ctr=ctr*1.0
	if len(users)==0:
	    ctr=0
	else:
	    ctr=(ctr/len(users))
	db(db.song.id==int(request.args(1))).update(Rating=ctr)
	return ctr
	 
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


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

@auth.requires_login()
def viewProfile():
	r=db(db.auth_user.id==auth.user.id).select(db.auth_user.id,db.auth_user.reputation)
     	x = db(db.auth_user.id == auth.user.id).select()
        liked = db((x[0]['id'] == db.likes.user_id)&(db.likes.song_id==db.song.id)).select(db.likes.song_id,db.song.ALL)
        disliked = db((x[0]['id'] == db.dislikes.user_id)&(db.dislikes.song_id==db.song.id)).select(db.dislikes.song_id,db.song.ALL)
        recommended = db((x[0]['id'] == db.recommend.recommended_to)&(db.recommend.song_id==db.song.id)&(db.recommend.recommended_by==db.auth_user.id)).select(db.recommend.ALL,db.song.ALL,db.auth_user.ALL)
	y = db(x[0]['id'] == db.auth_user.id).select(db.auth_user.first_name)
	a = db((x[0]['id'] == db.playlist.user_id)&(db.playlist.song_id==db.song.id)).select(db.playlist.song_id,db.song.ALL)
	b = db(db.song.user_id == x[0]['id']).select()
	return locals()

def homepage():
    var1=request.post_vars.button1
    var2=request.post_vars.button2
    var3=request.post_vars.button3
    var4=request.post_vars.button4
    a=auth.user_id
    fn=auth.user.first_name
    ln=auth.user.last_name
    likeform=[]
    dislikeform=[]
    commentform=[]
    rate1=[]
    rate2=[]
    rate3=[]
    rate4=[]
    rate5=[]
    likes=[]
    dislikes=[]
    if var1 is not None:
        option=1
        n=db().select(db.song.ALL,orderby=~db.song.post_time)
    elif var2 is not None:
        option=2
        n=db().select(db.song.ALL,orderby=~db.song.Rating)
    elif var3 is not None:
        option=3
        n=db((db.rated.user_id==auth.user_id) & (db.rated.song_id==db.song.id)).select(db.song.ALL,orderby=~db.rated.Rating)
    elif var4 is not None:
        option=4
        n=db().select(db.song.ALL,orderby=~db.song.Num_views)
    else:
        option=1
        n=db().select(db.song.ALL,orderby=~db.song.post_time)
    usernames=[]
    likesongid=request.post_vars.songid
    dislikesongid=request.post_vars.dsongid
    for i in range(len(n)):
        abc=db(db.auth_user.id==n[i]['user_id']).select(db.auth_user.username)
        usernames.append(abc[0]['username'])
        L=db(db.likes.song_id==n[i]['id']).select(db.likes.user_id)
        D=db(db.dislikes.song_id==n[i]['id']).select(db.dislikes.user_id)
        likes.append(n[i]['Num_likes'])
        dislikes.append(n[i]['Num_dislikes'])
        #likeform.append(SQLFORM.factory(submit_button="Like"))
        #dislikeform.append(SQLFORM.factory(submit_button="Dislike"))
        rate1.append(SQLFORM.factory(submit_button="1"))
        rate2.append(SQLFORM.factory(submit_button="2"))
        rate3.append(SQLFORM.factory(submit_button="3"))
        rate4.append(SQLFORM.factory(submit_button="4"))
        rate5.append(SQLFORM.factory(submit_button="5"))
        commentform.append(SQLFORM.factory(db.Field("cmt","string",label="Add comment:",required=True),
                                        submit_button="Comment"))
        flag=0
       # print '\n\n********' + request.post_vars.n[i]['id'] + '**************\n\n'
        if likesongid is not None and int(likesongid)==n[i]['id']:
            lk=db(db.likes.song_id==n[i]['id']).select(db.likes.ALL)
            dlk=db(db.dislikes.song_id==n[i]['id']).select(db.dislikes.ALL)
            for j in range(len(lk)):
                if lk[j]['song_id']==n[i]['id'] and lk[j]['user_id']==a:
                    flag=1
                    likes[i]-=1
                    db(db.likes.id==lk[j]['id']).delete()
                    db(db.song.id==n[i]['id']).update(song_rank=100+(2*likes[i])-dislikes[i])
		    reputations=db(db.auth_user.id==n[i]['user_id']).select(db.auth_user.id,db.auth_user.reputation)
		    init_rep=reputations[0]['reputation']
		    db(db.auth_user.id==n[i]['user_id']).update(reputation=init_rep-20)
                    x=db(db.song.id==n[i]['id']).select(db.song.song_rank)
                    db(db.song.id==n[i]['id']).update(Num_likes=likes[i],Num_dislikes=dislikes[i])
                    
            for j in range(len(dlk)):
                if dlk[j]['song_id']==n[i]['id'] and dlk[j]['user_id']==a:
                    flag=1
                    dislikes[i]-=1
                    likes[i]+=1
                    db.likes.insert(song_id=n[i]['id'],user_id=a)
                    db(db.dislikes.id==dlk[j]['id']).delete()
                    db(db.song.id==n[i]['id']).update(song_rank=100+(2*likes[i])-dislikes[i])
		    reputations=db(db.auth_user.id==n[i]['user_id']).select(db.auth_user.id,db.auth_user.reputation)
		    init_rep=reputations[0]['reputation']
		    db(db.auth_user.id==n[i]['user_id']).update(reputation=init_rep+30)
		    #db(db.auth_user.id==n[i]['user_id']).update(reputation=300)
                    db(db.song.id==n[i]['id']).update(Num_likes=likes[i],Num_dislikes=dislikes[i])
            if flag==0:
                db.likes.insert(song_id=n[i]['id'],user_id=a)
                likes[i]+=1
		reputations=db(db.auth_user.id==n[i]['user_id']).select(db.auth_user.id,db.auth_user.reputation)
		init_rep=reputations[0]['reputation']
		db(db.auth_user.id==n[i]['user_id']).update(reputation=init_rep+20)
                db(db.song.id==n[i]['id']).update(song_rank=100+(2*likes[i])-dislikes[i])
                db(db.song.id==n[i]['id']).update(Num_likes=likes[i],Num_dislikes=dislikes[i])
        if dislikesongid is not None and int(dislikesongid)==n[i]['id']:
             lk=db(db.likes.song_id==n[i]['id']).select(db.likes.ALL)
             dlk=db(db.dislikes.song_id==n[i]['id']).select(db.dislikes.ALL)
             flag=0
             for j in range(len(dlk)):
                 if dlk[j]['song_id']==n[i]['id'] and dlk[j]['user_id']==a:
                     flag=1
                     dislikes[i]-=1
                     db(db.dislikes.id==dlk[j]['id']).delete()
                     db(db.song.id==n[i]['id']).update(song_rank=100+(2*likes[i])-dislikes[i])
                     db(db.song.id==n[i]['id']).update(Num_likes=likes[i],Num_dislikes=dislikes[i])
		     reputations=db(db.auth_user.id==n[i]['user_id']).select(db.auth_user.id,db.auth_user.reputation)
		     init_rep=reputations[0]['reputation']
		     db(db.auth_user.id==n[i]['user_id']).update(reputation=init_rep+10)
                     redirect(URL(r=request,f='homepage'))
             for j in range(len(lk)):
                 if lk[j]['song_id']==n[i]['id'] and lk[j]['user_id']==a:
                     flag=1
                     dislikes[i]+=1
                     likes[i]-=1
                     db(db.likes.id==lk[j]['id']).delete()
                     db.dislikes.insert(user_id=a,song_id=n[i]['id'])
                     db(db.song.id==n[i]['id']).update(song_rank=100+(2*likes[i])-dislikes[i])
                     db(db.song.id==n[i]['id']).update(Num_likes=likes[i],Num_dislikes=dislikes[i])
		     reputations=db(db.auth_user.id==n[i]['user_id']).select(db.auth_user.id,db.auth_user.reputation)
		     init_rep=reputations[0]['reputation']
		     db(db.auth_user.id==n[i]['user_id']).update(reputation=init_rep-30)
                     redirect(URL(r=request,f='homepage'))
             if flag==0:
                 dislikes[i]+=1
                 db.dislikes.insert(user_id=a,song_id=n[i]['id'])
                 db(db.song.id==n[i]['id']).update(song_rank=100+(2*likes[i])-dislikes[i])
		 reputations=db(db.auth_user.id==n[i]['user_id']).select(db.auth_user.id,db.auth_user.reputation)
		 init_rep=reputations[0]['reputation']
		 db(db.auth_user.id==n[i]['user_id']).update(reputation=init_rep-10)
                 db(db.song.id==n[i]['id']).update(Num_likes=likes[i],Num_dislikes=dislikes[i])
                 redirect(URL(r=request,f='homepage'))
        if(commentform[i].process(formname='commentform[%d]'%i).accepted):
              db.comment.insert(user_id=a,song_id=n[i]['id'],comment_text=commentform.vars.cmt)
              redirect(URL(r=request,f='homepage'))
        if(rate1[i].process(formname='rate1[%d]'%i).accepted):
            rate=db().select(db.rated.ALL)
            flag=0
            for j in range(len(rate)):
                flag=1
                if rate[j]['song_id']==n[i]['id'] and rate[j]['user_id']==a:
                    db(db.rated.id==rate[j]['id']).update(Rating=1)
            if flag==0:
                db.rated.insert(song_id=n[i]['id'],user_id=a,Rating=1)
            redirect(URL(r=request,f='homepage'))
        if(rate2[i].process(formname='rate2[%d]'%i).accepted):
            rate=db().select(db.rated.ALL)
            flag=0
            for j in range(len(rate)):
                flag=1
                if rate[j]['song_id']==n[i]['id'] and rate[j]['user_id']==a:
                    db(db.rated.id==rate[j]['id']).update(Rating=2)
            if flag==0:
                db.rated.insert(song_id=n[i]['id'],user_id=a,Rating=2)
            redirect(URL(r=request,f='homepage'))
        if(rate3[i].process(formname='rate3[%d]'%i).accepted):
            rate=db().select(db.rated.ALL)
            flag=0
            for j in range(len(rate)):
                flag=1
                if rate[j]['song_id']==n[i]['id'] and rate[j]['user_id']==a:
                    db(db.rated.id==rate[j]['id']).update(Rating=3)
            if flag==0:
                db.rated.insert(song_id=n[i]['id'],user_id=a,Rating=3)
            redirect(URL(r=request,f='homepage'))
        if(rate4[i].process(formname='rate4[%d]'%i).accepted):
            rate=db().select(db.rated.ALL)
            flag=0
            for j in range(len(rate)):
                flag=1
                if rate[j]['song_id']==n[i]['id'] and rate[j]['user_id']==a:
                    db(db.rated.id==rate[j]['id']).update(Rating=4)
            if flag==0:
                db.rated.insert(song_id=n[i]['id'],user_id=a,Rating=4)
            redirect(URL(r=request,f='homepage'))
        if(rate5[i].process(formname='rate5[%d]'%i).accepted):
            rate=db().select(db.rated.ALL)
            flag=0
            for j in range(len(rate)):
                flag=1
                if rate[j]['song_id']==n[i]['id'] and rate[j]['user_id']==a:
                    db(db.rated.id==rate[j]['id']).update(Rating=5)
            if flag==0:
                db.rated.insert(song_id=n[i]['id'],user_id=a,Rating=5)
            redirect(URL(r=request,f='homepage'))
        #embed_mp3=XML('<embed src="%s" autoplay="false" loop="false" />' % n[i]['Audio_File'])
        flag=0
        lk=db().select(db.likes.ALL)
        dlk=db().select(db.dislikes.ALL)
        for k in range(len(lk)):
            if lk[k]['user_id']==auth.user_id and lk[k]['song_id']==n[i]['id']:
                flag=1
        if flag==1:
            likeform.append(1)
        else:
            likeform.append(0)
        flag=0
        for k in range(len(dlk)):
            if dlk[k]['user_id']==auth.user_id and dlk[k]['song_id']==n[i]['id']:
                flag=1
        if flag==1:
            dislikeform.append(1)
        else:
            dislikeform.append(0)
        #recordings()
    if option==1:
        n=db().select(db.song.ALL,orderby=~db.song.post_time)
    elif option==2:
        n=db().select(db.song.ALL,orderby=~db.song.Rating)
    elif option==3:
        n=db((db.rated.user_id==auth.user_id) & (db.rated.song_id==db.song.id)).select(db.song.ALL,orderby=~db.rated.Rating)
    elif option==4:
        n=db().select(db.song.ALL,orderby=~db.song.Num_views)
    return locals()

def upload():
	form = SQLFORM(db.song)
	form.vars.user_id = auth.user.id
	if form.process().accepted:
		response.flash="Success!!"
		redirect(URL(r=request,f='index'))
	return locals()
		 
@auth.requires_login()	
def delete_song():
	a = request.vars.id1
	a = int(a)
	if((auth.user.Account_type == 'Admin') or (auth.user.Account_type == 'Superuser')):
		db(db.song.id == a).delete()
		db(db.comments.song_id == a).delete()
		db(db.rated.song_id == a).delete()
		db(db.likes.song_id == a).delete()
		db(db.dislikes.song_id == a).delete()
		db(db.recommend.song_id == a).delete()
		redirect(URL(r=request, f='index'))
	else:
		x = db((db.song.user_id == auth.user.id) & (db.song.id == a)).select()
		if(len(x) == 0):
			redirect(URL(r=request, f='error_delete'))
		else:
			db((db.song.user_id == auth.user.id) & (db.song.id == a)).delete()
			db(db.comments.song_id == a).delete()
			db(db.rated.song_id == a).delete()
			db(db.likes.song_id == a).delete()
			db(db.dislikes.song_id == a).delete()
			db(db.recommend.song_id == a).delete()
			redirect(URL(r=request, f='index'))
	return locals()
def delete_song1():
	a = request.vars.id1
	a = int(a)
	if((auth.user.Account_type == 'Admin') or (auth.user.Account_type == 'Superuser')):
		db(db.song.id == a).delete()
		db(db.comments.song_id == a).delete()
		db(db.rated.song_id == a).delete()
		db(db.likes.song_id == a).delete()
		db(db.dislikes.song_id == a).delete()
		db(db.recommend.song_id == a).delete()
		redirect(URL(r=request, f='view_reported'))
	else:
		x = db((db.song.user_id == auth.user.id) & (db.song.id == a)).select()
		if(len(x) == 0):
			redirect(URL(r=request, f='error_delete'))
		else:
			db((db.song.user_id == auth.user.id) & (db.song.id == a)).delete()
			db(db.comments.song_id == a).delete()
			db(db.rated.song_id == a).delete()
			db(db.likes.song_id == a).delete()
			db(db.dislikes.song_id == a).delete()
			db(db.recommend.song_id == a).delete()
			redirect(URL(r=request, f='view_reported'))
	return locals()

def error_edit():
	return locals()
from gluon.tools import Crud
crud = Crud(db)
@auth.requires_login()	
def edit_song():
	a = int(request.vars.id1)
	x = db(db.song.id == a).select(db.song.user_id)
	form = crud.update(db.song,a)
#	form = SQLFORM.factory(
#		Field('Title', 'string', required=True),
#		Field('raaga','string'),
#		Field('taala','string'),
#		Field('Composer','string'),
#		Field('Genre','string',requires=IS_IN_SET(['Art music','Popular music','Traditional music'])),
#		Field('Description','text'))
#	db(db.song.id == a).update(Title = form.vars.Title)
#	db(db.song.id == a).update(raaga = form.vars.raaga)
#	db(db.song.id == a).update(taala = form.vars.taala)
#	db(db.song.id == a).update(Composer = form.vars.Composer)
#	db(db.song.id == a).update(Genre = form.vars.Genre)
#	db(db.song.id == a).update(Description = form.vars.Description)A
	return locals()		


@auth.requires_login()
def update_comment():
	a = request.vars.id1
	a = int(a)
	x = db((db.comments.song_id == a) & (db.comments.user_id == auth.user.id)).select(db.comments.id)
	form = crud.update(db.comments, x[0]['id'])
	if form.process().accepted:
    		redirect(URL('songpage?id1=%d'%(a)))
	return locals()
