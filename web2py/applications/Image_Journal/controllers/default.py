import re
@auth.requires_login()
def index():
    if auth.user == None:
        redirect(URL('user'))
    query=(db.image.id>0)
    con=db(query).count()
    if not session.counter:
        #response.flash='Served!'
        inp=session.counter = 0
    elif (session.counter)*10>con:
        response.flash='Reached the end!'
        inp=session.counter=con/10
    elif session.counter<0:
        response.flash='Reached the begin!'
        inp=session.counter=0
    else:
        #response.flash='Served!'
        inp=session.counter
    image = db().select(db.image.ALL, orderby=~db.image.likes)
    comments = db().select(db.post.ALL)
    return dict(images=image[inp*10:inp*10 + 10],comments=comments)
@auth.requires_login()

def next():
    session.counter+=1
    redirect(URL('index'))
@auth.requires_login()

def prev():
    session.counter-=1
    redirect(URL('index'))
@auth.requires_login()
def upload():
    db.image.user.default=auth.user.id
    form = SQLFORM(db.image, showid=False,fields=['title','file','description'])
    form.vars.email=auth.user.email
    form.vars.likes = 0
    form.vars.author = auth.user.first_name+" "+auth.user.last_name
    form.vars.username = auth.user.username
    form.element('input[name=file]')['_onchange'] = 'readURL(image_file)'
    if form.process().accepted:
        redirect(URL('index'))
    return dict(form=form)
@auth.requires_login()
def show():
    session.image=request.args(0,cast=int)
    image=db.image(request.args(0,cast=int)) or redirect(URL('index'))
    flag = 0
    results = db(db.like.user==auth.user.id )( db.like.like_id == image.id ).select()
    for result in results:
        flag = result.level
    report_id=request.args(0,cast=int)
    form_rep = SQLFORM(db.report)
    db.report.report_id.default=session.image
    db.report.report_by.default = str(auth.user.first_name) +" "+ str(auth.user.last_name)
    db.report.report_against.default = db( db.image.id == session.image ).select().first().user.username
    db.report.user.default = auth.user.id
    if form_rep.process().accepted:
        response.flash = 'thankyou for your response'
    if session.disp==1:
        response.flash = 'You like it!'
    elif session.disp==0:
        response.flash = "Already liked!"
    return dict(image=image, flag=flag, tags = db( db.tag.tag_id == session.image ).select(), comments = db( db.post.post_id == session.image ).select(), user=db(db.auth_user).select(),results=results,form_rep=form_rep)
@auth.requires_login()

def profile():
    profile_id=request.args(0,cast=int)
    #response.flash = 'profile_id'
    #image_upl = db().select(db.image.ALL)
    #image_like = db().select(db.like.ALL)
    #image_tag = db().select(db.tag.ALL)
    #image_report = db().select(db.report.ALL)
    #olo = db( db.image.id == 4 ).select().first()
    #el=solo.file
    image_upl = db( db.image.user == profile_id ).select()
    image_like = db( db.like.user == profile_id ).select()
    image_tag = db( db.tag.user == profile_id ).select()
    image_report = db( db.report.user == profile_id ).select()
    return dict(image_upl=image_upl, image_like=image_like,image_tag=image_tag, image_report=image_report, profile_id=profile_id)
@auth.requires_login()

def report():
    report_id=request.args(0,cast=int)
    form = SQLFORM(db.report)
    db.report.report_id.default=report_id
    db.report.report_by.default = str(auth.user.first_name) +" "+ str(auth.user.last_name)
    db.report.report_against.default = db( db.image.id == report_id ).select().first().user.username
    db.report.user.default = auth.user.id
    if form.process().accepted:
        redirect(URL('index'))
    return dict(form=form)

@auth.requires_login()
def download():
    return response.download(request, db)
def download_sup():
    img=db.image(db.image.id==request.args(0,cast=int)).select()
    imga=img(0)
    redirect(URL('download',args=imga.file))
    return download()
@auth.requires_login()
def my():
    images = db().select(db.image.ALL, orderby=~db.image.likes)
    return dict(images=images)
@auth.requires_login()
def my_show():
    image=db.image(request.args(0,cast=int)) or redirect(URL('index'))
    if auth.user.email != image.email:
        session.counter=0
        redirect(URL('index'))
    return dict(image=image)

@auth.requires_login()
def edit():
    update = db.image(request.args(0,cast=int))
    form = SQLFORM(db.image, update, showid=False,fields=['title','file','description','procedure'])
    if auth.user.email != update.email:
        session.counter=0
        redirect(URL('index'))
    if form.process().accepted:
        redirect(URL('my'))
    return dict(form=form)
@auth.requires_membership('moderator')

def manage():
    grid = SQLFORM.smartgrid(db.image)
    return dict(grid=grid)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

"""
@cache.action()
def download():
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    return response.download(request, db)
"""

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
@auth.requires_login()

def post():
    db.post.user.default=auth.user.id
    db.post.author.default=auth.user.username
    db.post.post_id.default=session.image
    form = SQLFORM(db.post)
    if form.accepts(request, formname=None):
        return DIV("Message posted")
    elif form.errors:
        return TABLE(*[TR(k, v) for k, v in form.errors.items()])

@auth.requires_login()
def post_list():
    return dict(comments = db( db.post.post_id == request.args(0,cast=int) ).select())

@auth.requires_login()
def tag_form():
    db.tag.tag_id.default=session.image
    db.tag.user.default=auth.user.id
    return dict(form=SQLFORM(db.tag).process())

@auth.requires_login()
def tag_list():
    return dict(comments = db( db.tag.tag_id == session.image ).select())

@auth.requires_login()
def tagging():
    db.tag.user.default=auth.user.id
    db.tag.tag_id.default=session.image
    form = SQLFORM(db.tag)
    if form.accepts(request, formname=None):
        rows=db( db.tag.tag_id == session.image & db.tag.person == request.vars.person ).select()
        count=0
        for i in rows:
            count+=1
        if count==2:
            db(db.like.user==auth.user.id)(db.like.like_id==nimage).delete()
            pass

            # delete the last entry
        if count==1:
            pass
            # update the link
        return DIV("Tagged")
    elif form.errors:
        return TABLE(*[TR(k, v) for k, v in form.errors.items()])
    
@auth.requires_login()
def user_selector():
    if not request.vars.comment:
        return ''
    #users = ['January', 'February', 'March', 'April', 'May',
    #'June', 'July', 'August', 'September' ,'October',
    #'November', 'December']
    searchObj = re.search( r'(@.*)', request.vars.comment, re.M|re.I)
    if not searchObj:
        return ''
    users = db(db.auth_user).select()
    user_start = searchObj.group(1)[1:].capitalize()
    selected = [m.username for m in users if m.username.capitalize().startswith(user_start)]
    #selected = [m for m in users if m.startswith(user_start)]
    return DIV(*[DIV(k,
     _onclick="jQuery('#comment').val('%s')" % k,
     _onmouseover="this.style.backgroundColor='yellow'",
     _onmouseout="this.style.backgroundColor='white'"
         ) for k in selected])


@auth.requires_login()
def tag_selector():
    if not request.vars.person: return ''
    #months = ['January', 'February', 'March', 'April', 'May',
#'June', 'July', 'August', 'September' ,'October',
#'November', 'December']
    pattern = request.vars.person.capitalize() + '%'
    selected = [row.username for row in db(db.auth_user.username.like(pattern)).select()]
    return ''.join([DIV(k,
                        _onclick="jQuery('#person').val('%s')" % k,
                        _onmouseover="this.style.backgroundColor='yellow'",
                        _onmouseout="this.style.backgroundColor='white'"
    ).xml() for k in selected])

@auth.requires_login()
def try1():
    session.image=request.args(0,cast=int)
    image=db.image(request.args(0,cast=int)) or redirect(URL('index'))
    flag = 0
    results = db(db.like.user==auth.user.id )( db.like.like_id == image.id ).select()
    for result in results:
        flag = result.level
    if session.disp==1:
        response.flash = 'You like it!'
    elif session.disp==0:
        response.flash = "Already liked!"
    return dict(image=image, flag=flag, tags = db( db.tag.tag_id == session.image ).select(), comments = db( db.post.post_id == session.image ).select(), user=db(db.auth_user).select(),results=results)
@auth.requires_membership('moderator')
def rep():
    reports=db().select(db.report.ALL)
    return dict(reports=reports)
@auth.requires_login()
def delete():
    image = db.image(request.args(0,cast=int))
    return dict(image=image, tags = db( db.tag.tag_id == request.args(0,cast=int) ).select(), comments = db( db.post.post_id == request.args(0,cast=int) ).select())

@auth.requires_login()
def search_result():
    return dict()
@auth.requires_login()
def search_list():
    if request.vars.option !=None and request.vars.query!=None:
        option=request.vars.option.capitalize()
        query=request.vars.query.capitalize()
    else:
        return dict(ans=None)
    #option='Title'
    #query=''
    if option=='Tags':
        pattern = query + '%'
        selected = [row.tag_id for row in db(db.tag.person.like(pattern)).select()]
        return DIV(*[ DIV(A( IMG( _width="400px", _height="200px",_src=URL('download',args=db( db.image.id == k ).select().first().file)), _href=URL('show',args=k)) + DIV("<-->"))for k in selected])
    elif option == 'Uploader':
        pattern = query + '%'
        selected = [row.id for row in db(db.image.created_by.like(pattern) | db.image.author.like(pattern) | db.image.username.like(pattern) ).select()]
        return DIV(*[ DIV(IMG( _width="400px", _height="200px",_src=URL('download',args=db( db.image.id == k ).select().first().file)) + DIV("<-->"))for k in selected])
    elif option == 'Title':
        pattern = query + '%'
        selected = [row.id for row in db(db.image.title.like(pattern)).select()]
        ans=db(db.image.title.like(pattern)).select()
        return DIV(*[ DIV(IMG( _width="400px", _height="200px",_src=URL('download',args=db( db.image.id == k ).select().first().file)) + DIV("<-->"))for k in selected])
    return dict(ans=None)
@auth.requires_login()
def liking():
    levels = request.args(0,cast=int)
    flag = 0
    results = db( db.like.like_id == session.image )(db.like.user==auth.user.id).select()
    for result in results:
        flag = result.level
    images=db(db.image.id==session.image).select()
    for row in images:
        k=row.likes
    if flag!=0:
        db(db.like.user==auth.user.id)(db.like.like_id==session.image).delete()
        k=k-1
        db(db.image.id==session.image).update(likes=k)
    else:
        db.like.insert(user=auth.user.id, like_id=session.image,level=levels)
        k=k+1
        db(db.image.id==session.image).update(likes=k)
    return DIV('Likes:', k)

@auth.requires_login()
def disliking():
    flag = 0
    results = db(db.like.user==auth.user.id)(db.like.like_id==session.image).select()
    for result in results:
        flag = result.level
    rows=db(db.image.id==session.image).select()
    for row in rows:
        k=row.likes
    if flag==0:
        response.flash = ("You cannot unlike this!")
    else:
        db(db.like.user==auth.user.id)(db.like.like_id==session.image).delete()
        k=k-1
        db(db.image.id==session.image).update(likes=k)
    return DIV('Likes:', k)
