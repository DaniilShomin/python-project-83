import os
from datetime import date

import psycopg2
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from modules import normalized_urls, not_correct_url
from repository import UrlCheckReposetory, UrlReposetory

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "index.html", 
        urls='',
        messages=messages
    )


@app.route('/urls')
def urls_get():
    conn = psycopg2.connect(DATABASE_URL)
    repo = UrlReposetory(conn)
    check_repo = UrlCheckReposetory(conn)
    urls = repo.get_content(reversed=True)
    for url in urls:
        check_url = check_repo.get_content(url['id'], reversed=True)
        if check_url:
            url['last_check'] = check_url[0]['created_at']
            url['status_code'] = check_url[0]['status_code']
        else:
            url.update({
                'last_check': '',
                'status_code': ''
            })
    conn.close()
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "urls/view.html",
        urls=urls,
        messages=messages
    )


@app.route('/urls', methods=['POST'])
def urls_post():
    url = request.form.get('url', '')
    error = not_correct_url(url)
    if error:
        flash(f'{error}', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            urls=url,
            messages=messages
        ), 422 
    conn = psycopg2.connect(DATABASE_URL)
    repo = UrlReposetory(conn)
    norm_url = {
        'name': normalized_urls(url),
        'created_at': date.today()
    }
    url_in_repo = repo.get_by_name(norm_url['name'])
    if url_in_repo:
        flash('Страница уже существует', 'info')
        conn.close()
        return redirect(url_for('urls_show', id=url_in_repo['id'])), 301
    else:
        repo.save(norm_url)
        flash('Страница успешно добавлена', 'success')
    conn.close()
    return redirect(url_for('urls_show', id=norm_url['id'])), 301


@app.route('/urls/<id>')
def urls_show(id):
    conn = psycopg2.connect(DATABASE_URL)
    repo = UrlReposetory(conn)
    check_repo = UrlCheckReposetory(conn)
    url = repo.find(id)
    checks_url = check_repo.get_content(id, reversed=True)
    conn.close()
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'urls/show.html',
        messages=messages,
        url=url,
        checks_url=checks_url
    )


@app.route('/urls/<id>/checks', methods=['POST'])
def urls_checks(id):
    conn = psycopg2.connect(DATABASE_URL)
    repo = UrlReposetory(conn)
    url = repo.find(id)
    error = False
    try:                
        req = requests.get(url['name'], timeout=2, auth=('user', 'pass'))
        req.raise_for_status()        
    except Exception:
        error = True
        flash('Произошла ошибка при проверке', 'danger')
    if not error:
        soup = BeautifulSoup(req.text, 'html.parser')
        extracted_h1 = soup.h1.string if soup.h1 else ''
        extracted_title = soup.title.string if soup.title else ''
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        extracted_description = meta_tag['content'] if meta_tag else ''
        check_repo = UrlCheckReposetory(conn)
        data = {
            'url_id': id, 
            'status_code': req.status_code, 
            'h1': extracted_h1, 
            'title': extracted_title, 
            'description': extracted_description, 
            'created_at': date.today()
        }
        check_repo.get_add(data)
        flash('Страница успешно проверена', 'success')
    conn.close()
    return redirect(url_for('urls_show', id=id))