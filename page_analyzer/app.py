from dotenv import load_dotenv
import os
import psycopg2
from flask import Flask, render_template, url_for, request, flash, redirect, get_flashed_messages
from modules import normalized_urls
from repository import UrlReposetory
import validators
from datetime import date

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "index.html", 
        urls = '',
        messages=messages
    )

@app.route('/urls')
def urls_get():
    conn = psycopg2.connect(DATABASE_URL)
    repo = UrlReposetory(conn)
    urls = repo.get_content(reversed=True)
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
    if not url:
        flash('URL обязателен', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            urls = url,
            messages=messages
        ), 422
    if len(url) > 255 or not validators.url(url):
        flash('Некорректный URL', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            urls = url,
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
        return redirect(url_for('urls_show', id=url_in_repo['id'])), 302
    
    repo.save(norm_url)
    conn.close()
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('urls_get')), 302

@app.route('/urls/<id>')
def urls_show(id):
    conn = psycopg2.connect(DATABASE_URL)
    repo = UrlReposetory(conn)
    url = repo.find(id)
    conn.close()
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'urls/show.html',
        messages=messages,
        url=url
    )
