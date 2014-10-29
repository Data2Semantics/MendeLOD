from mendelod import app, cache, mendeley, MendeleySession
from flask import Flask, redirect, render_template, request, session

import yaml






@app.route('/')
def home():
    if 'token' in app.config:
        return redirect('/listDocuments')

    auth = mendeley.start_authorization_code_flow()
    session['state'] = auth.state

    return render_template('home.html', login_url=(auth.get_login_url()))

@app.route('/reload')
def config_reload():
    with open('config.yml') as f:
        config = yaml.load(f)
    
    app.config['token'] = config['token']
    
    if 'token' in app.config:
        return redirect('/listDocuments')
    else :
        return redirect('/')

@app.route('/redirect')
def auth_return():
    auth = mendeley.start_authorization_code_flow(state=session['state'])
    mendeley_session = auth.authenticate(request.url)

    # session.clear()
    # session['token'] = mendeley_session.token
    #
    # print session['token']
    token_yaml = yaml.dump({'token': mendeley_session.token})
    
    return render_template('token.html',token=token_yaml)




@app.route('/listDocuments')
@cache.cached(timeout=3600)
def list_documents():
    if 'token' not in app.config:
        return redirect('/')

    mendeley_session = get_session_from_config()

    # name = mendeley_session.profiles.me.display_name
    # groups = mendeley_session.groups
    # for g in groups.list().items:
    #     print g.id, g.name
    group = mendeley_session.groups.get('7fc8fad4-ddf6-3b48-b39c-c05d75ba7135')
    
    docs = group.documents.list(view='all',page_size=500).items
    

    
    # docs = mendeley_session.documents.list(view='all',page_size=100).items

    return render_template('library.html', name=group.name, docs=docs)


@app.route('/document')
def get_document():
    if 'token' not in app.config:
        return redirect('/')

    mendeley_session = get_session_from_config()

    document_id = request.args.get('document_id')
    doc = mendeley_session.documents.get(document_id)

    return render_template('metadata.html', doc=doc)


@app.route('/metadataLookup')
def metadata_lookup():
    if 'token' not in app.config:
        return redirect('/')

    mendeley_session = get_session_from_config()

    doi = request.args.get('doi')
    doc = mendeley_session.catalog.by_identifier(doi=doi)

    return render_template('metadata.html', doc=doc)


@app.route('/download')
def download():
    if 'token' not in app.config:
        return redirect('/')

    mendeley_session = get_session_from_config()

    document_id = request.args.get('document_id')
    doc = mendeley_session.documents.get(document_id)
    doc_file = doc.files.list().items[0]

    return redirect(doc_file.download_url)


# @app.route('/logout')
# def logout():
#     session.pop('token', None)
#     return redirect('/')


def get_session_from_config():
    return MendeleySession(mendeley, app.config['token'])